@echo off
echo Starting Game Library...
python game_library_launcher.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting game library. Please make sure all dependencies are installed.
    echo Run install_dependencies.bat first if you haven't already.
    pause
    exit /b 1
)