# Resume Codex Prompt

Use this prompt at the start of a new Codex session for this repository:

```md
You are resuming work on this repository.

First:
- read every file in `/project_system`
- run `ailab\.venv\Scripts\python.exe project_system\reconstruct_context.py`
- check `git status`
- scan the repository structure again from the root
- rebuild understanding of the backend, frontend, launcher, database, pipeline orchestration, vector search, and async job system

Then:
- treat `/project_system` as the persistent project memory
- do not regenerate or replace existing memory files unless the task explicitly requires updating them
- preserve the current desktop runtime architecture:
  - FastAPI backend
  - React build served as static files
  - pywebview desktop launcher
- continue development from the current implementation state instead of re-planning from scratch

Before editing:
- identify the current entry points
- confirm how startup, job execution, search, and frontend polling currently work
- confirm the current repository state from `git status`
- check whether the requested task affects runtime, persistence, or packaging

When done:
- update `/project_system` only if the architecture or implementation state has materially changed
```
