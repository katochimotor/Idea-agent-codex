# AI Idea Research Lab

Это главный файл-памятка для проекта. Если вы открыли папку и забыли, что запускать, начинайте отсюда.

## С чего начать

Если вы просто хотите проверить, как работает проект:

1. Запустите `start_app.bat`.
2. Дождитесь открытия окна приложения.
3. Если окно не открылось, прочитайте сообщение в консоли: там будет написано, чего не хватает.

## Самый короткий путь

- `start_app.bat` — основной запуск приложения.
- `start.bat` — короткий запасной запуск, он просто вызывает `start_app.bat`.
- `build_exe.bat` — сборка `launcher.exe` через PyInstaller.

## Если проект не запускается

Проверьте по порядку:

1. Есть ли виртуальное окружение `.venv` внутри `ailab`.
2. Если его нет, запустите `ailab\scripts\install_env.bat`.
3. Есть ли собранный frontend в `ailab\frontend\dist`.
4. Если папки `dist` нет, откройте терминал в `ailab\frontend` и выполните `npm run build`.
5. После этого снова запустите `start_app.bat`.

## Что делает проект

Проект запускает локальное desktop-приложение:

- FastAPI работает как backend.
- React интерфейс собран в статические файлы.
- Backend сам раздаёт этот интерфейс.
- `pywebview` открывает всё это как отдельное окно приложения.

То есть проект больше не зависит от Vite dev server и не требует ручного открытия браузера для обычного запуска.

## Главные файлы в корне проекта

- `README.md` — этот файл. Быстрая памятка для человека.
- `SESSION_REPORT.md` — краткий отчёт о последних завершённых изменениях за текущую/последнюю сессию.
- `start_app.bat` — основной файл запуска приложения.
- `start.bat` — короткий запуск-обёртка.
- `build_exe.bat` — сборка `launcher.exe`.
- `create_desktop_shortcut.bat` — создание ярлыка на рабочем столе.
- `create_desktop_shortcut.ps1` — PowerShell-версия создания ярлыка.
- `.gitignore` — какие файлы git не должен сохранять.

## Папки в корне проекта

- `ailab` — основной код приложения.
- `project_system` — память проекта для будущих сессий Codex.
- `scripts` — быстрые git-команды для разработки.

## Что находится внутри `ailab`

### Запуск

- `ailab\launcher\launcher.py` — главный Python-лаунчер desktop-приложения.
- `ailab\launcher\desktop_window.py` — открывает окно `pywebview`.
- `ailab\launcher\start_server.py` — запускает FastAPI и проверяет, что сервер поднялся.
- `ailab\launcher\detect_ai_cli.py` — проверяет наличие локальных AI CLI.

### Backend

- `ailab\backend\main.py` — точка входа backend.
- `ailab\backend\app.py` — собирает FastAPI-приложение, API-маршруты и раздачу frontend.
- `ailab\backend\settings.py` — основные пути и настройки runtime.
- `ailab\backend\database\schema.sql` — структура SQLite базы.
- `ailab\backend\jobs\worker.py` — фоновый worker для async jobs.
- `ailab\backend\services\pipeline_orchestration_service.py` — основная orchestration-логика.
- `ailab\backend\search\retriever.py` — локальный vector search.

### Frontend

- `ailab\frontend\src` — исходники интерфейса React.
- `ailab\frontend\dist` — готовая production-сборка интерфейса.
- `ailab\frontend\package.json` — команды frontend.
- `ailab\frontend\vite.config.js` — конфигурация Vite для dev-режима.

### Важные служебные папки

- `ailab\templates` — шаблоны для отчётов и проектных файлов.
- `ailab\projects` — сгенерированные проектные папки.
- `ailab\idea_reports` — markdown-отчёты по идеям.
- `ailab\data\vector_index` — локальный векторный индекс.
- `ailab\backend\data` — SQLite база приложения.

## Что находится в `project_system`

Эти файлы нужны в первую очередь не для ручного запуска, а для восстановления контекста проекта:

- `project_system\PROJECT_CONTEXT.md` — что это за проект и как он работает.
- `project_system\SYSTEM_MAP.md` — карта структуры проекта.
- `project_system\SESSION_STATE.md` — текущее состояние реализации.
- `project_system\NEXT_STEPS.md` — краткий список следующих задач.
- `project_system\RESUME_CODEX_PROMPT.md` — prompt для будущих сессий Codex.
- `project_system\reconstruct_context.py` — быстрый сканер проекта.

## Что находится в `scripts`

- `scripts\dev_commit_push.bat` — `git add`, `git commit`, `git push`.
- `scripts\dev_commit_push.ps1` — PowerShell-версия той же команды.
- `scripts\dev_snapshot.bat` — обновляет контекст проекта, затем делает commit и push.

## Как перезапускать проект

Если вы просто хотите снова открыть приложение:

1. Закройте текущее окно приложения, если оно уже открыто.
2. Запустите `start_app.bat`.

Если вы меняли frontend:

1. Откройте терминал в `ailab\frontend`.
2. Выполните `npm run build`.
3. Потом снова запустите `start_app.bat`.

Если вы меняли backend или launcher:

1. Просто снова запустите `start_app.bat`.
2. Если нужно собрать отдельный exe, потом запустите `build_exe.bat`.

## Как собрать exe

1. Убедитесь, что проект запускается через `start_app.bat`.
2. Убедитесь, что `ailab\frontend\dist` существует.
3. Запустите `build_exe.bat`.
4. Готовая сборка появится в `ailab\dist\launcher`.

## Что открывать, если забыли

Если забыли, что делать:

- для запуска приложения — `start_app.bat`
- для сборки exe — `build_exe.bat`
- для понимания структуры — `README.md`
- для понимания последних изменений — `SESSION_REPORT.md`
- для восстановления контекста разработки — `project_system\RESUME_CODEX_PROMPT.md`
