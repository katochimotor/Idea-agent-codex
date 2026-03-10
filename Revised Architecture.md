# AI Idea Research Lab
## Revised Architecture

This version keeps the current product local-first and simple for MVP, but adds the minimum architectural seams required for a scalable AI idea research system.

## 1. Architecture Goals

The revised architecture must:

- keep the MVP runnable on one local machine
- support asynchronous long-running research jobs
- standardize ingestion from multiple public sources
- preserve raw evidence and processing lineage
- support semantic search over documents, problems, and ideas
- make AI model selection explicit and configurable

The system should still feel like a desktop product:

Launcher -> Local API -> Background Worker -> Local Database/Indexes -> Web Dashboard

## 2. Design Principles

1. Local-first by default.
2. Simple MVP implementation, scalable interfaces.
3. Clear separation between ingestion, research, retrieval, and UI.
4. Every generated idea must be traceable back to source evidence.
5. AI calls must be versioned and reproducible.

## 3. Revised High-Level Topology

```text
Desktop Launcher
      |
      v
Web Dashboard (React)
      |
      v
Local API Server (FastAPI)
      |
      +--------------------------+
      |                          |
      v                          v
Job API / Orchestrator      Query API
      |                          |
      v                          v
Background Worker          Vector Search API
      |                          |
      v                          v
Ingestion Framework        AI Model Registry
      |                          |
      v                          v
Document Store --------> Embedding Pipeline
      |                          |
      v                          v
Problem Extraction / Clustering / Idea Generation / Scoring
      |
      v
SQLite Metadata DB + Local Vector Index + File-based Raw Document Store
```

## 4. Runtime Model

The system now has two execution modes:

- synchronous query path
  - list ideas
  - open idea details
  - search problems or ideas
  - view analytics
- asynchronous job path
  - crawl sources
  - extract problems
  - cluster problems
  - generate ideas
  - score ideas
  - refresh embeddings
  - build starter project

The API should return a `job_id` for long-running actions instead of blocking the request.

## 5. Async Job System

### 5.1 Why it is needed

Source collection, extraction, embeddings, clustering, and idea generation will become slow and failure-prone as data volume grows. These should not run inline inside an HTTP request.

### 5.2 MVP design

Keep the MVP simple:

- one `jobs` table in SQLite
- one `job_events` table for state transitions and logs
- one local worker process or thread-based worker service
- polling from the dashboard every few seconds

### 5.3 Scale-ready interface

The orchestration interface should be storage-agnostic so the job backend can later move to Redis, Postgres queue tables, Temporal, or Celery without changing the application API.

### 5.4 Job types

- `discover_sources`
- `ingest_source_batch`
- `extract_problems`
- `cluster_problems`
- `generate_ideas`
- `score_ideas`
- `refresh_embeddings`
- `build_project`
- `export_report`

### 5.5 Job states

- `queued`
- `running`
- `completed`
- `failed`
- `cancelled`
- `retrying`

### 5.6 Required backend modules

```text
backend/
  jobs/
    job_models.py
    job_repository.py
    job_service.py
    worker.py
    scheduler.py
```

### 5.7 API additions

- `POST /api/jobs/discover`
- `POST /api/jobs/embeddings/rebuild`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/events`

## 6. Ingestion Framework

### 6.1 Why it is needed

Source adapters are currently just service files. A scalable system needs a consistent ingestion contract so each source can be crawled, normalized, deduplicated, and reprocessed predictably.

### 6.2 Source connector contract

Each connector should implement:

- `fetch_batch(cursor)`
- `normalize(raw_item)`
- `fingerprint(document)`
- `extract_metadata(document)`
- `rate_limit_policy()`

### 6.3 Ingestion stages

```text
Source Connector
  -> Raw Fetch
  -> Normalization
  -> Deduplication
  -> Document Persistence
  -> Chunking
  -> Embedding
  -> Extraction Trigger
```

### 6.4 MVP implementation

For the first version:

- support Reddit, Hacker News, RSS, and manual import
- store cursors/checkpoints in SQLite
- deduplicate by source URL hash plus text fingerprint
- run ingestion from one local worker

### 6.5 Required backend modules

```text
backend/
  ingestion/
    base_connector.py
    registry.py
    pipeline.py
    deduper.py
    normalizer.py
    checkpoints.py
    connectors/
      reddit_connector.py
      hackernews_connector.py
      rss_connector.py
      manual_connector.py
```

## 7. Document Store

### 7.1 Why it is needed

The current schema stores final ideas and extracted problems, but not the original evidence. That prevents auditability, reprocessing, and better retrieval.

### 7.2 Revised storage model

Use a split storage approach:

- SQLite for metadata and relationships
- local filesystem for raw document payloads and normalized JSON documents

This keeps the MVP simple and local, while preserving a clean upgrade path to object storage or Postgres JSONB later.

### 7.3 Document layers

- raw documents
  - exact source payloads
- normalized documents
  - canonical text, metadata, source identifiers
- chunks
  - text chunks for embeddings and retrieval
- derived artifacts
  - extracted problems, clusters, reports, idea evidence links

### 7.4 File layout

```text
data/
  docstore/
    raw/
      reddit/
      hackernews/
      rss/
    normalized/
    chunks/
