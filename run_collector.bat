@echo off
rem KRX 시세/투자자별 매매동향 수집기 실행 스크립트 (Windows). 더블클릭으로 실행한다.
rem setup.bat을 먼저 한 번 실행해서 가상환경을 만들어둬야 한다.
setlocal

cd /d "%~dp0"

if not exist ".venv" (
    echo [오류] 가상환경^(.venv^)이 없습니다. 먼저 setup.bat 을 실행하세요.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

set /p TICKER=종목코드를 입력하세요 (예: 005930):
set /p START_DATE=시작일을 입력하세요 (YYYYMMDD, 예: 20260101):
set /p END_DATE=종료일을 입력하세요 (YYYYMMDD, 예: 20260710):

echo.
echo %TICKER% 종목의 %START_DATE% ~ %END_DATE% 데이터를 수집합니다...
python -m scripts.collectors.collector_krx %TICKER% %START_DATE% %END_DATE%

echo.
echo 수집 완료(성공/실패 여부는 위 로그 참고). data\raw\krx\%TICKER%\ 폴더를 확인하세요.
pause
