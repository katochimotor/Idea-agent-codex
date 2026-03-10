from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "ailab"
EXCLUDED_PARTS = {"node_modules", "dist", "__pycache__", ".git", ".venv"}


def is_relevant(path: Path) -> bool:
    return not any(part in EXCLUDED_PARTS for part in path.parts)


def list_files(base: Path, suffixes: tuple[str, ...] = (".py", ".js", ".jsx", ".md", ".bat")) -> list[Path]:
    if not base.exists():
        return []
    return sorted(
        [
            path.relative_to(ROOT)
            for path in base.rglob("*")
            if path.is_file() and is_relevant(path) and path.suffix.lower() in suffixes
        ]
    )


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def print_group(label: str, paths: list[Path]) -> None:
    print(f"{label}: {len(paths)} files")
    for path in paths[:12]:
        print(f"  - {path.as_posix()}")
    if len(paths) > 12:
        print(f"  ... ({len(paths) - 12} more)")


def main() -> None:
    print("AI Idea Research Lab context reconstruction")
    print(f"Repository root: {ROOT}")

    print_section("Entry Points")
    entry_points = [
        ROOT / "start_app.bat",
        ROOT / "start.bat",
        ROOT / "build_exe.bat",
        APP_ROOT / "launcher" / "launcher.py",
        APP_ROOT / "backend" / "main.py",
        APP_ROOT / "backend" / "app.py",
        APP_ROOT / "frontend" / "src" / "main.jsx",
    ]
    for entry in entry_points:
        status = "present" if entry.exists() else "missing"
        print(f"- {entry.relative_to(ROOT).as_posix()} [{status}]")

    print_section("Important Modules")
    groups = {
        "Backend API": list_files(APP_ROOT / "backend" / "api"),
        "Controllers": list_files(APP_ROOT / "backend" / "controllers"),
        "Jobs": list_files(APP_ROOT / "backend" / "jobs"),
        "Pipelines": list_files(APP_ROOT / "backend" / "pipelines"),
        "Search": list_files(APP_ROOT / "backend" / "search"),
        "Database": list_files(APP_ROOT / "backend" / "database"),
        "Models": list_files(APP_ROOT / "backend" / "models"),
        "Frontend": list_files(APP_ROOT / "frontend" / "src"),
        "Launcher": list_files(APP_ROOT / "launcher"),
        "Project System": list_files(ROOT / "project_system"),
    }
    for label, paths in groups.items():
        print_group(label, paths)

    print_section("Architecture Summary")
    print("Desktop runtime:")
    print("- start_app.bat/start.bat -> launcher.py -> FastAPI -> pywebview window")
    print("- FastAPI serves /api routes and the built React frontend from frontend/dist")
    print("- Startup runs DB migrations, seeds sample data, and starts the background worker")
    print("Data and orchestration:")
    print("- SQLite stores jobs, ideas, documents, reports, vectors, and pipeline lineage")
    print("- BackgroundJobWorker polls queued jobs and executes them through PipelineOrchestrationService")
    print("- VectorSearchService chunks documents, builds embeddings, writes JSON vector files, and serves search results")
    print("Frontend behavior:")
    print("- Dashboard enqueues discovery jobs, polls for completion, and reloads ideas")
    print("- API clients use same-origin /api requests for desktop/static mode")


if __name__ == "__main__":
    main()
