# Resume Codex Prompt

Use this prompt at the start of a new Codex session for this repository:

```md
You are resuming work on this repository.

First:
- read `README.md`
- read `SESSION_REPORT.md`
- read every file in `/project_system`
- run `ailab\.venv\Scripts\python.exe project_system\reconstruct_context.py`
- check `git status`
- scan the repository structure again from the root
- rebuild understanding of the backend, frontend, launcher, database, pipeline orchestration, opportunity engine, vector search, and async job system

Then:
- treat `/project_system` as the persistent project memory
- do not regenerate or replace existing memory files unless the task explicitly requires updating them
- preserve the current desktop runtime architecture:
  - FastAPI backend
  - React build served as static files
  - pywebview desktop launcher
- preserve the current pipeline architecture:
  - collect discussions
  - extract problems
  - cluster problems
  - opportunity analysis
  - generate ideas
  - score ideas
  - save results
- continue development from the current implementation state instead of re-planning from scratch

Before editing:
- identify the current entry points
- confirm how startup, job execution, opportunity analysis, search, and frontend polling currently work
- confirm the current repository state from `git status`
- confirm the latest completed work from `SESSION_REPORT.md`
- check whether the requested task affects runtime, persistence, or packaging

When done:
- update `/project_system` only if the architecture or implementation state has materially changed
```

## Short User Prompt

If the user wants to resume quickly in natural language, they can write:

`Продолжаем AI Idea Research Lab с текущего SESSION_REPORT. Сначала прочитай README.md, SESSION_REPORT.md и всё в project_system, затем запусти reconstruct_context.py, проверь git status и продолжи с opportunity engine / dashboard UX с места остановки.`
