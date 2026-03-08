@echo off
echo ===================================
echo Starting Automated Affiliate Build
echo ===================================
echo %DATE% %TIME%

cd /d "%~dp0"

echo Activating Python Environment...
call venv\Scripts\activate.bat

echo Generating fresh HTML...
python generate_site.py

echo.
echo ===================================
echo Done! 
echo Next step: To fully automate this, add git commit/push commands here.
echo Set this script to run daily in Windows Task Scheduler.
echo ===================================
pause
