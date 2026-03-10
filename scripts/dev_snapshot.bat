@echo off
setlocal

ailab\.venv\Scripts\python.exe project_system\reconstruct_context.py
git add .
git commit -m "snapshot: project context updated"
git push
