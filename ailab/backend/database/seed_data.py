from datetime import datetime

from sqlmodel import Session, select

from backend.models.document_model import Document
from backend.models.idea_model import Idea, IdeaScoreRecord, Report
from backend.models.model_registry_model import ModelRegistryEntry
from backend.models.source_model import Source
from backend.utils.slug_generator import slugify


def _get_or_create_source(session: Session, display_name: str, now: str) -> Source:
    source_key = slugify(display_name) or "manual"
    source = session.exec(select(Source).where(Source.source_key == source_key)).first()
    if source:
        return source

    source = Source(
        source_key=source_key,
        display_name=display_name,
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


def _seed_model_registry(session: Session, now: str) -> None:
    existing = session.exec(select(ModelRegistryEntry).where(ModelRegistryEntry.task_key == "idea_generation")).first()
    if existing:
        return

    entries = [
        ModelRegistryEntry(
            task_key="idea_generation",
            provider="local",
            model_name="placeholder-generator-v1",
            endpoint_type="chat",
            input_mode="text",
            output_schema_json='{"type":"idea"}',
            temperature=0.4,
            max_tokens=800,
            embedding_dimensions=None,
            is_default=True,
            enabled=True,
            fallback_model_id=None,
            config_json=None,
            created_at=now,
            updated_at=now,
        ),
        ModelRegistryEntry(
            task_key="embeddings",
            provider="local",
            model_name="placeholder-embeddings-v1",
            endpoint_type="embeddings",
            input_mode="text",
            output_schema_json=None,
            temperature=None,
            max_tokens=None,
            embedding_dimensions=384,
            is_default=True,
            enabled=True,
            fallback_model_id=None,
            config_json=None,
            created_at=now,
            updated_at=now,
        ),
    ]
    for entry in entries:
        session.add(entry)
    session.flush()


def seed_ideas(session: Session) -> None:
    existing = session.exec(select(Idea)).first()
    if existing:
        return

    now = datetime.utcnow().isoformat()
    _seed_model_registry(session, now)

    idea_rows = [
        {
            "title": "Библиотека промптов для команд",
            "summary": "Локальный сервис для хранения, поиска и оценки промптов внутри команды.",
            "score": 8.4,
            "niche": "AI tools",
            "source": "Reddit",
            "url": "https://reddit.com/r/saas/example",
        },
        {
            "title": "Трекер боли для саппорт-команд",
            "summary": "Инструмент, который группирует жалобы пользователей и выделяет повторяющиеся проблемы.",
            "score": 7.9,
            "niche": "Support",
            "source": "Hacker News",
            "url": "https://news.ycombinator.com/item?id=1",
        },
    ]

    for row in idea_rows:
        source = _get_or_create_source(session, row["source"], now)
        document = Document(
            source_id=source.id,
            external_id=slugify(row["title"]),
            canonical_url=row["url"],
            author_name=None,
            title=row["title"],
            language_code="ru",
            published_at=now,
            ingested_at=now,
            content_hash=slugify(row["title"]),
            raw_payload_path=None,
            normalized_payload_path=None,
            content_text=row["summary"],
            content_markdown=row["summary"],
            metadata_json=None,
            status="active",
        )
        session.add(document)
        session.flush()

        idea = Idea(
            cluster_id=None,
            primary_source_document_id=document.id,
            title=row["title"],
            slug=slugify(row["title"]),
            summary=row["summary"],
            target_audience="Solo founders, indie developers",
            niche_label=row["niche"],
            source_type="discussion-derived",
            generation_run_id=None,
            status="active",
            created_at=now,
            updated_at=now,
        )
        session.add(idea)
        session.flush()

        session.add(
            IdeaScoreRecord(
                idea_id=idea.id,
                scoring_run_id=None,
                market_demand_score=row["score"],
                competition_score=6.0,
                implementation_difficulty_score=5.0,
                monetization_score=8.0,
                confidence_score=0.8,
                total_score=row["score"],
                rationale_json='{"difficulty":"Средняя","monetization":"Подписка"}',
                created_at=now,
            )
        )
        session.add(
            Report(
                idea_id=idea.id,
                report_type="markdown",
                output_path=f"idea_reports/{slugify(row['title'])}.md",
                markdown_checksum=None,
                generated_by_run_id=None,
                created_at=now,
            )
        )

    session.commit()
