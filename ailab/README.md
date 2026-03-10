# AI Idea Research Lab

Local-first product idea research application with a desktop runtime.

## Stack

- Backend: Python, FastAPI, SQLite
- Frontend: React, Vite
- Desktop shell: pywebview
- Packaging: PyInstaller-ready launcher

## Structure

- `launcher/` starts the local backend and opens a desktop window
- `backend/` exposes API routes and orchestrates the research pipeline
- `frontend/` contains the Russian-language dashboard UI
- `templates/` stores report and project generation templates
- `projects/` contains generated project folders
- `project_system/` stores persistent project memory for future Codex sessions

## Desktop Runtime

The production app now runs as:

- FastAPI backend on `127.0.0.1:8000`
- built React frontend served from `frontend/dist`
- `pywebview` window opened by `launcher/launcher.py`

Primary startup script:

```bat
..\start_app.bat
```

## Development

Backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Launcher:

```bash
.venv\Scripts\python.exe launcher\launcher.py
```

Production frontend build:

```bash
cd frontend
npm run build
```

Windows setup:

```bat
scripts\install_env.bat
```
