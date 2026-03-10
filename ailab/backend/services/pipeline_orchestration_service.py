from __future__ import annotations

import json
from datetime import datetime

from sqlmodel import Session, select

from backend.agents.report_agent import ReportAgent
from backend.ingestion.semantic_deduper import SemanticDeduplicationEngine
from backend.jobs.job_repository import JobRepository
from backend.models.cluster_model import Problem, ProblemCluster, ProblemClusterMembership
from backend.models.document_model import Document
from backend.models.idea_model import Idea, IdeaEvidence, IdeaScoreRecord, Report
from backend.models.job_model import Job
from backend.models.model_registry_model import ModelRegistryEntry
from backend.models.run_model import PipelineRun
from backend.models.source_model import Source
from backend.pipelines.idea_pipeline import IdeaPipeline
from backend.search.retriever import VectorSearchService
from backend.services.opportunity_engine import OpportunityEngine
from backend.settings import settings
from backend.utils.slug_generator import slugify


class PipelineOrchestrationService:
    def __init__(self) -> None:
        self.pipeline = IdeaPipeline()
        self.report_agent = ReportAgent()
        self.deduper = SemanticDeduplicationEngine()
        self.vector_search = VectorSearchService()
        self.job_repository = JobRepository()
        self.opportunity_engine = OpportunityEngine()

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
        metrics: dict | None = None,
    ) -> None:
        if not job_id:
            return
        payload = {"stage": stage, "stage_label": stage_label}
        if metrics:
            payload.update(metrics)
        self.job_repository.add_event(
            session,
            job_id,
            event_type,
            status,
            message,
            payload_json=json.dumps(payload, ensure_ascii=False),
        )
        session.commit()

    def _get_or_create_document(
        self,
        session: Session,
        *,
        source_id: int,
        external_id: str,
        canonical_url: str,
        title: str | None,
        content_text: str,
        now: str,
    ) -> Document:
        existing = session.exec(select(Document).where(Document.canonical_url == canonical_url)).first()
        if existing:
            if title and not existing.title:
                existing.title = title
            return existing

        document = Document(
            source_id=source_id,
            external_id=external_id,
            canonical_url=canonical_url,
            author_name=None,
            title=title,
            language_code="ru",
            published_at=now,
            ingested_at=now,
            content_hash=self.deduper.fingerprint(content_text),
            raw_payload_path=None,
            normalized_payload_path=None,
            content_text=content_text,
            content_markdown=content_text,
            metadata_json=None,
            status="active",
        )
        session.add(document)
        session.flush()
        return document

    def _persist_research_artifacts(self, session: Session, run: PipelineRun, research_output: dict) -> list[dict]:
        now = self._now()
        persisted_clusters: dict[int, dict] = {}

        for cluster in research_output["clusters"]:
            source = self._ensure_source(session, cluster["source"], now)
            canonical_url = cluster.get("url") or f"generated://cluster/{slugify(cluster['problem_statement'])}"
            document = self._get_or_create_document(
                session,
                source_id=source.id,
                external_id=slugify(cluster.get("thread_title") or canonical_url) or f"cluster-{slugify(cluster['problem_statement'])}",
                canonical_url=canonical_url,
                title=cluster.get("thread_title"),
                content_text=cluster.get("quote") or cluster["problem_statement"],
                now=now,
            )

            problem = Problem(
                document_id=document.id,
                extraction_run_id=None,
                normalized_text=cluster["problem_statement"],
                original_text=cluster.get("quote") or cluster["problem_statement"],
                problem_type="user-pain",
                severity_score=0.8,
                evidence_span_json=None,
                language_code="ru",
                status="active",
                created_at=now,
                updated_at=now,
            )
            session.add(problem)
            session.flush()

            cluster_key = slugify(f"{cluster.get('niche', 'general')}-{cluster['problem_statement']}") or cluster["cluster_id"]
            cluster_row = session.exec(select(ProblemCluster).where(ProblemCluster.cluster_key == cluster_key)).first()
            if not cluster_row:
                cluster_row = ProblemCluster(
                    cluster_key=cluster_key,
                    title=cluster.get("cluster_title") or cluster["problem_statement"][:80],
                    summary=cluster.get("cluster_summary") or cluster["problem_statement"],
                    niche_label=cluster.get("niche"),
                    centroid_vector_key=None,
                    status="active",
                    created_by_run_id=run.id,
                    created_at=now,
                    updated_at=now,
                )
                session.add(cluster_row)
                session.flush()
            else:
                cluster_row.summary = cluster.get("cluster_summary") or cluster_row.summary
                cluster_row.niche_label = cluster.get("niche") or cluster_row.niche_label
                cluster_row.updated_at = now

            membership = session.exec(
                select(ProblemClusterMembership)
                .where(ProblemClusterMembership.cluster_id == cluster_row.id)
                .where(ProblemClusterMembership.problem_id == problem.id)
            ).first()
            if not membership:
                session.add(
                    ProblemClusterMembership(
                        cluster_id=cluster_row.id,
                        problem_id=problem.id,
                        membership_score=1.0,
                        assigned_by_run_id=run.id,
                        created_at=now,
                    )
                )

            snapshot = persisted_clusters.setdefault(
                cluster_row.id,
                {
                    "cluster_db_id": cluster_row.id,
                    "cluster_key": cluster_row.cluster_key,
                    "title": cluster_row.title,
                    "summary": cluster_row.summary or cluster["problem_statement"],
                    "niche": cluster_row.niche_label or cluster.get("niche") or "General",
                    "problem_count": 0,
                    "primary_document_id": document.id,
                    "primary_problem_id": problem.id,
                    "source": cluster["source"],
                    "url": cluster.get("url"),
                    "thread_title": cluster.get("thread_title"),
                    "quote": cluster.get("quote") or cluster["problem_statement"],
                    "problem_statement": cluster["problem_statement"],
                },
            )
            snapshot["problem_count"] += 1

        return list(persisted_clusters.values())

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
            research_output = self.pipeline.run_research(
                stage_callback=lambda stage, stage_label, message, metrics=None: self._emit_job_event(
                    session,
                    job_id,
                    event_type=f"pipeline_{stage}",
                    stage=stage,
                    stage_label=stage_label,
                    message=message,
                    metrics=metrics,
                )
            )
            persisted_clusters = self._persist_research_artifacts(session, run, research_output)
            opportunity_result = self.opportunity_engine.analyze_clusters(session, persisted_clusters)
            self._emit_job_event(
                session,
                job_id,
                event_type="pipeline_opportunity_analysis",
                stage="opportunity_analysis",
                stage_label="Opportunity analysis",
                message="Анализируем opportunity signals по найденным кластерам.",
                metrics=opportunity_result["metrics"],
            )

            generated = self.pipeline.generate_and_score(
                opportunity_result["clusters"],
                stage_callback=lambda stage, stage_label, message, metrics=None: self._emit_job_event(
                    session,
                    job_id,
                    event_type=f"pipeline_{stage}",
                    stage=stage,
                    stage_label=stage_label,
                    message=message,
                    metrics=metrics,
                ),
            )

            existing_ideas = session.exec(select(Idea)).all()
            persisted: list[dict] = []
            now = self._now()
            duplicates_skipped = 0
            linked_existing_ids: list[int] = []
            cluster_lookup = {cluster["cluster_db_id"]: cluster for cluster in opportunity_result["clusters"]}
            pipeline_metrics = {
                **research_output["metrics"],
                **opportunity_result["metrics"],
                "ideas_generated": len(generated),
            }

            self._emit_job_event(
                session,
                job_id,
                event_type="pipeline_save_results",
                stage="save_results",
                stage_label="Saving results",
                message="Сохраняем результаты pipeline в базу данных.",
                metrics=pipeline_metrics,
            )

            for item in generated:
                candidate_text = f"{item['title']}\n{item['summary']}"
                matched_existing = next(
                    (
                        existing
                        for existing in existing_ideas
                        if self.deduper.is_duplicate(candidate_text, f"{existing.title}\n{existing.summary}")
                    ),
                    None,
                )
                if matched_existing:
                    cluster_snapshot = cluster_lookup.get(item.get("cluster_db_id"))
                    matched_existing.cluster_id = item.get("cluster_db_id") or matched_existing.cluster_id
                    matched_existing.opportunity_score = item.get("opportunity_score") or matched_existing.opportunity_score
                    matched_existing.updated_at = now
                    if cluster_snapshot and cluster_snapshot.get("primary_document_id"):
                        matched_existing.primary_source_document_id = cluster_snapshot["primary_document_id"]
                    session.add(matched_existing)
                    linked_existing_ids.append(matched_existing.id)
                    duplicates_skipped += 1
                    continue

                cluster_snapshot = cluster_lookup.get(item.get("cluster_db_id"))
                document = session.get(Document, cluster_snapshot["primary_document_id"]) if cluster_snapshot else None
                if not document:
                    source = self._ensure_source(session, item["source"], now)
                    document = self._get_or_create_document(
                        session,
                        source_id=source.id,
                        external_id=f"generated-{slugify(item['title'])}",
                        canonical_url=item.get("source_url") or f"generated://{slugify(item['title'])}",
                        title=item.get("source_title") or item["title"],
                        content_text=item.get("source_quote") or item["problem"],
                        now=now,
                    )

                idea = Idea(
                    cluster_id=item.get("cluster_db_id"),
                    primary_source_document_id=document.id,
                    title=item["title"],
                    slug=slugify(item["title"]),
                    summary=item["summary"],
                    target_audience=item["audience"],
                    niche_label=item["niche"],
                    opportunity_score=item.get("opportunity_score"),
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
                session.add(
                    IdeaEvidence(
                        idea_id=idea.id,
                        evidence_type="document",
                        evidence_ref_id=document.id,
                        relevance_score=1.0,
                        note=item.get("source_quote"),
                        created_at=now,
                    )
                )
                if item.get("cluster_db_id"):
                    session.add(
                        IdeaEvidence(
                            idea_id=idea.id,
                            evidence_type="cluster",
                            evidence_ref_id=item["cluster_db_id"],
                            relevance_score=0.95,
                            note=cluster_snapshot["summary"] if cluster_snapshot else item["problem"],
                            created_at=now,
                        )
                    )
                if cluster_snapshot and cluster_snapshot.get("primary_problem_id"):
                    session.add(
                        IdeaEvidence(
                            idea_id=idea.id,
                            evidence_type="problem",
                            evidence_ref_id=cluster_snapshot["primary_problem_id"],
                            relevance_score=0.92,
                            note=item["problem"],
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
                persisted.append(
                    {
                        "id": idea.id,
                        "title": idea.title,
                        "summary": idea.summary,
                        "score": item["score"],
                        "cluster_id": idea.cluster_id,
                        "opportunity_score": idea.opportunity_score,
                    }
                )
                existing_ideas.append(idea)

            pipeline_metrics.update(
                {
                    "duplicates_skipped": duplicates_skipped,
                    "linked_existing_ideas": len(linked_existing_ids),
                    "new_ideas_added": len(persisted),
                    "ideas_added_to_database": len(persisted),
                }
            )
            self._emit_job_event(
                session,
                job_id,
                event_type="pipeline_save_summary",
                stage="save_results",
                stage_label="Saving results",
                message="Сохранение завершено. Pipeline summary обновлён.",
                metrics=pipeline_metrics,
            )

            self._emit_job_event(
                session,
                job_id,
                event_type="pipeline_rebuild_vectors",
                stage="save_results",
                stage_label="Saving results",
                message="Обновляем векторный индекс и артефакты поиска.",
                metrics=pipeline_metrics,
            )
            index_result = self.vector_search.rebuild_document_chunk_index(session, pipeline_run=run)
            run.status = "completed"
            run.finished_at = self._now()
            run.output_summary_json = json.dumps(
                {
                    "ideas_created": len(persisted),
                    "pipeline_metrics": pipeline_metrics,
                    "vector_index": index_result,
                },
                ensure_ascii=False,
            )
            session.commit()
            return {
                "pipeline_run_id": run.id,
                "ideas_created": len(persisted),
                "idea_ids": [item["id"] for item in persisted] + linked_existing_ids,
                "pipeline_metrics": pipeline_metrics,
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
