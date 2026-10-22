# 💼 미래에셋 연금RM 일일 활동보고 자동 생성기

오늘 한 일을 **키워드로 대충 적기만 하면**, 우리 팀 카카오톡 보고 양식(개조식, `-함/-음`·명사형 종결)으로
팀장님 제출용 일일 활동보고서를 만들어 주는 웹 앱입니다.

```
[입력]  A사 방문, DC 디폴트옵션 규약 변경 설명, 타사 50억 이전 유치 긍정적 / B물류 담당자 부재로 내일 통화 예정

[출력]  2팀 홍길동 수석 (2026.10.22)

        1. A사
        - 방문 / 담당자 미팅
        - DC 디폴트옵션 운영 현황 점검 및 규약 변경 절차 안내
        - 타사 DC 적립금 당사 이전 관련 긍정적 반응 확인 (약 50억 규모)
        - 이전 절차 관련 자료 송부 예정

        2. B물류
        - 유선 / 담당자 부재로 금일 통화 불가
        - 익일 재연락 예정
```

## 📁 파일 구성

| 파일 | 설명 |
|---|---|
| `app.py` | 웹 화면 + AI 호출 코드 (프롬프트/Few-shot 예시 포함) |
| `requirements.txt` | 필요한 파이썬 패키지 목록 |
| `.env.example` | API 키 설정 예시 파일 |
| `.gitignore` | API 키 파일(.env)이 GitHub에 올라가지 않도록 막는 설정 |

---

## 1️⃣ 내 PC에서 실행하기 (처음 한 번만 따라 하면 됩니다)

