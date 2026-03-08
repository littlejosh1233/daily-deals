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
echo Pushing updates to live website...
git add docs/index.html
git commit -m "Auto-update daily deals %DATE%"
git push origin main

echo.
echo ===================================
echo Done! The website has been updated live.
echo ===================================
pause
