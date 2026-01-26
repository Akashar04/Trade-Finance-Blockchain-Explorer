@echo off
REM Quick start script for Trade Finance Frontend (Windows)

echo ================================
echo Trade Finance Frontend Setup
echo ================================
echo.

REM Check if Node is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo X Node.js is not installed. Please install Node.js 16+
    pause
    exit /b 1
)

echo + Node.js found: 
node --version
echo + npm found: 
npm --version
echo.

REM Navigate to frontend
cd /d "%~dp0\frontend" || exit /b 1

REM Install dependencies
echo Installing dependencies...
call npm install

REM Start development server
echo.
echo ================================
echo Starting development server...
echo ================================
echo.
echo Frontend will open at: http://localhost:3000
echo Backend API at: http://localhost:8000
echo API Docs at: http://localhost:8000/docs
echo.

call npm start
pause
