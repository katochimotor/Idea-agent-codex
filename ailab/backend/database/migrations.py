import sqlite3
from datetime import datetime
from pathlib import Path

from backend.settings import settings
from backend.utils.slug_generator import slugify


SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def _connect() -> sqlite3.Connection:
    db_path = Path(settings.database_url.removeprefix("sqlite:///"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def apply_sqlite_schema() -> None:
    with _connect() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def _ensure_source(connection: sqlite3.Connection, display_name: str, now: str) -> int:
    source_key = slugify(display_name) or "manual"
    existing = connection.execute(
        "SELECT id FROM sources WHERE source_key = ?",
        (source_key,),
    ).fetchone()
    if existing:
        return int(existing["id"])

    cursor = connection.execute(
        """
        INSERT INTO sources (
            source_key, display_name, source_type, base_url, enabled, config_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (source_key, display_name, "legacy", None, 1, None, now, now),
    )
    return int(cursor.lastrowid)


def _ensure_legacy_document(
    connection: sqlite3.Connection,
    source_id: int,
    legacy_row: sqlite3.Row,
    now: str,
) -> int:
    canonical_url = f"legacy://idea/{legacy_row['id']}"
    existing = connection.execute(
        "SELECT id FROM documents WHERE canonical_url = ?",
        (canonical_url,),
    ).fetchone()
    if existing:
        return int(existing["id"])

    cursor = connection.execute(
        """
        INSERT INTO documents (
            source_id,
            external_id,
            canonical_url,
            author_name,
            title,
            language_code,
            published_at,
            ingested_at,
            content_hash,
            raw_payload_path,
            normalized_payload_path,
            content_text,
            content_markdown,
            metadata_json,
            status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_id,
            f"legacy-idea-{legacy_row['id']}",
            canonical_url,
            None,
            legacy_row["title"],
            "ru",
            legacy_row["created_at"],
            now,
            f"legacy-idea-{legacy_row['id']}",
            None,
            None,
            legacy_row["summary"],
            legacy_row["summary"],
            None,
            "active",
        ),
    )
    return int(cursor.lastrowid)


def migrate_legacy_schema() -> None:
    with _connect() as connection:
        now = datetime.utcnow().isoformat()

        if _table_exists(connection, "idea"):
            legacy_ideas = connection.execute("SELECT * FROM idea ORDER BY id").fetchall()
            for legacy_idea in legacy_ideas:
                slug = slugify(legacy_idea["title"]) or f"legacy-idea-{legacy_idea['id']}"
                existing = connection.execute(
                    "SELECT id FROM ideas WHERE slug = ?",
                    (slug,),
                ).fetchone()
                if existing:
                    continue

                source_id = _ensure_source(connection, legacy_idea["source"], now)
                document_id = _ensure_legacy_document(connection, source_id, legacy_idea, now)

                cursor = connection.execute(
                    """
                    INSERT INTO ideas (
                        cluster_id,
                        primary_source_document_id,
                        title,
                        slug,
                        summary,
                        target_audience,
                        niche_label,
                        source_type,
                        generation_run_id,
                        status,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        None,
                        document_id,
                        legacy_idea["title"],
                        slug,
                        legacy_idea["summary"],
                        "Solo founders, indie developers",
                        legacy_idea["niche"],
                        "discussion-derived",
                        None,
                        "active",
                        legacy_idea["created_at"],
                        legacy_idea["created_at"],
                    ),
                )
                new_idea_id = int(cursor.lastrowid)

                connection.execute(
                    """
                    INSERT INTO idea_scores (
                        idea_id,
                        scoring_run_id,
                        market_demand_score,
                        competition_score,
                        implementation_difficulty_score,
                        monetization_score,
                        confidence_score,
                        total_score,
                        rationale_json,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        new_idea_id,
                        None,
                        float(legacy_idea["score"]),
                        6.0,
                        5.0,
                        8.0,
                        0.8,
                        float(legacy_idea["score"]),
                        legacy_idea["tags"],
                        legacy_idea["created_at"],
                    ),
                )

                connection.execute(
                    """
                    INSERT INTO reports (
                        idea_id,
                        report_type,
                        output_path,
                        markdown_checksum,
                        generated_by_run_id,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        new_idea_id,
                        "markdown",
                        f"idea_reports/{slug}.md",
                        None,
                        None,
                        legacy_idea["created_at"],
                    ),
                )

        if _table_exists(connection, "project"):
            legacy_projects = connection.execute("SELECT * FROM project ORDER BY id").fetchall()
            for legacy_project in legacy_projects:
                existing = connection.execute(
                    "SELECT id FROM projects WHERE folder_path = ?",
                    (legacy_project["folder_path"],),
                ).fetchone()
                if existing:
                    continue

                cursor = connection.execute(
                    """
                    INSERT INTO projects (
                        idea_id,
                        title,
                        folder_path,
                        status,
                        created_by_job_id,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        legacy_project["idea_id"],
                        Path(legacy_project["folder_path"]).name,
                        legacy_project["folder_path"],
                        "generated",
                        None,
                        legacy_project["created_at"],
                        legacy_project["created_at"],
                    ),
                )
                project_id = int(cursor.lastrowid)
                connection.execute(
                    """
                    INSERT OR IGNORE INTO project_files (
                        project_id, relative_path, file_type, checksum, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (project_id, "README.md", "markdown", None, legacy_project["created_at"], legacy_project["created_at"]),
                )

        ideas_without_reports = connection.execute(
            """
            SELECT i.id, i.slug
            FROM ideas i
            LEFT JOIN reports r ON r.idea_id = i.id
            WHERE r.id IS NULL
            """
        ).fetchall()
        for row in ideas_without_reports:
            connection.execute(
                """
                INSERT INTO reports (
                    idea_id,
                    report_type,
                    output_path,
                    markdown_checksum,
                    generated_by_run_id,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (row["id"], "markdown", f"idea_reports/{row['slug']}.md", None, None, now),
            )

        connection.commit()


def run_migrations() -> None:
    apply_sqlite_schema()
    migrate_legacy_schema()
