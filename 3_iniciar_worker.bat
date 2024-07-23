@echo off

docker run -d --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management >> nul

timeout 10

:: Activate virtual environment
call .venv\Scripts\activate

:: Run Flask application
celery -A app worker --pool=solo -l INFO

if %errorlevel% neq 0 (
    echo Error occurred. Press any key to exit...
    pause >nul
)