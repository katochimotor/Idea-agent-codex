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
- Current discovery flow:
  - collect discussions
  - extract problems
  - cluster problems
  - opportunity analysis
  - generate ideas
  - score ideas
  - save results
- Discovery persistence now writes:
  - `sources`
  - `documents`
  - `problems`
  - `problem_clusters`
  - `problem_cluster_memberships`
  - `opportunities`
  - `ideas`
  - `idea_scores`
  - `reports`
  - `idea_evidence`
- Job feedback now includes:
  - `documents_scanned`
  - `problems_extracted`
  - `clusters_detected`
  - `clusters_analyzed`
  - `opportunities_discovered`
  - `top_opportunity_score`
  - `ideas_generated`
  - `duplicates_skipped`
  - `linked_existing_ideas`
  - `ideas_added_to_database`

### Opportunity engine

- Implemented in `backend/services/opportunity_engine.py`.
- Runs after clustering and before idea generation.
- Calculates and stores:
  - `pain_score`
  - `frequency_score`
  - `solution_gap_score`
  - `market_score`
  - `build_complexity_score`
  - `opportunity_score`
- Exposes API:
  - `GET /api/opportunities`
  - `GET /api/opportunities/{cluster_id}`

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
- Extracted problems are stored in `problems`.
- Cluster structure is stored in `problem_clusters` and `problem_cluster_memberships`.
- Opportunity signals are stored in `opportunities`.

### Frontend MVP state

- Dashboard is connected to live backend data.
- `Latest Pipeline Results` uses real results from the latest discovery run.
- `Startup Opportunities` uses `/api/opportunities`.
- `PipelineRunPanel` shows stage progress, metrics, and advanced logs.
- Idea cards render source traceability, source links, cluster links, and opportunity score.
- Idea detail page renders report preview and source evidence.
- Opportunity detail page is implemented and linked from dashboard/cards.
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
- Offline/local verification is still possible because `LLMClient` has a deterministic fallback path when no external provider is configured.

### Launcher

- Desktop runtime is stable:
  - `start_app.bat` -> launcher -> FastAPI -> built React SPA -> `pywebview`
- Launcher starts FastAPI in production mode and opens `pywebview`.
- When the desktop window closes, the launcher terminates the backend process it started.

### Repository workflow

- `project_system` is the persistent memory layer for future Codex sessions.
- `reconstruct_context.py` is the quick context rebuild entrypoint.
- `SESSION_REPORT.md` is the short human-readable summary of the latest completed work.
- `.gitignore` now excludes generated `ailab/projects/` runtime folders so test project artifacts do not pollute future commits.

## Latest Verified State

- `npm run build` passes for the frontend.
- Python `compileall` passes for backend.
- End-to-end smoke testing was run against a live local FastAPI process:
  - discovery job completed successfully
  - `opportunities` table exists
  - `ideas.opportunity_score` exists
  - `/api/opportunities` returned top opportunities
  - `/api/dashboard` returned top opportunities and latest results
  - all ideas received `cluster_id`
  - all ideas received `opportunity_score`
  - opportunity detail returned `related_ideas`

## Known Gaps

- No separate worker process; worker is still in-process.
- Source connectors and parts of research generation are still placeholders.
- No websocket or server-sent event progress streaming.
- Search still focuses on `document_chunks`; opportunity/problem/idea search can be expanded later.
- Opportunity detail exists, but a dedicated cluster detail workflow is not yet implemented.
