@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: Get the current folder path of the script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo [*] Creating Python virtual environment in: %SCRIPT_DIR%ytdlp
:: Using --clear ensures fresh paths if the folder was moved to a new PC
python -m venv ytdlp --clear
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [*] Activating virtual environment...
:: Ensure the correct activation script is called
call "%SCRIPT_DIR%ytdlp\Scripts\activate.bat"

echo [*] Upgrading pip...
python -m pip install --upgrade pip

echo [*] Installing yt-dlp and requests...
:: Installing dependencies inside the isolated environment
python -m pip install yt-dlp requests

echo.
echo [SUCCESS] Setup completed!
echo --------------------------------------------------
echo Status: Portable Environment Ready
echo Location: %SCRIPT_DIR%ytdlp
echo --------------------------------------------------
echo.
echo To run your Python script now, use:
echo python your_script_name.py
echo.

pause
