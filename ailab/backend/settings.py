import os
import sys
from pathlib import Path

from pydantic import BaseModel


def _resolve_runtime_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _resolve_bundle_dir(runtime_dir: Path) -> Path:
    env_bundle_dir = os.getenv("AILAB_BUNDLE_DIR")
    if env_bundle_dir:
        return Path(env_bundle_dir).resolve()
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root).resolve()
    return runtime_dir


RUNTIME_DIR = _resolve_runtime_dir()
BUNDLE_DIR = _resolve_bundle_dir(RUNTIME_DIR)


class Settings(BaseModel):
    app_name: str = "AI Idea Research Lab"
    api_prefix: str = "/api"
    runtime_dir: Path = RUNTIME_DIR
    bundle_dir: Path = BUNDLE_DIR
    database_url: str = f"sqlite:///{(RUNTIME_DIR / 'backend' / 'data' / 'ailab.db').as_posix()}"
    data_dir: Path = RUNTIME_DIR / "data"
    vector_index_dir: Path = RUNTIME_DIR / "data" / "vector_index"
    docstore_dir: Path = RUNTIME_DIR / "data" / "docstore"
    reports_dir: Path = RUNTIME_DIR / "idea_reports"
    projects_dir: Path = RUNTIME_DIR / "projects"
    templates_dir: Path = BUNDLE_DIR / "templates"
    frontend_dist_dir: Path = BUNDLE_DIR / "frontend" / "dist"
    log_file: Path = RUNTIME_DIR / "backend" / "logs" / "ailab.log"
    worker_poll_interval_seconds: float = 1.5
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000


settings = Settings()
