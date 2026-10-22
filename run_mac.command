#!/bin/bash
cd "$(dirname "$0")"

if ! command -v python3 > /dev/null; then
    echo "[오류] Python이 설치되어 있지 않습니다. https://www.python.org/downloads/ 에서 설치하세요."
    read -p "Enter를 누르면 닫힙니다."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "[1/3] 처음 실행이라 준비 중입니다. 1~2분 걸립니다..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[2/3] 텍스트 편집기가 열리면 sk-ant- 로 시작하는 API 키를 붙여넣고 저장한 뒤 닫으세요."
    open -W -e .env
fi

echo "[3/3] 앱을 실행합니다. 잠시 후 브라우저가 열립니다. 끝내려면 이 창을 닫으세요."
streamlit run app.py
