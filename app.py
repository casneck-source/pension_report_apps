"""
💼 미래에셋 연금RM 일일 활동보고 자동 생성기

키워드 메모 몇 줄을 입력하면, 연금RM 부서 카카오톡 보고 양식(개조식, '-함/-음/명사형' 종결)으로
팀장님 제출용 일일 활동보고서를 만들어 줍니다.

실행:  streamlit run app.py
"""

import json
import os
from datetime import date

import anthropic
import streamlit as st
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# 0. 기본 설정
# ─────────────────────────────────────────────
load_dotenv()  # 로컬 실행 시 .env 파일의 ANTHROPIC_API_KEY 를 읽어옴

MODEL = "claude-opus-5-5"
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

st.set_page_config(
    page_title="연금RM 일일보고 생성기",
    page_icon="💼",
    layout="centered",
)


def get_api_key() -> str | None:
    """로컬은 .env, Streamlit Cloud 배포 시에는 Secrets 에서 API 키를 읽어옴."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:  # secrets.toml 이 아예 없는 경우
        return None


# ─────────────────────────────────────────────
# 1. 프롬프트 (카카오톡 보고 내역 분석 결과 반영)
# ─────────────────────────────────────────────
# 실제 단톡방 일일보고 약 900건을 분석해 뽑은 팀 고유 스타일:
#  - 머리말: "N팀 홍길동 수석 (2026.10.21)" 형태
#  - 법인별 번호 매김: "1. 법인명(신규/미도입/기존)" → 하위 "- " 개조식
#  - 활동 유형 태그: "방문 / ", "사내 / ", "유선 / " 등 슬래시 구분
#  - 면담자 표기: "HR팀장, 실무자 미팅", "(w. 노무사 동행)"
#  - 종결어미: 명사형(예정·안내·제안·완료·협의·요청·확정·전달) + '-함/-음'
#  - 빈출 용어: DC/DB/IRP, 사업자 진입·이전·추가, 제도전환, 경성DC, 경영성과급DC,
#    상담부스, 제도설명회, 세미나, 규약 변경, 사무담당자, 실물이전, 단체개인연금,
#    퇴직임원 IRP, 연컨(연금컨설팅), 디폴트옵션, 운용현황, 수익률, 부담금, 명부
# 아래 예시는 실제 보고문의 문체만 살리고 고객사명·인명·금액은 가명/가공 처리함.

SYSTEM_PROMPT = """너는 미래에셋증권 연금RM(법인 퇴직연금 영업) 부서에서 10년 넘게 일한 베테랑 수석이다.
팀원이 대충 적어 준 활동 메모를 받아, 팀장님께 카카오톡으로 올리는 '일일 활동보고서'로 정리한다.

# 반드시 지킬 출력 양식
첫 줄: 보고자 머리말 (예: "2팀 홍길동 수석 (2026.10.21)") — 사용자가 준 작성자/일자를 그대로 사용
그다음 아래 4개 목차를 이 순서·이 제목 그대로 쓴다.

1. 금일 주요 활동 및 상담 내역
2. 영업 성과 및 파이프라인
3. 특이사항 및 이슈
4. 익일 계획

# 목차별 작성 규칙
[1. 금일 주요 활동 및 상담 내역]
- 법인별로 "① 법인명(신규/미도입/기존 등 알 수 있을 때만)" 형태로 묶는다. 원문자 ①②③ 순서로 번호를 매긴다.
- 각 법인 아래 첫 줄은 "- 활동유형 / 면담자" 형태로 쓴다. (활동유형: 방문, 사내, 유선, 메일, 중식, 세미나 등. 면담자: 인사팀장, HR 담당임원, 사무담당자, CFO, 실무자 등)
- 이어서 "- " 개조식으로 주요 안건을 1~4줄 정리한다.
- 동행자가 있으면 "(w. 노무사 동행)"처럼 괄호로 붙인다.

