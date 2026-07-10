@echo off
rem Streamlit 대시보드 실행 스크립트 (Windows). 더블클릭으로 실행한다.
rem setup.bat을 먼저 한 번 실행해서 가상환경을 만들어둬야 한다.
setlocal

cd /d "%~dp0"

if not exist ".venv" (
    echo [오류] 가상환경^(.venv^)이 없습니다. 먼저 setup.bat 을 실행하세요.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo 대시보드를 실행합니다. 잠시 후 브라우저가 자동으로 열립니다...
echo 종료하려면 이 창에서 Ctrl+C를 누르세요.
echo.
streamlit run scripts\dashboard\app_streamlit.py

pause
