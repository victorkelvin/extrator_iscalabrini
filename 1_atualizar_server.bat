@echo off

:: Set the repository URL and local path
set REPO_URL=https://github.com/victorkelvin/extrator_iscalabrini.git
::set LOCAL_PATH=C:\Path\To\Your\Repo

:: Change to the local repository path
::cd /d %LOCAL_PATH%

:: Checkout the repository if it doesn't exist
if not exist .git (
    git init
    git remote add origin %REPO_URL%
    git pull origin main
) else (
    :: Update the repository if it already exists
    git pull origin main
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt


if %errorlevel% neq 0 (
    echo Error occurred. Press any key to exit...
    pause >nul
)