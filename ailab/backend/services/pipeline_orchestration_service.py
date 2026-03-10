from __future__ import annotations

import json
from datetime import datetime

from sqlmodel import Session, select
from backend.agents.report_agent import ReportAgent
from backend.ingestion.semantic_deduper import SemanticDeduplicationEngine
from backend.models.document_model import Document
from backend.models.idea_model import Idea, IdeaScoreRecord, Report
from backend.models.job_model import Job
from backend.models.model_registry_model import ModelRegistryEntry
from backend.models.run_model import PipelineRun
from backend.models.source_model import Source
from backend.jobs.job_repository import JobRepository
from backend.pipelines.idea_pipeline import IdeaPipeline
from backend.search.retriever import VectorSearchService
from backend.settings import settings
from backend.utils.slug_generator import slugify


class PipelineOrchestrationService:
    def __init__(self) -> None:
        self.pipeline = IdeaPipeline()
        self.report_agent = ReportAgent()
        self.deduper = SemanticDeduplicationEngine()
        self.vector_search = VectorSearchService()
        self.job_repository = JobRepository()

    def _now(self) -> str:
        return datetime.utcnow().isoformat()

    def _resolve_model(self, session: Session, task_key: str) -> ModelRegistryEntry | None:
        return session.exec(
            select(ModelRegistryEntry)
            .where(ModelRegistryEntry.task_key == task_key)
            .where(ModelRegistryEntry.enabled == True)  # noqa: E712
            .order_by(ModelRegistryEntry.is_default.desc(), ModelRegistryEntry.id.desc())
        ).first()

    def _create_pipeline_run(
        self,
        session: Session,
        *,
        run_type: str,
        trigger_type: str,
        job_id: int | None,
        model_task_key: str | None = None,
        input_summary: dict | None = None,
    ) -> PipelineRun:
        model = self._resolve_model(session, model_task_key) if model_task_key else None
        run = PipelineRun(
            run_type=run_type,
            status="running",
            trigger_type=trigger_type,
            job_id=job_id,
            model_registry_entry_id=model.id if model else None,
            prompt_version_id=None,
            input_summary_json=json.dumps(input_summary or {}, ensure_ascii=False),
            output_summary_json=None,
            error_message=None,
            started_at=self._now(),
            finished_at=None,
            created_at=self._now(),
        )
        session.add(run)
        session.flush()
        return run

    def _ensure_source(self, session: Session, source_name: str, now: str) -> Source:
        source_key = slugify(source_name) or "generated-source"
        source = session.exec(select(Source).where(Source.source_key == source_key)).first()
        if source:
            return source

        source = Source(
            source_key=source_key,
            display_name=source_name,
            source_type="discussion",
            base_url=None,
            enabled=True,
            config_json=None,
            created_at=now,
            updated_at=now,
        )
        session.add(source)
        session.flush()
        return source

    def _emit_job_event(
        self,
        session: Session,
        job_id: int | None,
        *,
        event_type: str,
        stage: str,
        stage_label: str,
        message: str,
        status: str = "running",
    ) -> None:
        if not job_id:
            return
        self.job_repository.add_event(
            session,
            job_id,
            event_type,
            status,
            message,
            payload_json=json.dumps({"stage": stage, "stage_label": stage_label}, ensure_ascii=False),
        )
        session.commit()

    def discover_and_persist(
        self,
        session: Session,
        *,
        trigger_type: str,
        job_id: int | None = None,
        requested_by: str | None = None,
    ) -> dict:
        run = self._create_pipeline_run(
            session,
            run_type="discover_ideas",
            trigger_type=trigger_type,
            job_id=job_id,
            model_task_key="idea_generation",
            input_summary={"requested_by": requested_by},
        )
        try:
            generated = self.pipeline.run(
                stage_callback=lambda stage, stage_label, message: self._emit_job_event(
                    session,
                    job_id,
                    event_type=f"pipeline_{stage}",
                    stage=stage,
                    stage_label=stage_label,
                    message=message,
                )
            )
            existing_ideas = session.exec(select(Idea)).all()
            persisted: list[dict] = []
            now = self._now()

            self._emit_job_event(
                session,
                job_id,
                event_type="pipeline_save_results",
                stage="save_results",
                stage_label="Saving results",
                message="Сохраняем результаты pipeline в базу данных.",
            )

            for item in generated:
                candidate_text = f"{item['title']}\n{item['summary']}"
                if any(
                    self.deduper.is_duplicate(candidate_text, f"{existing.title}\n{existing.summary}")
                    for existing in existing_ideas
                ):
                    continue

                source = self._ensure_source(session, item["source"], now)
                document = Document(
                    source_id=source.id,
                    external_id=f"generated-{slugify(item['title'])}",
                    canonical_url=f"generated://{slugify(item['title'])}",
                    author_name=None,
                    title=item["title"],
                    language_code="ru",
                    published_at=now,
                    ingested_at=now,
                    content_hash=self.deduper.fingerprint(item["problem"]),
                    raw_payload_path=None,
                    normalized_payload_path=None,
                    content_text=item["problem"],
                    content_markdown=item["problem"],
                    metadata_json=None,
                    status="active",
                )
                session.add(document)
                session.flush()

                idea = Idea(
                    cluster_id=None,
                    primary_source_document_id=document.id,
                    title=item["title"],
                    slug=slugify(item["title"]),
                    summary=item["summary"],
                    target_audience=item["audience"],
                    niche_label=item["niche"],
                    source_type="hybrid",
                    generation_run_id=run.id,
                    status="active",
                    created_at=now,
                    updated_at=now,
                )
                session.add(idea)
                session.flush()

                session.add(
                    IdeaScoreRecord(
                        idea_id=idea.id,
                        scoring_run_id=run.id,
                        market_demand_score=item["market_demand"],
                        competition_score=item["competition"],
                        implementation_difficulty_score=item["difficulty_score"],
                        monetization_score=item["monetization_score"],
                        confidence_score=0.8,
                        total_score=item["score"],
                        rationale_json=None,
                        created_at=now,
                    )
                )

                report_path = self.report_agent.run(
                    settings.reports_dir,
                    {"title": idea.title, "problem": item["problem"], "summary": item["summary"]},
                )
                session.add(
                    Report(
                        idea_id=idea.id,
                        report_type="markdown",
                        output_path=str(report_path),
                        markdown_checksum=None,
                        generated_by_run_id=run.id,
                        created_at=now,
                    )
                )
                persisted.append({"id": idea.id, "title": idea.title, "summary": idea.summary, "score": item["score"]})
                existing_ideas.append(idea)

            self._emit_job_event(
                session,
                job_id,
                event_type="pipeline_rebuild_vectors",
                stage="save_results",
                stage_label="Saving results",
                message="Обновляем векторный индекс и артефакты поиска.",
            )
            index_result = self.vector_search.rebuild_document_chunk_index(session, pipeline_run=run)
            run.status = "completed"
            run.finished_at = self._now()
            run.output_summary_json = json.dumps(
                {
                    "ideas_created": len(persisted),
                    "vector_index": index_result,
                },
                ensure_ascii=False,
            )
            session.commit()
            return {
                "pipeline_run_id": run.id,
                "ideas_created": len(persisted),
                "ideas": persisted,
                "vector_index": index_result,
            }
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = self._now()
            session.commit()
            raise

    def rebuild_vector_index(
        self,
        session: Session,
        *,
        trigger_type: str,
        job_id: int | None = None,
        requested_by: str | None = None,
    ) -> dict:
        run = self._create_pipeline_run(
            session,
            run_type="refresh_embeddings",
            trigger_type=trigger_type,
            job_id=job_id,
            model_task_key="embeddings",
            input_summary={"requested_by": requested_by},
        )
        try:
            result = self.vector_search.rebuild_document_chunk_index(session, pipeline_run=run)
            run.status = "completed"
            run.finished_at = self._now()
            run.output_summary_json = json.dumps(result, ensure_ascii=False)
            session.commit()
            return {"pipeline_run_id": run.id, **result}
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = self._now()
            session.commit()
            raise

    def execute_job(self, session: Session, job: Job) -> dict:
        payload = json.loads(job.payload_json or "{}")
        if job.job_type == "discover_ideas":
            return self.discover_and_persist(
                session,
                trigger_type="job",
                job_id=job.id,
                requested_by=job.requested_by,
            )
        if job.job_type == "refresh_embeddings":
            return self.rebuild_vector_index(
                session,
                trigger_type="job",
                job_id=job.id,
                requested_by=job.requested_by,
            )
        raise ValueError(f"Unsupported job type: {job.job_type} with payload {payload}")
