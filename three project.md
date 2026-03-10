Полное дерево проекта
AI Idea Research Lab
ailab/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── config.yaml
│
├── launcher/
│   ├── launcher.py
│   ├── start_server.py
│   ├── open_browser.py
│   └── detect_ai_cli.py
│
├── backend/
│   │
│   ├── main.py
│   ├── app.py
│   ├── settings.py
│   ├── logger.py
│   │
│   ├── api/
│   │   ├── routes_ideas.py
│   │   ├── routes_projects.py
│   │   ├── routes_dashboard.py
│   │   └── routes_sources.py
│   │
│   ├── controllers/
│   │   ├── idea_controller.py
│   │   ├── project_controller.py
│   │   ├── analysis_controller.py
│   │   └── dashboard_controller.py
│   │
│   ├── agents/
│   │   ├── collector_agent.py
│   │   ├── extractor_agent.py
│   │   ├── cluster_agent.py
│   │   ├── idea_generator_agent.py
│   │   ├── idea_scoring_agent.py
│   │   ├── report_agent.py
│   │   └── runner_agent.py
│   │
│   ├── pipelines/
│   │   ├── idea_pipeline.py
│   │   ├── research_pipeline.py
│   │   └── scoring_pipeline.py
│   │
│   ├── services/
│   │   ├── reddit_service.py
│   │   ├── hackernews_service.py
│   │   ├── rss_service.py
│   │   ├── text_cleaner.py
│   │   └── prompt_builder.py
│   │
│   ├── ai/
│   │   ├── llm_client.py
│   │   ├── prompt_templates.py
│   │   └── embeddings.py
│   │
│   ├── models/
│   │   ├── idea_model.py
│   │   ├── problem_model.py
│   │   ├── source_model.py
│   │   └── project_model.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   ├── schema.sql
│   │   ├── migrations.py
│   │   └── seed_data.py
│   │
│   ├── utils/
│   │   ├── idea_formatter.py
│   │   ├── score_calculator.py
│   │   ├── file_writer.py
│   │   └── slug_generator.py
│   │
│   └── logs/
│       └── ailab.log
│
│
├── frontend/
│   │
│   ├── package.json
│   ├── vite.config.js
│   │
│   ├── public/
│   │   └── logo.svg
│   │
│   └── src/
│       │
│       ├── main.jsx
│       ├── App.jsx
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── IdeasPage.jsx
│       │   ├── IdeaDetail.jsx
│       │   ├── ProjectsPage.jsx
│       │   └── SettingsPage.jsx
│       │
│       ├── components/
│       │   ├── IdeaCard.jsx
│       │   ├── IdeaList.jsx
│       │   ├── IdeaScore.jsx
│       │   ├── GenerateButton.jsx
│       │   ├── MindMapView.jsx
│       │   ├── TrendGraph.jsx
│       │   ├── Sidebar.jsx
│       │   └── Topbar.jsx
│       │
│       ├── visualizations/
│       │   ├── mindmap.jsx
│       │   ├── score_chart.jsx
│       │   └── niche_graph.jsx
│       │
│       ├── api/
│       │   ├── ideas_api.js
│       │   ├── projects_api.js
│       │   └── dashboard_api.js
│       │
│       └── styles/
│           ├── global.css
│           └── dashboard.css
│
│
├── idea_reports/
│   └── sample_idea.md
│
├── projects/
│
│   └── example_project/
│       ├── README.md
│       ├── architecture.md
│       ├── tech_stack.md
│       ├── mvp_plan.md
│       ├── starter_prompt.md
│       ├── run.bat
│       └── run.sh
│
│
├── templates/
│   ├── idea_report_template.md
│   ├── project_readme_template.md
│   └── starter_prompt_template.md
│
│
├── scripts/
│   ├── install_env.bat
│   ├── install_env.sh
│   ├── run_dev_server.py
│   └── build_exe.py
│
│
└── build/
    ├── packaging_config.toml
    └── installer_script.py
Как работает эта структура
launcher

Запускает приложение.

launcher.py

делает:

start backend
start frontend
open browser
backend

Это сервер приложения.

Там:

API

AI-агенты

pipeline анализа

agents

Самая важная папка.

Там находятся агенты:

collector_agent
extractor_agent
cluster_agent
idea_generator
idea_scoring

Это и есть агентная архитектура продукта.

pipelines

Здесь строится последовательность обработки:

collect data
extract problems
cluster problems
generate ideas
score ideas
services

Работа с источниками данных.

reddit_service
rss_service
hackernews_service
ai

Интеграция с нейросетями.

llm_client
prompt_templates
embeddings
database

Хранение идей.

SQLite

таблицы:

ideas
problems
sources
projects
frontend

React интерфейс.

Основные страницы:

Dashboard
Ideas
Projects
Settings
visualizations

Там находится:

mindmap
trend graphs
score charts
projects

Когда пользователь нажимает Создать проект,
сюда создаётся папка нового продукта.

templates

Шаблоны:

idea report
README
starter prompt
scripts

Скрипты установки.

install_env
run_dev
build_exe
build

Упаковка приложения.

Можно собрать:

Windows .exe
Почему эта структура хороша

Она:

модульная

понятная для AI-агентов

масштабируемая

удобна для solo-разработчика.

Теперь очень важный момент

Если дать это дерево проекта + мастер-промпт агенту кодирования,
он сможет почти полностью сгенерировать проект автоматически.

Следующий шаг (пункт 4) будет самым важным для реальной разработки.

Я покажу:

как должен выглядеть UX-макет интерфейса

главный экран

mind map

карточки идей

кнопки генерации

Это сильно влияет на то, насколько инструмент будет приятным и удобным.