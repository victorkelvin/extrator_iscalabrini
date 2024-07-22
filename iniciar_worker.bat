@echo off

:: Activate virtual environment
call .venv\Scripts\activate

:: Run Flask application
celery -A app worker --pool=solo -l INFO