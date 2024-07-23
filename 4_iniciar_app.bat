@echo off

:: Activate virtual environment
call .venv\Scripts\activate

:: Run Flask application
waitress-serve app:flask_app


if %errorlevel% neq 0 (
    echo Error occurred. Press any key to exit...
    pause >nul
)