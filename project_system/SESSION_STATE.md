# Session State

## Current Implementation State

### Async job system

- Implemented and active.
- `jobs` and `job_events` are persisted in SQLite.
- `BackgroundJobWorker` runs inside the FastAPI process as a daemon thread.
- Frontend uses `/api/jobs/discover` and polls `/api/jobs/{id}` until completion.
- Supported job types:
  - `discover_ideas`
  - `refresh_embeddings`

### Pipeline orchestration

- `PipelineOrchestrationService` is the central runtime service.
- It creates `pipeline_runs`, resolves model registry entries, executes idea discovery, deduplicates ideas, writes reports, and rebuilds the document chunk vector index.
- Discovery persistence currently writes:
  - `sources`
  - `documents`
  - `ideas`
  - `idea_scores`
  - `reports`
- Problem extraction and clustering are not yet persisted into `problems` / `problem_clusters`; those parts are still in-memory scaffolds.

### Vector search

- Working local implementation for document chunk search.
- Embeddings are deterministic hash-based vectors from `backend/search/embedding_service.py`.
- Vector metadata is stored in SQLite tables:
  - `vector_collections`
  - `vector_entries`
  - `vector_sync_runs`
- Raw vectors are stored in JSON files under `ailab/data/vector_index/`.
- Search endpoint:
  - `POST /api/search/documents`

### Document store

- Source documents are stored in `documents`.
- Text chunks are stored in `document_chunks`.
- Fingerprint table exists in schema, but current orchestration primarily relies on `SemanticDeduplicationEngine` and content hashes.
- Raw payload paths and normalized payload paths are schema-ready but not fully used by the current stub connectors.

### Frontend polling

- Dashboard starts discovery through the async jobs API.
- Polling interval is 1500 ms with a default timeout of 45 seconds.
- After job completion the dashboard reloads the idea list.
- API clients now use same-origin `/api`, which matches desktop/static serving mode.

### Launcher

- Converted to desktop mode.
- Launcher now starts only FastAPI in production mode.
- The frontend is expected to be prebuilt into `ailab/frontend/dist`.
- FastAPI serves the built SPA directly.
- Launcher opens `pywebview` instead of the system browser.
- When the desktop window closes, the launcher terminates the backend process it started.

### Repository workflow

- `project_system` is now the persistent project memory layer for future sessions.
- `reconstruct_context.py` is the quick context rebuild entrypoint.
- `scripts/dev_commit_push.bat` and `scripts/dev_commit_push.ps1` automate add/commit/push.
- `scripts/dev_snapshot.bat` captures a project-context snapshot and pushes it.

## Known Gaps

- No separate worker process; worker is still in-process.
- Source connectors and LLM generation are placeholders.
- No websocket or server-sent event progress streaming.
- No persisted problem/cluster lineage yet.
- Search currently covers only `document_chunks`.
