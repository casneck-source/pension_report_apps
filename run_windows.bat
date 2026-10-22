@echo off
chcp 65001 > nul
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 설치하세요. 설치 화면에서 "Add Python to PATH"를 꼭 체크하세요.
    pause
    exit /b
)

if not exist ".venv" (
    echo [1/3] 처음 실행이라 준비 중입니다. 1~2분 걸립니다...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

if not exist ".env" (
    copy .env.example .env > nul
    echo [2/3] 메모장이 열리면 sk-ant- 로 시작하는 API 키를 붙여넣고 저장한 뒤 메모장을 닫으세요.
    notepad .env
)

echo [3/3] 앱을 실행합니다. 잠시 후 브라우저가 열립니다. 끝내려면 이 창을 닫으세요.
streamlit run app.py
pause
