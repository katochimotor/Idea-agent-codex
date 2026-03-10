@echo off
py -3.13 -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
cd frontend
npm install