[2. 영업 성과 및 파이프라인]
- 메모에 등장한 수주·유치·전환 건을 "- 법인명: 내용 (예상 규모 / 진행 단계)" 형태로 정리한다.
- 예상 규모(금액·인원), 디폴트옵션 도입 여부, 사업자 진입/이전/추가 여부, 제도(DB/DC/IRP/경성DC/경영성과급DC) 정보가 있으면 반드시 명시한다.
- 진행 단계는 "제안 → 협의 중 → 확정 → 계좌개설/입금 완료" 같은 표현으로 짧게 판단해 붙인다. (단, 메모에서 추론 가능한 범위까지만)

[3. 특이사항 및 이슈]
- 고객사 애로사항, 민원, 제도·세제 변경 문의, 담당자 부재·인사이동, 경쟁사 동향, 내부 협조 필요 사항 등을 적는다.

[4. 익일 계획]
- Follow-up 일정을 "- 법인명: 할 일 (시점)" 형태로 적는다. 시점이 없으면 "(익일)" 또는 "(차주)"처럼 메모 표현을 따른다.

# 문체 규칙
- 개조식. 각 줄은 "- "로 시작하고 한 줄은 짧게.
- 종결은 명사형(예정, 안내, 제안, 완료, 협의, 요청, 확정, 전달, 조율, 회신 등) 또는 '-함 / -음'으로 끝낸다. "~했습니다", "~합니다" 같은 서술형 금지.
- 업계 용어를 자연스럽게 사용: DC/DB/IRP, 사업자 진입·이전·추가, 제도전환, 디폴트옵션(사전지정운용제도), 규약 변경, 상담부스, 제도설명회, 사무담당자, 부담금, 운용현황, 수익률, 실물이전, 단체개인연금, 퇴직임원 IRP, 연컨, 당사, 타사 등.
- 메모의 축약어를 풀어 쓰되(예: "디옵" → "디폴트옵션", "사업자 이전 유치" 등), 회사명·인명·숫자는 메모 그대로 둔다.

