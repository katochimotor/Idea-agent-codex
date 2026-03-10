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

### Frontend MVP state

- Dashboard is connected to live backend data and no longer uses static placeholder cards.
- Idea cards render real `title`, `summary`, `score`, `source`, `tags`, and `created_at` values from SQLite-backed API responses.
- The progress panel renders live `job_events`, current pipeline stage, failure messages, and loading states.
- The projects page loads real projects from the database.
- The idea detail page now guarantees a report preview by regenerating a markdown report file if the DB path exists but the file is missing.
- A light/dark theme toggle exists in Settings and is persisted in `localStorage`.

### Provider configuration

- Default provider is `codex_cli`.
- Optional providers remain:
  - `openai`
  - `anthropic`
- Settings page supports:
  - loading saved provider state
  - testing provider connectivity
  - saving active provider configuration
- Provider API clients now handle non-JSON backend failures more safely in the UI.

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
- Root-level `SESSION_REPORT.md` is the short human-readable summary of the latest completed work.

## Latest Verified State

- `npm run build` passes for the frontend.
- Python `compileall` passes for backend, launcher, and `project_system`.
- End-to-end smoke testing was run against a live local FastAPI process:
  - dashboard endpoints responded
  - provider test/save endpoints responded
  - discovery job completed successfully
  - `job_events` were returned with stage messages
  - idea reports existed on disk and were readable
  - project creation endpoint wrote a DB record and project folder

## Known Gaps

- No separate worker process; worker is still in-process.
- Source connectors and parts of research generation are still placeholders.
- No websocket or server-sent event progress streaming.
- No persisted problem/cluster lineage yet.
- Search currently covers only `document_chunks`.
