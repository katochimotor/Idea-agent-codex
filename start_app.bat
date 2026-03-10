@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "APP_DIR=%ROOT_DIR%ailab"
set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"
set "LAUNCHER=%APP_DIR%\launcher\launcher.py"
set "FRONTEND_DIST=%APP_DIR%\frontend\dist\index.html"

if not exist "%APP_DIR%" (
    echo Application directory not found: "%APP_DIR%"
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo Virtual environment not found: "%PYTHON_EXE%"
    echo Run "ailab\scripts\install_env.bat" first.
    pause
    exit /b 1
)

if not exist "%LAUNCHER%" (
    echo Launcher file not found: "%LAUNCHER%"
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIST%" (
    echo Frontend production build not found: "%FRONTEND_DIST%"
    echo Run "npm run build" inside "ailab\frontend" before starting the desktop app.
    pause
    exit /b 1
)

cd /d "%APP_DIR%"
"%PYTHON_EXE%" "%LAUNCHER%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Desktop app exited with an error. Exit code: %EXIT_CODE%
    pause
    exit /b %EXIT_CODE%
)
