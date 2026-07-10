@echo off
rem 프로젝트 초기 설치 스크립트 (Windows). 더블클릭으로 실행한다.
rem 가상환경 생성 -> 패키지 설치 -> .env 파일 준비까지 한 번에 처리한다.
setlocal

cd /d "%~dp0"

echo ==============================================
echo  Kor1 프로젝트 초기 설치
echo ==============================================

where python >nul 2>nul
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않거나 PATH에 없습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.10 이상을 설치한 뒤 다시 실행하세요.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [1/3] 가상환경^(.venv^) 생성 중...
    python -m venv .venv
) else (
    echo [1/3] 가상환경^(.venv^) 이미 존재 - 건너뜀
)

echo [2/3] 패키지 설치 중... ^(몇 분 걸릴 수 있습니다^)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo [오류] 패키지 설치에 실패했습니다. 위 로그를 확인하세요.
    pause
    exit /b 1
)

if not exist ".env" (
    echo [3/3] .env 파일 생성 중 ^(.env.example 복사^)...
    copy .env.example .env >nul
    echo       DART 공시 수집기를 쓰려면 .env 파일을 열어 DART_API_KEY 값을 채워주세요.
    echo       ^(https://opendart.fss.or.kr 에서 무료 발급^)
) else (
    echo [3/3] .env 파일 이미 존재 - 건너뜀
)

echo.
echo ==============================================
echo  설치 완료! run_dashboard.bat 을 더블클릭해서 대시보드를 실행하세요.
echo ==============================================
pause
