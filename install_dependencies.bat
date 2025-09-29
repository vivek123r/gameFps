@echo off
echo Installing required dependencies for Modern Gaming Advisor...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error installing dependencies. Please make sure Python is installed correctly.
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!
echo.
echo Run the application with:
echo    python enhanced_gaming_advisor.py
echo.
echo Or run the standalone game library with:
echo    python game_library_launcher.py
echo.
pause