### 준비물
- **Python 3.10 이상** ([python.org](https://www.python.org/downloads/) 에서 설치, Windows는 설치 시 *"Add Python to PATH"* 체크)
- **Anthropic API 키** ([console.anthropic.com](https://console.anthropic.com) → *API Keys* → *Create Key*)

### 실행 순서

터미널(Windows: *명령 프롬프트* 또는 *PowerShell*, Mac: *터미널*)을 열고 프로젝트 폴더로 이동한 뒤:

```bash
# 1) 가상환경 만들기 (패키지를 이 프로젝트 안에만 설치)
python -m venv .venv

# 2) 가상환경 켜기
#    Windows:
.venv\Scripts\activate
#    Mac / Linux:
source .venv/bin/activate

# 3) 패키지 설치
pip install -r requirements.txt

# 4) API 키 파일 만들기
#    Windows:
copy .env.example .env
#    Mac / Linux:
cp .env.example .env
#    → 메모장 등으로 .env 파일을 열어 sk-ant-... 키를 붙여넣고 저장

# 5) 실행!
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501` 에서 앱을 사용할 수 있습니다.
종료는 터미널에서 `Ctrl + C`.

> 다음부터는 **2) 가상환경 켜기 → 5) 실행** 두 단계만 하면 됩니다.

---

## 2️⃣ 인터넷에 무료로 배포하기 (Streamlit Community Cloud)

배포하면 휴대폰·회사 PC 어디서든 링크 하나로 접속할 수 있습니다.

### Step 1. GitHub에 코드 올리기
1. [github.com](https://github.com) 가입 후 오른쪽 위 **+ → New repository**
2. 이름 예: `pension-rm-report`, **🔒 Private(비공개)** 선택 ← *고객사 정보가 담길 수 있으므로 꼭 비공개로!*
3. 만들어진 저장소 화면에서 **uploading an existing file** 클릭 →
   `app.py`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md` 를 끌어다 놓고 **Commit changes**
   - ⚠️ **`.env` 파일(실제 API 키)은 절대 올리지 마세요.**

### Step 2. Streamlit Cloud 연결
1. [share.streamlit.io](https://share.streamlit.io) 접속 → **Continue with GitHub** 로 로그인
2. **Create app → Deploy a public app from GitHub** (비공개 저장소도 선택 가능)
3. 입력값
   - Repository: `내아이디/pension-rm-report`
   - Branch: `main`
   - Main file path: `app.py`
4. **Advanced settings → Secrets** 칸에 아래처럼 입력 (`.env` 대신 여기에 키를 넣습니다)
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-본인-키"
   APP_PASSWORD = "팀원들과-공유할-비밀번호"
   ```
   `APP_PASSWORD` 를 넣으면 앱 첫 화면에서 비밀번호를 물어봅니다. 주소가 외부에 퍼져도 내 API 키가 쓰이지 않게 막아 줍니다.
5. **Deploy!** → 1~2분 뒤 `https://xxxx.streamlit.app` 주소가 생깁니다.

### Step 3. 사용 금액 한도 걸기 (권장)
[console.anthropic.com](https://console.anthropic.com) → **Settings → Limits** 에서 월 사용 한도를 정해 두면, 예상보다 많이 쓰여도 그 이상은 청구되지 않습니다.

### (선택) 접속 제한 걸기
배포된 앱 화면 오른쪽 아래 **Manage app → ⋮ → Settings → Sharing** 에서
*"Only specific people can view this app"* 를 선택하고 팀원 이메일만 추가하세요.
누구나 접속하면 **내 API 키로 요금이 청구**됩니다.

### 코드를 수정했을 때
GitHub 저장소의 파일을 수정(연필 아이콘 ✏️)하고 저장하면, Streamlit Cloud가 **자동으로 다시 배포**합니다.

---

## 3️⃣ 사용 팁

- **작성자 칸**은 `2팀 홍길동 수석` 처럼 팀·직급까지 적으면 보고서 머리말에 그대로 들어갑니다.
- 메모는 **법인명 / 만난 사람 / 안건 / 금액·인원 / 다음 할 일** 순으로 키워드만 적어도 충분합니다.
  여러 법인은 **줄바꿈** 이나 **`/`** 로 구분하세요.
- 생성된 보고서는 결과 창에서 **직접 수정**한 뒤 복사·다운로드할 수 있습니다.
- 법인을 2곳 적으면 `1. 법인명` / `2. 법인명` 처럼 번호가 붙어 정리됩니다.
- 짧은 키워드도 연금RM 업무 표현으로 풀어서 써 주지만, 메모에 **없는 숫자·사람 이름·날짜는 지어내지 않도록** 설정되어 있습니다.

## 4️⃣ 보고 양식 바꾸고 싶을 때

`app.py` 상단의 다음 부분만 고치면 됩니다.

| 바꾸고 싶은 것 | 수정 위치 |
|---|---|
| 양식·문체 규칙 | `SYSTEM_PROMPT` |
| 팀 실제 보고 문체 예시 | `SYSTEM_PROMPT` 안의 `<style_examples>` |
| 입력→출력 완성 예시 | `FEW_SHOT_USER`, `FEW_SHOT_ASSISTANT` |
| 사용 AI 모델 | `MODEL` (기본값 `claude-opus-5-5`) |

> 💡 문체 예시는 단톡방 실제 보고 약 900건을 분석해 만들었고, **고객사명·인명은 가명(A화학, B물산 등)으로 바꿔** 넣었습니다.

## ❓ 자주 묻는 문제

| 증상 | 해결 |
|---|---|
| `ANTHROPIC_API_KEY 가 설정되지 않았습니다` | 로컬: `.env` 파일 이름·위치(app.py와 같은 폴더) 확인 / 배포: Secrets 입력 확인 |
| `API 키가 올바르지 않습니다` | 키 앞뒤 공백, 따옴표 확인. 콘솔에서 키를 새로 발급 |
| `streamlit: command not found` | 가상환경이 켜져 있는지 확인 (`.venv\Scripts\activate`) |
| 복사 버튼이 안 될 때 | 회사 보안 브라우저에서 클립보드가 막힌 경우입니다. 결과 창에서 `Ctrl+A → Ctrl+C` 로 복사하세요 |
