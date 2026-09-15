# .agents/ — ⚠️ Gemini/Antigravity 전용 인프라, 자격증명 취급

`plugins/confluence_mcp.py`는 **Gemini/Antigravity가 쓰는** Confluence MCP 서버다.
Claude Code `.mcp.json`에는 등록되어 있지 않다 (의도적으로 제거함 — OAuth 방식 `atlassian`
서버만 사용). 즉 나(Claude Code)는 이 서버를 **실행할 수 없지만, 코드는 여전히 수정할 수 있다** —
그리고 이 코드를 고치면 제미나이 쪽 동작이 그대로 바뀐다.

## 이 폴더가 하는 일
- `.env.local`의 `CONFLUENCE_EMAIL` + `CONFLUENCE_API_TOKEN`(고정 API 토큰, OAuth 아님)으로
  Atlassian Basic Auth 인증.
- 노출 툴: `confluence_get_page`(읽기), `confluence_search`(읽기),
  `confluence_update_page`(**기존 페이지 덮어쓰기**), `confluence_create_page`(**신규 페이지 생성**).
  즉 읽기 전용이 아니라 실제 쓰기 권한이 있는 스크립트다.

## 추가 가드레일 (루트 가드레일에 더해 적용)
- `CONFLUENCE_API_TOKEN`, `CONFLUENCE_EMAIL` 값을 로그/출력/커밋/에러 메시지에 남기지 않는다.
- 이 폴더 수정은 항상 "큰 변경"으로 취급 — 계획을 먼저 제안하고 승인 후 진행한다
  (나에게는 안 보이지만 제미나이 쪽 쓰기 동작에 영향을 주기 때문).
- `update_page`/`create_page`의 동작(버전 처리, payload 구조, 에러 핸들링)을 바꿀 때는
  실제 Confluence 페이지에 반영되기 전에 사용자 확인을 받는다 — 되돌리기 어려움.
- `.mcp.json`에 이 서버(`confluence`)를 다시 등록하지 않는다 — 재등록이 필요하다고 판단되면
  먼저 사용자에게 이유를 묻는다 (OAuth 우회 경로가 다시 열리는 것이므로).
- `.env.local`이 `.gitignore`에 있는지 커밋 전 항상 재확인 (이미 등록되어 있음 — 지우지 말 것).
- `.agents/plugins/confluence/mcp_config.json`, `plugin.json`은 제미나이/Antigravity의
  자체 설정 파일 — Claude Code 동작과 무관하니 임의로 이 저장소 관례(예: 상대경로)에 맞춰
  "정리"하지 않는다.
