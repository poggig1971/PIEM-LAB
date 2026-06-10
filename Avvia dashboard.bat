@echo off
cd /d "%~dp0"
echo Avvio del Navigatore Prezzario Lombardia 2026...
echo Apertura su http://localhost:8765 - lasciare questa finestra aperta.
where py >nul 2>nul
if %errorlevel%==0 (
  start "" http://localhost:8765
  py -m http.server 8765
  exit /b
)
where python >nul 2>nul
if %errorlevel%==0 (
  start "" http://localhost:8765
  python -m http.server 8765
  exit /b
)
echo.
echo Python non risulta installato: impossibile avviare il server locale.
echo Installare Python da https://www.python.org oppure pubblicare la cartella su GitHub Pages (vedere README.md).
pause
