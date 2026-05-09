@echo off
REM =============================================================================
REM Kimari — Launch server and open browser (Windows Batch)
REM =============================================================================

setlocal EnableDelayedExpansion

set KIMARI_ROOT=%~dp0..\..
set CONFIG_FILE=%KIMARI_ROOT%\config\kimari.profiles.json
set PROFILE=gtx1060

echo === Kimari — Launching Web UI ===

REM Check config
if not exist "%CONFIG_FILE%" (
    echo [ERROR] Config not found: %CONFIG_FILE%
    exit /b 1
)

REM Start server in background
echo [INFO] Starting Kimari server in background ...
start "Kimari Server" /MIN powershell -ExecutionPolicy Bypass -File "%KIMARI_ROOT%\scripts\windows\start-kimari-1060.ps1"

REM Wait for server
echo [INFO] Waiting for server to start ...
set READY=0
for /l %%i in (1,1,30) do (
    if !READY!==0 (
        ping -n 2 127.0.0.1 >nul 2>&1
        curl -s --connect-timeout 2 http://127.0.0.1:11435/health >nul 2>&1
        if !errorlevel!==0 (
            set READY=1
        )
    )
)

if !READY!==0 (
    echo [OK] Server is ready!
) else (
    echo [WARN] Server may not be ready yet. Try opening manually.
)

REM Open browser
echo [INFO] Opening browser ...
start http://127.0.0.1:11435

echo.
echo === Kimari is running ===
echo   API:  http://127.0.0.1:11435
echo.
echo   Close the "Kimari Server" window to stop.

endlocal
