# System Map

## Repository Root

- `start_app.bat`: primary desktop startup script for local use.
- `start.bat`: legacy root launcher script; still works and now opens the desktop app.
- `build_exe.bat`: PyInstaller packaging helper for building `launcher.exe`.
- `project_system/`: persistent project memory and context reconstruction tooling.
- `ailab/`: main application source tree.
- top-level `*.md`: original product, PRD, UX, and architecture notes.

## `ailab/`

### `backend/`

- `main.py`: FastAPI import entrypoint.
- `app.py`: application factory, router registration, startup/shutdown lifecycle, static frontend serving.
- `settings.py`: runtime paths and app configuration for normal and frozen builds.
- `logger.py`: file logger setup.

### `backend/api/`

- `routes_dashboard.py`: dashboard summary and analytics endpoints.
- `routes_ideas.py`: idea list, synchronous discovery wrapper, idea detail.
- `routes_jobs.py`: async job enqueueing and polling.
- `routes_projects.py`: starter project creation endpoint.
- `routes_search.py`: document search and embedding rebuild endpoints.
- `routes_sources.py`: available source and CLI discovery.

### `backend/controllers/`

- thin HTTP-facing adapters around orchestration or local data access.
- `IdeaController` is the most important controller because it bridges DB records to frontend cards/details.

### `backend/services/`

- `pipeline_orchestration_service.py`: central orchestration service for long-running research flows.
- `reddit_service.py`, `hackernews_service.py`, `rss_service.py`: current normalized source stubs.
- `prompt_builder.py`, `text_cleaner.py`: small helpers used by agents.

### `backend/pipelines/`

- `research_pipeline.py`: collector -> extractor -> cluster.
- `idea_pipeline.py`: research pipeline -> idea generation -> scoring.
- `scoring_pipeline.py`: scoring wrapper.

### `backend/agents/`

- `collector_agent.py`: aggregates source connectors.
- `extractor_agent.py`: normalizes problem statements.
- `cluster_agent.py`: placeholder clustering.
- `idea_generator_agent.py`: placeholder idea generation via local LLM client stub.
- `idea_scoring_agent.py`: deterministic scoring scaffold.
- `report_agent.py`: writes markdown reports.
- `runner_agent.py`: detects local AI CLIs.

### `backend/jobs/`

- `job_repository.py`: job rows and event writes.
- `job_service.py`: enqueue, fetch, execute.
- `worker.py`: single in-process polling worker thread.

### `backend/search/`

- `embedding_service.py`: hash-based local embeddings.
- `vector_index.py`: JSON-backed on-disk vector store.
- `retriever.py`: chunking, collection management, rebuild, and query flow.
- `similarity.py`: cosine similarity.

### `backend/database/`

- `schema.sql`: source of truth for the SQLite schema.
- `migrations.py`: schema application and legacy backfill.
- `seed_data.py`: bootstrap sample ideas and model registry entries.
- `db.py`: SQLModel engine/session setup.

### `backend/models/`

- SQLModel table mappings for documents, ideas, jobs, runs, vectors, projects, sources, models, and clusters.

### Runtime data/output folders

- `backend/data/ailab.db`: SQLite database file.
- `data/vector_index/`: JSON vector files for local search.
- `idea_reports/`: generated markdown reports.
- `projects/`: generated starter project folders.

## `ailab/frontend/`

- `src/main.jsx`: SPA entrypoint.
- `src/App.jsx`: shared shell and routes.
- `src/pages/Dashboard.jsx`: dashboard data loading, discovery trigger, job polling, project creation.
- `src/pages/IdeasPage.jsx`, `IdeaDetail.jsx`, `ProjectsPage.jsx`, `SettingsPage.jsx`: route pages.
- `src/api/*.js`: fetch wrappers; now use same-origin `/api`.
- `dist/`: production build served by FastAPI.
- `vite.config.js`: dev server config for local development only.

## `ailab/launcher/`

- `launcher.py`: desktop production entrypoint.
- `start_server.py`: backend process startup and readiness checks.
- `desktop_window.py`: `pywebview` window creation.
- `detect_ai_cli.py`: CLI detection.
- `open_browser.py`: legacy browser helper, no longer used by the desktop runtime.

## `project_system/`

- `PROJECT_CONTEXT.md`: high-level purpose and architecture.
- `SYSTEM_MAP.md`: repository map.
- `SESSION_STATE.md`: current implementation state.
- `NEXT_STEPS.md`: minimal future work list.
- `RESUME_CODEX_PROMPT.md`: reusable prompt for future Codex sessions.
- `reconstruct_context.py`: quick repository scanner/summary script.
