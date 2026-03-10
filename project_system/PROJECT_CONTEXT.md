# Project Context

AI Idea Research Lab is a local-first Windows desktop application for researching product opportunities from public discussions, generating startup ideas, scoring them, and producing starter project assets.

The repository has three main runtime layers:

- `ailab/backend`: FastAPI API, SQLite persistence, background job worker, pipeline orchestration, report generation, and local vector search.
- `ailab/frontend`: React single-page application used as the product UI.
- `ailab/launcher`: production launcher that starts FastAPI locally and opens the UI in a `pywebview` desktop window.

The product is no longer a mock dashboard. The current frontend is wired to the live backend and SQLite state:

- the dashboard loads real ideas and analytics from `/api`
- discovery runs through the async jobs system
- job progress is shown from `job_events`
- idea detail pages show a real markdown report preview
- project creation writes starter project folders and DB records
- settings switch the active LLM provider and UI theme

The current runtime model is desktop-first:

1. `start_app.bat` or `start.bat` checks the virtual environment and starts `ailab/launcher/launcher.py`.
2. The launcher starts FastAPI on `http://127.0.0.1:8000`.
3. FastAPI serves both the API under `/api/*` and the built frontend from `frontend/dist`.
4. The launcher opens a native desktop window with `pywebview` pointed at the local FastAPI URL.
5. On backend startup, migrations run, seed data is inserted if the DB is empty, and the in-process background worker starts.

The product flow is:

1. The dashboard enqueues an async discovery job.
2. The background worker claims and executes the job.
3. The orchestration service runs the idea pipeline:
   - collect discussion samples
   - extract normalized problems
   - cluster them
   - analyze opportunities
   - generate idea candidates
   - score ideas
   - persist problems, clusters, opportunities, ideas, reports, and source documents
   - rebuild the local vector index
4. The frontend polls job status and refreshes the idea list after completion.

The implementation is intentionally local and deterministic:

- SQLite stores metadata and lineage.
- Vector metadata is stored in SQLite, while vectors are written to local JSON files under `data/vector_index`.
- The provider layer supports `codex_cli` as the default local provider, with optional `openai` and `anthropic` configurations.
- Current source connectors and some research/generation stages are still scaffolded with placeholder/local implementations.
- The worker is a single daemon thread inside the FastAPI process.

This repository now also contains `project_system/`, which is the persistent memory layer for future Codex sessions.

The repository management workflow is now also standardized:

1. `project_system/` stores persistent architectural memory.
2. `project_system/reconstruct_context.py` prints a fast runtime summary for reopened sessions.
3. `scripts/dev_commit_push.*` provide quick add/commit/push helpers.
4. `scripts/dev_snapshot.bat` refreshes context, creates a snapshot commit, and pushes it.
