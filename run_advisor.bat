@echo off
echo Starting Enhanced Gaming Advisor...
python enhanced_gaming_advisor.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting application. Please make sure all dependencies are installed.
    echo Run install_dependencies.bat first if you haven't already.
    pause
    exit /b 1
)