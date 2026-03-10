# Project Context

AI Idea Research Lab is a local-first Windows desktop application for researching product opportunities from public discussions, generating startup ideas, scoring them, and producing starter project assets.

The repository has three main runtime layers:

- `ailab/backend`: FastAPI API, SQLite persistence, background job worker, pipeline orchestration, report generation, and local vector search.
- `ailab/frontend`: React single-page application used as the product UI.
- `ailab/launcher`: production launcher that starts FastAPI locally and opens the UI in a `pywebview` desktop window.

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
   - generate idea candidates
   - score ideas
   - persist ideas, reports, and source documents
   - rebuild the local vector index
4. The frontend polls job status and refreshes the idea list after completion.

The implementation is intentionally local and deterministic:

- SQLite stores metadata and lineage.
- Vector metadata is stored in SQLite, while vectors are written to local JSON files under `data/vector_index`.
- Current source connectors, idea generation, and scoring are scaffolded with placeholder/local implementations.
- The worker is a single daemon thread inside the FastAPI process.

This repository now also contains `project_system/`, which is the persistent memory layer for future Codex sessions.

The repository management workflow is now also standardized:

1. `project_system/` stores persistent architectural memory.
2. `project_system/reconstruct_context.py` prints a fast runtime summary for reopened sessions.
3. `scripts/dev_commit_push.*` provide quick add/commit/push helpers.
4. `scripts/dev_snapshot.bat` refreshes context, creates a snapshot commit, and pushes it.
