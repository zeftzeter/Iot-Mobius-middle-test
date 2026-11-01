@echo off
setlocal

set "PROJECT_ROOT=%~dp0.."
if not defined FREEBOARD_DIR set "FREEBOARD_DIR=%PROJECT_ROOT%\freeboard-master"
set "DASHBOARD_URL=http://127.0.0.1:8004/index.html?load=jjh-sonic-dashboard.json"

if not exist "%FREEBOARD_DIR%\index.html" (
    echo [ERROR] Freeboard was not found. Set FREEBOARD_DIR or place freeboard-master in the project root.
    echo %FREEBOARD_DIR%
    pause
    exit /b 1
)

curl.exe --silent --fail --max-time 2 ^
  -H "X-M2M-RI: one-click-check" ^
  -H "X-M2M-Origin: S" ^
  -H "Accept: application/json" ^
  "http://127.0.0.1:7579/Mobius" >nul 2>&1

if errorlevel 1 (
    if not defined MOBIUS_DIR set "MOBIUS_DIR=C:\Mobius"
    if exist "%MOBIUS_DIR%\mobius.js" (
        start "Mobius" /min /D "%MOBIUS_DIR%" node mobius.js
    ) else (
        echo [WARNING] Mobius was not found. Set MOBIUS_DIR if it is installed elsewhere.
    )
)

curl.exe --silent --fail --max-time 2 "http://127.0.0.1:8004/index.html" >nul 2>&1
if errorlevel 1 (
    start "Original Freeboard Server" /min py -m http.server 8004 --bind 127.0.0.1 --directory "%FREEBOARD_DIR%"
)

set /a WAIT_COUNT=0
:WAIT_FOR_FREEBOARD
curl.exe --silent --fail --max-time 2 "http://127.0.0.1:8004/index.html" >nul 2>&1
if not errorlevel 1 goto OPEN_DASHBOARD
set /a WAIT_COUNT+=1
if %WAIT_COUNT% GEQ 15 goto SERVER_ERROR
timeout /t 1 /nobreak >nul
goto WAIT_FOR_FREEBOARD

:OPEN_DASHBOARD
start "" "%DASHBOARD_URL%"
exit /b 0

:SERVER_ERROR
echo [ERROR] Freeboard server did not start on port 8004.
pause
exit /b 1