@echo off
REM Quick run script for Windows - assumes setup is already done

echo.
echo 🌍 AI Travel Platform
echo.
echo Select UI to launch:
echo 1) Web UI (Modern responsive interface)
echo 2) Gradio UI (Simple interactive interface)
echo.

set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting Web UI on http://localhost:8080
    python main.py --ui web
) else if "%choice%"=="2" (
    echo.
    echo 🚀 Starting Gradio UI
    python main.py --ui gradio
) else (
    echo Invalid choice
    exit /b 1
)
