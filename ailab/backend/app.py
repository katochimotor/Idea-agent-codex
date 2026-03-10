from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.api.routes_dashboard import router as dashboard_router
from backend.api.routes_ideas import router as ideas_router
from backend.api.routes_jobs import router as jobs_router
from backend.api.routes_opportunities import router as opportunities_router
from backend.api.routes_projects import router as projects_router
from backend.api.routes_search import router as search_router
from backend.api.routes_settings import router as settings_router
from backend.api.routes_sources import router as sources_router
from backend.database.db import engine, init_db
from backend.database.seed_data import seed_ideas
from backend.jobs.worker import BackgroundJobWorker
from backend.logger import logger
from backend.settings import settings
from sqlmodel import Session


def _register_frontend(app: FastAPI) -> None:
    dist_dir = settings.frontend_dist_dir
    index_file = dist_dir / "index.html"
    if not index_file.exists():
        return

    dist_root = dist_dir.resolve()

    @app.get("/", include_in_schema=False)
    def serve_root():
        return FileResponse(index_file)

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str):
        if not full_path or full_path.startswith("api"):
            return FileResponse(index_file)

        candidate = (dist_dir / Path(full_path)).resolve()
        try:
            candidate.relative_to(dist_root)
        except ValueError:
            return FileResponse(index_file)

        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index_file)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ideas_router, prefix=settings.api_prefix)
    app.include_router(jobs_router, prefix=settings.api_prefix)
    app.include_router(opportunities_router, prefix=settings.api_prefix)
    app.include_router(projects_router, prefix=settings.api_prefix)
    app.include_router(dashboard_router, prefix=settings.api_prefix)
    app.include_router(search_router, prefix=settings.api_prefix)
    app.include_router(settings_router, prefix=settings.api_prefix)
    app.include_router(sources_router, prefix=settings.api_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        logger.info("backend startup")
        init_db()
        with Session(engine) as session:
            seed_ideas(session)
        worker = BackgroundJobWorker()
        worker.start()
        app.state.background_worker = worker

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        worker = getattr(app.state, "background_worker", None)
        if worker is not None:
            worker.stop()

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    _register_frontend(app)

    return app
