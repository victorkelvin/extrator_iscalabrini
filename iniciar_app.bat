@echo off

:: Activate virtual environment
call .venv\Scripts\activate

:: Run Flask application
waitress-serve app:flask_app