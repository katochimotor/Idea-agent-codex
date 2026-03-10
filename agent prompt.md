You are a senior software architect, full-stack developer, and AI systems engineer.

Your task is to build a working MVP application called:

AI Idea Research Lab

The full product specification is provided in a Markdown document.

Your job is to:

1. parse the specification
2. design the architecture
3. generate the full codebase
4. create a runnable local application

The application must run locally on Windows.

-----------------------------------------------------

IMPORTANT LANGUAGE RULE

All user-facing text must be generated in Russian.

This includes:

UI labels
buttons
notifications
idea reports
README files
project descriptions

English may only be used in source code.

-----------------------------------------------------

GOAL OF THE APPLICATION

Create a tool that helps founders discover startup ideas automatically.

The system must:

discover problems
generate ideas
analyze ideas
visualize ideas
generate project structures

-----------------------------------------------------

PROJECT STRUCTURE

Generate a project with this structure:

ailab/
 backend/
 frontend/
 agents/
 pipelines/
 database/
 templates/
 projects/
 scripts/

-----------------------------------------------------

TECH STACK

Backend
Python
FastAPI

Frontend
React
Vite

Database
SQLite

Visualization
React Flow

Packaging
PyInstaller or Tauri

-----------------------------------------------------

SYSTEM MODULES

The system must contain these modules:

Research Engine
Problem Extractor
Idea Generator
Idea Analyzer
Visualization Engine
Project Builder

-----------------------------------------------------

IDEA PIPELINE

Implement this processing pipeline:

Collect discussions
↓
Extract user problems
↓
Cluster problems
↓
Generate product ideas
↓
Score ideas
↓
Save ideas to database
↓
Display ideas in dashboard

-----------------------------------------------------

DATA SOURCES

Implement connectors for:

Reddit API
Hacker News API
RSS feeds

If API keys are not available, allow manual text input.

-----------------------------------------------------

IDEA GENERATION

The system must produce two types of ideas:

Ideas extracted from real discussions

AI-generated ideas based on trends

Each time the user presses:

"Сгенерировать ещё идеи"

the system must create 10 additional ideas.

-----------------------------------------------------

IDEA SCORING MODEL

Each idea must be evaluated with:

market demand
competition
implementation difficulty
monetization potential

Score range:

1–10

Compute a total score.

-----------------------------------------------------

UI DESIGN

The interface must include:

Dashboard
Idea Cards
Mind Map
Analytics Page
Projects Page

UI labels must be in Russian.

Example buttons:

"Найти идеи"
"Сгенерировать ещё идеи"
"Анализ идеи"
"Создать проект"

-----------------------------------------------------

PROJECT GENERATION

When the user clicks:

"Создать проект"

create a project folder.

Example:

projects/idea_name/

README.md
architecture.md
tech_stack.md
mvp_plan.md
starter_prompt.md
run.bat

-----------------------------------------------------

RUN SCRIPT

Create scripts:

run_dev_server.py
build_exe.py

run.bat must:

create virtual environment
install dependencies
start backend
start frontend

-----------------------------------------------------

EXECUTION PLAN

Follow these steps:

STEP 1
Parse the specification document.

STEP 2
Generate the project folder structure.

STEP 3
Generate backend skeleton.

STEP 4
Generate frontend skeleton.

STEP 5
Implement idea pipeline.

STEP 6
Implement database schema.

STEP 7
Connect UI to backend API.

STEP 8
Create project builder module.

STEP 9
Create example idea data.

STEP 10
Generate instructions for running the application.

-----------------------------------------------------

OUTPUT REQUIREMENTS

You must output:

project structure
generated code
installation instructions
run instructions

-----------------------------------------------------

IMPORTANT

Focus on building a working MVP first.

Avoid unnecessary complexity.

The application must run locally.

-----------------------------------------------------

Start by generating the project folder structure and backend skeleton.