# 절대 금지
- 메모에 없는 사실, 금액, 인원, 일정, 인명을 지어내지 않는다. 모르면 쓰지 않는다.
- 해당 목차에 넣을 내용이 없으면 "- 특이사항 없음" 한 줄만 쓴다.
- 인사말, 설명, 마크다운 기호(#, **, 표)를 쓰지 않는다. 카카오톡에 그대로 붙여넣을 순수 텍스트만 출력한다.

# 참고: 우리 팀이 실제로 올린 보고 문체 예시 (가명 처리)
<style_examples>
2팀 김OO 수석
1. A화학(미도입)
- 방문 / 노동조합 중식, 제도도입 관련 사측과 큰 틀에서 협의 시작(DB, DC 동시 도입 고려 중)
- 기금형제도 도입 관련 퇴직금 강제 투자 우려 있음. 기금형제도 법안 발의내용 전달

2. B물산
- 사내 / 퇴직임원 세후 퇴직금 IRP 입금 관련 사내 작업
---
1팀 이OO 수석 (2026. 10. 19)
1. C제약(신규)
- 자금팀장
  / DC사업자 진입 확정
  / 개정규약 최종본 작성업무 지원
  / 퇴직연금스쿨 초대
2. D홀딩스
- 자금팀장, 차장
  / 법인고유자금 운용니즈 확인(20억)
  / 목표전환형 & 롱숏펀드 추가제안
---
2팀 박OO 수석
1. E인터내셔널
- 경성DC 도입 위한 노조 대상 컨설팅 진행 협의
- 차주 수요일 당사 노무사와 함께 법인 방문하여 경성DC 컨설팅 진행 합의

2. F세미콘
- 법인 금융팀장 차주 미팅 일정 확정(10/15)
- 실무자 대상 DB운용 현황 및 수익률 세부 자료 안내
---
1팀 최OO 수석
G건설
- DC제도전환 및 개인연금 사업자 추가 관련 자료요청
- 현재 근로자 수익률, 상품 분석 등 자료 요청함
- 차주 전달 및 미팅 예정
</style_examples>"""

# 입력 → 최종 출력 Few-shot 예시 (4개 목차 양식 시연용)
FEW_SHOT_USER = """보고 일자: 2026.10.21 (수)
작성자: 2팀 홍길동 수석

활동 메모:
H전자 인사팀장 미팅 dc 디옵 규약변경 설명함 타사 30억 이전 긍정적, 노무사 동행
I물류 사무담당자 통화 dc 수익률 급락 민원 직원설명회 요청
J바이오 미도입 대표님 중식 경영성과급dc 관심, 다음주 제안서 보내기로
내일 I물류 설명회 날짜 확정 전화"""

FEW_SHOT_ASSISTANT = """2팀 홍길동 수석 (2026.10.21)

1. 금일 주요 활동 및 상담 내역
① H전자
- 방문 / 인사팀장 미팅 (w. 노무사 동행)
- DC 디폴트옵션 운영 관련 규약 변경 사항 설명
- 타사 DC 적립금 당사 이전 관련 긍정적 반응 확인

② I물류
- 유선 / 사무담당자
- 최근 DC 수익률 급락에 따른 가입자 민원 발생 공유받음
- 직원 대상 설명회 개최 요청 접수

③ J바이오(미도입)
- 중식 / 대표이사
- 경영성과급DC 도입에 관심 표명함

2. 영업 성과 및 파이프라인
- H전자: 타사 DC 적립금 당사 이전 유치 (예상 규모 30억 / 긍정 검토 중)
- J바이오: 경영성과급DC 신규 도입 (제안 단계 / 차주 제안서 발송 예정)

3. 특이사항 및 이슈
- I물류: DC 수익률 급락으로 가입자 불만 발생, 설명회 통한 조기 대응 필요

4. 익일 계획
- I물류: 직원 설명회 일정 확정 위한 유선 협의 (익일)
- J바이오: 경영성과급DC 제안서 작성 및 발송 (차주)"""


def build_user_message(report_date: date, author: str, memo: str) -> str:
    date_str = f"{report_date:%Y.%m.%d} ({WEEKDAYS[report_date.weekday()]})"
    return f"보고 일자: {date_str}\n작성자: {author}\n\n활동 메모:\n{memo.strip()}"


def stream_report(api_key: str, report_date: date, author: str, memo: str):
    """Claude 응답을 글자 단위로 흘려보내는 제너레이터 (st.write_stream 용)."""
    client = anthropic.Anthropic(api_key=api_key)
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        output_config={"effort": "medium"},
        # 안전 필터로 거절될 경우 서버가 자동으로 다른 모델로 재시도
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[
            {"role": "user", "content": FEW_SHOT_USER},
            {"role": "assistant", "content": FEW_SHOT_ASSISTANT},
            {"role": "user", "content": build_user_message(report_date, author, memo)},
        ],
    ) as stream:
        yield from stream.text_stream
        final = stream.get_final_message()
    if final.stop_reason == "refusal":
        raise RuntimeError("AI가 이 요청에 대한 응답을 거절했습니다. 메모 내용을 확인해 주세요.")
    if final.stop_reason == "max_tokens":
        st.warning("보고서가 너무 길어 일부가 잘렸을 수 있습니다. 메모를 나눠서 생성해 보세요.")


def copy_button(text: str) -> None:
    """원클릭 클립보드 복사 버튼 (HTML + JS)."""
    # "<" 를 이스케이프해 보고서 안의 문자열이 <script> 태그를 깨뜨리지 않도록 함
    payload = json.dumps(text).replace("<", "\\u003c")
    st.iframe(
        f"""
        <style>body {{ margin: 0; }}</style>
        <button id="copy-btn" style="
            width:100%; padding:0.55rem 0; font-size:15px; font-weight:600;
            border:1px solid rgba(49,51,63,0.25); border-radius:8px;
            background:#ffffff; color:#262730; cursor:pointer;">
            📋 원클릭 클립보드 복사
        </button>
        <script>
        const text = {payload};
        const btn = document.getElementById("copy-btn");
        function done(ok) {{
            btn.innerText = ok ? "✅ 복사 완료! 카톡에 붙여넣기 하세요" : "⚠️ 복사 실패 - 텍스트를 직접 선택해 주세요";
            setTimeout(() => btn.innerText = "📋 원클릭 클립보드 복사", 2500);
        }}
        function fallbackCopy() {{
            const ta = document.createElement("textarea");
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            let ok = false;
            try {{ ok = document.execCommand("copy"); }} catch (e) {{}}
            document.body.removeChild(ta);
            done(ok);
        }}
        btn.addEventListener("click", () => {{
            if (navigator.clipboard && window.isSecureContext) {{
                navigator.clipboard.writeText(text).then(() => done(true), fallbackCopy);
            }} else {{
                fallbackCopy();
            }}
        }});
        </script>
        """,
        height=50,
    )


# ─────────────────────────────────────────────
# 2. 화면 구성
# ─────────────────────────────────────────────
st.title("💼 미래에셋 연금RM 일일 활동보고 자동 생성기")
st.caption("오늘 한 일을 키워드로 대충 적어도, 팀장님 제출용 보고 양식으로 정리해 드립니다.")

api_key = get_api_key()
if not api_key:
    st.error(
        "ANTHROPIC_API_KEY 가 설정되지 않았습니다. "
        "로컬은 `.env` 파일, Streamlit Cloud 는 App settings → Secrets 에 키를 넣어 주세요."
    )

col1, col2 = st.columns(2)
with col1:
    report_date = st.date_input("📅 보고 일자", value=date.today(), format="YYYY.MM.DD")
with col2:
    author = st.text_input("✍️ 작성자", placeholder="예: 2팀 홍길동 수석")

memo = st.text_area(
    "📝 오늘 수행한 활동 메모",
    height=200,
    placeholder=(
        "A사 방문, DC 디폴트옵션 규약 변경 설명, 타사 50억 이전 유치 긍정적 / "
        "B물류 담당자 부재로 내일 통화 예정"
    ),
    help="법인명, 만난 사람, 안건, 금액, 다음 할 일을 키워드로만 적어도 됩니다. 줄바꿈이나 '/'로 구분해 주세요.",
)

if st.button("🚀 팀장님 보고서 생성하기", type="primary", use_container_width=True, disabled=not api_key):
    if not author.strip():
        st.warning("작성자 이름을 입력해 주세요.")
    elif not memo.strip():
        st.warning("활동 메모를 입력해 주세요.")
    else:
        try:
            with st.status("보고서를 작성하고 있습니다...", expanded=True) as status:
                result = st.write_stream(stream_report(api_key, report_date, author.strip(), memo))
                status.update(label="작성 완료!", state="complete", expanded=False)
            st.session_state["report"] = result.strip()
            st.session_state["report_editor"] = result.strip()  # 새 결과로 편집창 갱신
            st.session_state["report_date"] = report_date
            st.session_state["report_author"] = author.strip()
        except anthropic.AuthenticationError:
            st.error("API 키가 올바르지 않습니다. ANTHROPIC_API_KEY 를 확인해 주세요.")
        except anthropic.RateLimitError:
            st.error("요청이 많아 잠시 제한되었습니다. 1분 후 다시 시도해 주세요.")
        except anthropic.APIConnectionError:
            st.error("네트워크 연결에 실패했습니다. 인터넷 연결을 확인해 주세요.")
        except anthropic.APIStatusError as e:
            st.error(f"AI 서버 오류가 발생했습니다 ({e.status_code}). 잠시 후 다시 시도해 주세요.")
        except RuntimeError as e:
            st.error(str(e))

# 결과 영역 (버튼을 다시 누르지 않아도 화면에 유지)
if "report" in st.session_state:
    st.divider()
    st.subheader("📄 완성된 일일 활동보고서")
    final_text = st.text_area(
        "필요하면 아래에서 직접 수정한 뒤 복사/다운로드하세요.",
        height=420,
        key="report_editor",
    )

    b1, b2 = st.columns(2)
    with b1:
        copy_button(final_text)
    with b2:
        d = st.session_state["report_date"]
        st.download_button(
            "💾 .txt 파일 다운로드",
            data=final_text.encode("utf-8"),
            file_name=f"일일보고_{d:%Y%m%d}_{st.session_state['report_author'].replace(' ', '')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
