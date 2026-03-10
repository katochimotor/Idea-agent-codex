import os
import sys
from pathlib import Path

from detect_ai_cli import detect_ai_cli
from desktop_window import open_desktop_window
from start_server import is_port_open, start_backend, wait_for_http


def resolve_root_dir() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root).resolve()
    return Path(__file__).resolve().parents[1]


ROOT_DIR = resolve_root_dir()
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"


def ensure_project_python() -> None:
    current_python = Path(sys.executable).resolve()
    if VENV_PYTHON.exists() and current_python != VENV_PYTHON.resolve():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve())])


def main() -> None:
    ensure_project_python()
    print("Detected AI CLI:", ", ".join(detect_ai_cli()) or "none")

    backend = None
    backend_ready = is_port_open("127.0.0.1", 8000)

    if not backend_ready:
        print("Starting backend on http://127.0.0.1:8000")
        backend = start_backend(ROOT_DIR)
        backend_ready = wait_for_http("http://127.0.0.1:8000/health", timeout_seconds=20.0)
    else:
        print("Backend is already running on http://127.0.0.1:8000")

    if not backend_ready:
        print("Backend did not become ready.")
        sys.exit(1)

    try:
        print("Opening desktop window: http://127.0.0.1:8000")
        open_desktop_window("http://127.0.0.1:8000", title="AI Idea Research Lab")
    except KeyboardInterrupt:
        pass
    finally:
        if backend is not None and backend.poll() is None:
            backend.terminate()
            try:
                backend.wait(timeout=5)
            except Exception:
                backend.kill()
        sys.exit(0)


if __name__ == "__main__":
    main()