```

### 7.5 Core metadata tables

- `sources`
- `source_checkpoints`
- `documents`
- `document_chunks`
- `document_fingerprints`
- `extraction_runs`
- `problems`
- `problem_clusters`
- `ideas`
- `idea_evidence`
- `projects`

### 7.6 Required backend modules

```text
backend/
  docstore/
    document_repository.py
    raw_store.py
    normalized_store.py
    chunk_store.py
```

## 8. Vector Search

### 8.1 Why it is needed

Semantic search is required for:

- grouping similar complaints
- finding related problems
- retrieving evidence for an idea
- trend exploration
- idea deduplication

### 8.2 MVP implementation

Keep it local and simple:

- generate embeddings in batches
- persist vectors in a local on-disk index
- keep vector metadata in SQLite
- expose search through one backend service

Good MVP options are:

- a lightweight local FAISS index
- or a SQLite-friendly local vector extension

The important decision is the abstraction boundary, not the specific library.

### 8.3 Search entities

- document chunks
- problems
- problem clusters
- ideas

### 8.4 Search APIs

- `POST /api/search/documents`
- `POST /api/search/problems`
- `POST /api/search/ideas`
- `GET /api/ideas/{id}/evidence`

### 8.5 Required backend modules

```text
backend/
  search/
    embedding_service.py
    vector_index.py
    retriever.py
    similarity.py
```

## 9. AI Model Registry

### 9.1 Why it is needed

The system will use different models for:

- problem extraction
- clustering support
- idea generation
- scoring assistance
- report generation
- project generation
- embeddings

Without an explicit registry, model changes become invisible and results become hard to reproduce.

### 9.2 MVP implementation

Keep the MVP lightweight:

- one registry file in YAML or JSON
- one backend service that resolves the active model by task
- prompt templates versioned in files
- store model id and prompt version with every run

### 9.3 Registry fields

- `task`
- `provider`
- `model_name`
- `endpoint_type`
- `input_mode`
- `output_schema`
- `temperature`
- `max_tokens`
- `embedding_dimensions`
- `enabled`
- `fallback_model`

### 9.4 Required backend modules

```text
backend/
  model_registry/
    registry.yaml
    service.py
    schemas.py
    resolver.py
```

### 9.5 Model-aware run metadata

Every extraction or generation run should persist:

- model name
- provider
- prompt template id
- prompt version
- run timestamp
- input document ids
- output artifact ids

## 10. Revised Research Flow

### 10.1 Ingestion flow

```text
Scheduler
  -> enqueue ingest job
  -> connector fetches batch
  -> normalize document
  -> deduplicate
  -> save raw payload
  -> save normalized document
  -> chunk document
  -> create embedding job
  -> create extraction job
```

### 10.2 Idea generation flow

```text
User clicks "Найти идеи"
  -> API creates research job
  -> worker loads recent documents/problems
  -> cluster problems
  -> generate ideas
  -> score ideas
  -> link evidence
  -> save ideas
  -> emit job completion event
  -> dashboard refreshes
```

## 11. Revised Data Model

The current MVP tables remain, but the model should expand to:

### Core metadata

- `sources`
- `source_checkpoints`
- `documents`
- `document_chunks`
- `document_fingerprints`
- `jobs`
- `job_events`

### Research artifacts

- `problems`
- `problem_clusters`
- `ideas`
- `idea_scores`
- `idea_evidence`
- `reports`

### AI traceability

- `model_registry_entries`
- `prompt_versions`
- `pipeline_runs`
- `run_artifacts`

### Project generation

- `projects`
- `project_files`

## 12. Revised Repository Structure

```text
ailab/
  launcher/
  backend/
    api/
    controllers/
    jobs/
    ingestion/
    docstore/
    search/
    model_registry/
    agents/
    pipelines/
    ai/
    models/
    database/
    services/
    utils/
  frontend/
  templates/
  projects/
  idea_reports/
  data/
    docstore/
    vector_index/
```

## 13. Keeping the MVP Simple

The MVP should not introduce distributed infrastructure yet.

### MVP decisions

- keep FastAPI
- keep React/Vite
- keep SQLite as the main metadata store
- keep local filesystem for document payloads
- keep one local worker process
- keep one local vector index
- keep a file-based model registry
- keep polling-based job status in the UI

### Explicitly deferred

- Redis or Kafka
- cloud object storage
- distributed workers
- multi-tenant auth
- managed vector database
- online model experimentation platform

## 14. Scale-Up Path

The revised architecture is intentionally layered so each subsystem can evolve independently.

### Phase 1: MVP

- SQLite metadata
- filesystem docstore
- local worker
- local vector index
- YAML model registry

### Phase 2: Advanced local / small team

- separate worker process
- stronger document dedupe
- richer evidence graph
- scheduled recurring ingestion
- review workflow for idea quality

### Phase 3: cloud or collaborative version

- Postgres for metadata
- object storage for documents
- Qdrant/pgvector for search
- distributed job queue
- authentication and workspace boundaries

## 15. Recommended Next Implementation Changes

To evolve the current scaffold without overbuilding, add these next:

1. `backend/jobs/worker.py` and SQLite-backed job tables
2. `backend/ingestion/` connector framework with checkpoints and dedupe
3. `backend/docstore/` for raw and normalized document persistence
4. `backend/search/` with one local vector index
5. `backend/model_registry/registry.yaml` and task-based model resolution

This keeps the current MVP small while removing the main architectural bottlenecks.
