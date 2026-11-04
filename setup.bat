@echo off
echo ======================================================================
echo  Web-Based Period-Wise Attendance Management - 1-Click First-Time Setup
echo ======================================================================

echo.
echo [1/2] Setting up Python Backend Virtual Environment...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [2/2] Installing Frontend Dependencies (Node.js)...
cd ..\frontend
call npm install

echo.
echo ======================================================================
echo  Setup Completed Successfully!
echo  You can now start the system anytime by double-clicking "start.bat"
echo ======================================================================
pause
