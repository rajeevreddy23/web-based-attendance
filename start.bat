@echo off
echo ======================================================================
echo  Starting Web-Based Period-Wise Student Attendance Management System
echo ======================================================================

echo.
echo [*] Launching FastAPI Backend Server on http://localhost:8000...
start "Attendance Backend (FastAPI)" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

echo.
echo [*] Launching Next.js Frontend on http://localhost:3000...
start "Attendance Frontend (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ======================================================================
echo  System is Starting!
echo  - Frontend URL:  http://localhost:3000
echo  - Backend Docs:  http://localhost:8000/api/v1/docs
echo.
echo  Default Logins:
echo    Admin:   admin@college.edu      / Admin@123
echo    Faculty: dr.sharma@college.edu  / Faculty@123
echo ======================================================================
echo.
timeout /t 5 >nul
start http://localhost:3000
