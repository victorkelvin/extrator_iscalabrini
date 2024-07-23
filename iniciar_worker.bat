@echo off

:: Activate virtual environment
call .venv\Scripts\activate

:: Run Flask application
celery -A app worker --pool=solo -l INFO

if %errorlevel% neq 0 (
    echo Error occurred. Press any key to exit...
    pause >nul
)