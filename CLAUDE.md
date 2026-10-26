# 작업 규칙

- 이 저장소의 `main` 브랜치는 Streamlit Community Cloud(https://mirae-pension-rm.streamlit.app/)에 바로 배포된다.
- 사용자가 수정을 요청하면, 변경을 확인(테스트)한 뒤 **따로 묻지 말고 `main`에 커밋하고 바로 푸시한다.** (사용자 요청에 따른 상시 허용)
- 푸시 전에 `git pull --rebase origin main`으로 원격 변경(Streamlit이 추가하는 `.devcontainer` 등)을 먼저 받는다.
- API 키, 비밀번호 같은 비밀값은 절대 커밋하지 않는다. 비밀값은 Streamlit Secrets에만 둔다.
- 보고서 문체 예시에는 실제 고객사명·인명을 넣지 않고 가명(A화학, B물산 등)을 쓴다.
