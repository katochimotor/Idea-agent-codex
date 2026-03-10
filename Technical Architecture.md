AI Idea Research Lab
1. Общая архитектура системы

Система строится как локальное desktop-приложение с web-интерфейсом.

Общий поток выглядит так:

Desktop Launcher
        ↓
Local API Server
        ↓
AI Agent System
        ↓
Idea Processing Pipeline
        ↓
Local Database
        ↓
Web Dashboard

Пользователь взаимодействует только с дашбордом.

2. Основные компоненты системы

Система состоит из пяти ключевых слоев.

Interface Layer
Application Layer
AI Agent Layer
Data Layer
System Layer
3. Interface Layer (UI)

Это пользовательский интерфейс.

Он работает как локальный веб-сайт.

Основные элементы:

Dashboard
Idea Cards
Mind Map
Analytics Graphs
Project Builder

UI должен быть динамическим.

Технологии

React

Vite

React Flow

D3.js

4. Application Layer

Это основной сервер приложения.

Он принимает команды пользователя и запускает процессы анализа.

Основные модули
idea_controller
analysis_controller
project_controller
dashboard_controller
Пример API
GET /ideas
POST /discover
GET /idea/{id}
POST /build_project
5. AI Agent Layer

Это ядро системы.

Здесь находятся агенты, которые выполняют анализ.

Система строится как pipeline агентов.

6. Pipeline анализа идей

Обработка идей происходит по этапам.

Data Collector
        ↓
Problem Extractor
        ↓
Problem Clustering
        ↓
Idea Generator
        ↓
Idea Scoring
        ↓
Visualization Builder
7. Data Collector

Этот модуль собирает данные.

Источники:

Reddit API
Hacker News API
RSS feeds
Manual input

Результат:

raw_discussions
8. Problem Extractor

Задача модуля — найти проблемы пользователей.

Пример текста:

"I wish there was a tool that..."

Модуль выделяет:

problem_statement
9. Problem Clustering

После извлечения проблем система объединяет похожие проблемы.

Пример:

AI prompt management
AI prompt organization
AI prompt library

объединяются в один кластер.

10. Idea Generator

На основе проблем генерируются идеи продуктов.

Например:

Problem:
developers struggle with prompt management

Idea:
Prompt library SaaS

Генерируются два типа идей:

идеи из обсуждений

основаны на реальных проблемах.

идеи от ИИ

генерируются на основе трендов.

11. Idea Scoring

Каждая идея получает оценку.

Метрики:

Market demand
Competition
Difficulty
Monetization

Формула оценки:

score = weighted_average
12. Visualization Builder

Этот модуль строит визуальные структуры.

Например:

Mind Map
niche
 ├ problem
 │  ├ idea
 │  ├ idea
13. Data Layer

Все данные хранятся локально.

Используется база:

SQLite
14. Основные таблицы
ideas
id
title
summary
score
created_at
problems
id
text
source
cluster_id
sources
id
platform
url
timestamp
projects
id
idea_id
folder_path
created_at
15. Project Builder

Когда пользователь выбирает идею, система создаёт проект.

Структура:

projects/

   idea_name/

      README.md
      architecture.md
      tech_stack.md
      mvp_plan.md
      starter_prompt.md
      run.bat
16. Runner Agent

Этот агент может запускать генерацию проекта.

Он проверяет:

qwen CLI
gpt CLI
claude CLI

После этого предлагает:

generate code
17. Система логирования

Каждый этап pipeline логируется.

Пример:

collector started
collector finished
extractor started
extractor finished

Логи сохраняются в:

logs/ailab.log
18. Поток данных (data flow)

Полный поток обработки выглядит так:

User clicks "Find ideas"
        ↓
Data Collector gathers discussions
        ↓
Problem Extractor detects problems
        ↓
Clustering groups problems
        ↓
Idea Generator creates product ideas
        ↓
Idea Scoring evaluates ideas
        ↓
Ideas stored in database
        ↓
Dashboard updates
19. Архитектура запуска

Приложение запускается так:

launcher.exe
      ↓
start backend
      ↓
start frontend
      ↓
open browser
20. Минимальная архитектура MVP

Для первой версии достаточно:

collector
idea generator
dashboard
project builder
21. Масштабирование

Если продукт будет расти, можно добавить:

vector database
trend analysis
GitHub integration
code generation agent
Итог

Архитектура AI Idea Research Lab строится вокруг агентного pipeline анализа идей, который соединяет:

сбор данных

анализ проблем

генерацию идей

оценку

запуск проекта

Это позволяет пользователю быстро переходить от исследования рынка к созданию продукта.