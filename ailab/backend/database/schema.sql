PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    source_key TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    base_url TEXT,
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    config_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_checkpoints (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    cursor_value TEXT,
    cursor_type TEXT,
    last_document_published_at TEXT,
    status TEXT NOT NULL DEFAULT 'idle' CHECK (status IN ('idle', 'running', 'completed', 'failed')),
    last_run_id INTEGER,
    last_error TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
    FOREIGN KEY (last_run_id) REFERENCES pipeline_runs(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_source_checkpoints_source_id
    ON source_checkpoints(source_id);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    external_id TEXT,
    canonical_url TEXT NOT NULL,
    author_name TEXT,
    title TEXT,
    language_code TEXT NOT NULL DEFAULT 'en',
    published_at TEXT,
    ingested_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    raw_payload_path TEXT,
    normalized_payload_path TEXT,
    content_text TEXT NOT NULL,
    content_markdown TEXT,
    metadata_json TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'duplicate', 'deleted', 'filtered')),
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_source_external_id
    ON documents(source_id, external_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_canonical_url
    ON documents(canonical_url);

CREATE INDEX IF NOT EXISTS idx_documents_source_published_at
    ON documents(source_id, published_at DESC);

CREATE INDEX IF NOT EXISTS idx_documents_content_hash
    ON documents(content_hash);

CREATE TABLE IF NOT EXISTS document_fingerprints (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    fingerprint_type TEXT NOT NULL,
    fingerprint_value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_document_fingerprints_unique
    ON document_fingerprints(fingerprint_type, fingerprint_value);

CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    token_count INTEGER,
    char_start INTEGER,
    char_end INTEGER,
    content_hash TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_document_chunks_document_chunk
    ON document_chunks(document_id, chunk_index);

CREATE INDEX IF NOT EXISTS idx_document_chunks_content_hash
    ON document_chunks(content_hash);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled', 'retrying')),
    priority INTEGER NOT NULL DEFAULT 100,
    requested_by TEXT,
    parent_job_id INTEGER,
    payload_json TEXT,
    result_json TEXT,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    scheduled_at TEXT,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (parent_job_id) REFERENCES jobs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_status_priority
    ON jobs(status, priority, created_at);

CREATE INDEX IF NOT EXISTS idx_jobs_job_type
    ON jobs(job_type, created_at DESC);

CREATE TABLE IF NOT EXISTS job_events (
    id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT,
    message TEXT,
    payload_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_job_events_job_id_created_at
    ON job_events(job_id, created_at);

CREATE TABLE IF NOT EXISTS model_registry_entries (
    id INTEGER PRIMARY KEY,
    task_key TEXT NOT NULL,
    provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    endpoint_type TEXT NOT NULL,
    input_mode TEXT NOT NULL,
    output_schema_json TEXT,
    temperature REAL,
    max_tokens INTEGER,
    embedding_dimensions INTEGER,
    is_default INTEGER NOT NULL DEFAULT 0 CHECK (is_default IN (0, 1)),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    fallback_model_id INTEGER,
    config_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (fallback_model_id) REFERENCES model_registry_entries(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_model_registry_task_model
    ON model_registry_entries(task_key, provider, model_name);

CREATE INDEX IF NOT EXISTS idx_model_registry_task_default
    ON model_registry_entries(task_key, is_default, enabled);

CREATE TABLE IF NOT EXISTS prompt_versions (
    id INTEGER PRIMARY KEY,
    prompt_key TEXT NOT NULL,
    version_label TEXT NOT NULL,
    template_text TEXT NOT NULL,
    variables_json TEXT,
    checksum TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (prompt_key, version_label)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    trigger_type TEXT NOT NULL CHECK (trigger_type IN ('manual', 'scheduled', 'job', 'system')),
    job_id INTEGER,
    model_registry_entry_id INTEGER,
    prompt_version_id INTEGER,
    input_summary_json TEXT,
    output_summary_json TEXT,
    error_message TEXT,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL,
    FOREIGN KEY (model_registry_entry_id) REFERENCES model_registry_entries(id) ON DELETE SET NULL,
    FOREIGN KEY (prompt_version_id) REFERENCES prompt_versions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_type_status
    ON pipeline_runs(run_type, status, created_at DESC);

CREATE TABLE IF NOT EXISTS run_artifacts (
    id INTEGER PRIMARY KEY,
    pipeline_run_id INTEGER NOT NULL,
    artifact_type TEXT NOT NULL,
    artifact_ref_type TEXT NOT NULL,
    artifact_ref_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_run_artifacts_run_type
    ON run_artifacts(pipeline_run_id, artifact_type);

CREATE TABLE IF NOT EXISTS extraction_runs (
    id INTEGER PRIMARY KEY,
    pipeline_run_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    extractor_name TEXT NOT NULL,
    extractor_version TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    output_json TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_extraction_runs_document_id
    ON extraction_runs(document_id, created_at DESC);

CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    extraction_run_id INTEGER,
    normalized_text TEXT NOT NULL,
    original_text TEXT,
    problem_type TEXT,
    severity_score REAL,
    evidence_span_json TEXT,
    language_code TEXT NOT NULL DEFAULT 'en',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'merged', 'discarded')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL,
    FOREIGN KEY (extraction_run_id) REFERENCES extraction_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_problems_document_id
    ON problems(document_id);

CREATE INDEX IF NOT EXISTS idx_problems_status
    ON problems(status, created_at DESC);

CREATE TABLE IF NOT EXISTS problem_clusters (
    id INTEGER PRIMARY KEY,
    cluster_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT,
    niche_label TEXT,
    centroid_vector_key TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'merged', 'archived')),
    created_by_run_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (created_by_run_id) REFERENCES pipeline_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_problem_clusters_niche
    ON problem_clusters(niche_label, created_at DESC);

CREATE TABLE IF NOT EXISTS problem_cluster_memberships (
    id INTEGER PRIMARY KEY,
    cluster_id INTEGER NOT NULL,
    problem_id INTEGER NOT NULL,
    membership_score REAL,
    assigned_by_run_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (cluster_id) REFERENCES problem_clusters(id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by_run_id) REFERENCES pipeline_runs(id) ON DELETE SET NULL,
    UNIQUE (cluster_id, problem_id)
);

CREATE INDEX IF NOT EXISTS idx_problem_cluster_memberships_problem
    ON problem_cluster_memberships(problem_id);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    cluster_id INTEGER,
    primary_source_document_id INTEGER,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    target_audience TEXT,
    niche_label TEXT,
    source_type TEXT NOT NULL CHECK (source_type IN ('discussion-derived', 'ai-generated', 'hybrid')),
    generation_run_id INTEGER,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'rejected')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (cluster_id) REFERENCES problem_clusters(id) ON DELETE SET NULL,
    FOREIGN KEY (primary_source_document_id) REFERENCES documents(id) ON DELETE SET NULL,
    FOREIGN KEY (generation_run_id) REFERENCES pipeline_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_ideas_cluster_id
    ON ideas(cluster_id);

CREATE INDEX IF NOT EXISTS idx_ideas_status_created_at
    ON ideas(status, created_at DESC);

CREATE TABLE IF NOT EXISTS idea_scores (
    id INTEGER PRIMARY KEY,
    idea_id INTEGER NOT NULL,
    scoring_run_id INTEGER,
    market_demand_score REAL NOT NULL,
    competition_score REAL NOT NULL,
    implementation_difficulty_score REAL NOT NULL,
    monetization_score REAL NOT NULL,
    confidence_score REAL,
    total_score REAL NOT NULL,
    rationale_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (scoring_run_id) REFERENCES pipeline_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_idea_scores_idea_id_created_at
    ON idea_scores(idea_id, created_at DESC);

CREATE TABLE IF NOT EXISTS idea_evidence (
    id INTEGER PRIMARY KEY,
    idea_id INTEGER NOT NULL,
    evidence_type TEXT NOT NULL CHECK (evidence_type IN ('document', 'chunk', 'problem', 'cluster')),
    evidence_ref_id INTEGER NOT NULL,
    relevance_score REAL,
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_idea_evidence_idea_id
    ON idea_evidence(idea_id);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY,
    idea_id INTEGER NOT NULL,
    report_type TEXT NOT NULL,
    output_path TEXT NOT NULL,
    markdown_checksum TEXT,
    generated_by_run_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by_run_id) REFERENCES pipeline_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_reports_idea_id
    ON reports(idea_id, created_at DESC);

CREATE TABLE IF NOT EXISTS vector_collections (
    id INTEGER PRIMARY KEY,
    collection_key TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('document_chunk', 'problem', 'cluster', 'idea')),
    embedding_model_id INTEGER NOT NULL,
    dimensions INTEGER NOT NULL,
    metric TEXT NOT NULL DEFAULT 'cosine',
    index_path TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (embedding_model_id) REFERENCES model_registry_entries(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS vector_entries (
    id INTEGER PRIMARY KEY,
    collection_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('document_chunk', 'problem', 'cluster', 'idea')),
    vector_key TEXT NOT NULL,
    vector_hash TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES vector_collections(id) ON DELETE CASCADE,
    UNIQUE (collection_id, entity_type, entity_id, version),
    UNIQUE (vector_key)
);

CREATE INDEX IF NOT EXISTS idx_vector_entries_collection_entity
    ON vector_entries(collection_id, entity_type, entity_id);

CREATE TABLE IF NOT EXISTS vector_sync_runs (
    id INTEGER PRIMARY KEY,
    collection_id INTEGER NOT NULL,
    pipeline_run_id INTEGER,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    inserted_count INTEGER NOT NULL DEFAULT 0,
    updated_count INTEGER NOT NULL DEFAULT 0,
    deleted_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES vector_collections(id) ON DELETE CASCADE,
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    idea_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    folder_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'generated' CHECK (status IN ('generated', 'updated', 'archived')),
    created_by_job_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_job_id) REFERENCES jobs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_projects_idea_id
    ON projects(idea_id, created_at DESC);

CREATE TABLE IF NOT EXISTS project_files (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    relative_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    checksum TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE (project_id, relative_path)
);

COMMIT;
