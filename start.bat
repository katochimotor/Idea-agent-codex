@echo off
setlocal

call "%~dp0start_app.bat"
if errorlevel 1 (
    exit /b %errorlevel%
)
