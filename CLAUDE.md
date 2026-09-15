# Personal QA Project

개인 QA 프로세스 + QA AI 에이전트 + LLM judge 평가를 하나로 묶은 프로젝트.
테스트 대상은 공개 데모 사이트 <https://practicesoftwaretesting.com> (Toolshop).

## 목적
1. QA 하고자하는 대상 서비스의 기획 문서와 요구사항을 분석하여 QA 프로세스를 수립한다.
2. 테스트케이스(TC)를 코드로 관리하고 Confluence와 동기화한다.
3. Playwright(pytest) UI 자동화 스크립트를 유지한다.
4. pytest 프레임워크로 API requests 스크립트를 유지한다.
5. 에이전트가 QA 프로세스의 개선점을 분석하고 제안한다.
6. 에이전트가 테스트 실패를 분류(triage)하고, 스펙/셀렉터 변경으로 인한 실패를 수리한다.
7. LLM judge가 에이전트의 수리 결과를 채점한다.

## 저장소 구조
- `playwright-demo/` — UI 자동화(Playwright/pytest). 컨벤션은 [playwright-demo/CLAUDE.md](playwright-demo/CLAUDE.md).
- `testcases/` — TC 원본(마크다운) + Confluence 동기화. 규칙은 [testcases/CLAUDE.md](testcases/CLAUDE.md).
- `scripts/` — 리포트/트레이서빌리티 생성, CI 게이트 스크립트. 규칙은 [scripts/CLAUDE.md](scripts/CLAUDE.md).
- `.agents/plugins/` — Confluence MCP 서버(자격증명 취급). **Gemini/Antigravity 전용** — Claude Code(`.mcp.json`)에는 등록하지 않는다.
  규칙은 [.agents/CLAUDE.md](.agents/CLAUDE.md) — **변경 전 반드시 확인** (수정하면 Gemini 쪽에도 영향).

## 에이전트 가드레일 (중요)
- 변경 전 관련 파일을 먼저 읽는다.
- 큰 변경은 근거를 포함하여 계획을 **먼저 제안**하고 진행 여부를 묻는다. 
- 에이전트는 사용자 허락이 있을 때만 **draft PR만** 생성한다. main 직접 push·머지·auto-merge 금지.
- pr/커밋 생성 시 **무엇을, 왜** 바꾸는지 변경 의도와 범위를 명확히 한다.
- 실패는 반드시 **먼저 분류**한다: `real-bug` / `selector-drift` / `timing` / `spec-change` / `test-bug`.
- **`real-bug`로 분류되면 코드를 수정하지 않는다.** 이슈/PR에 근거와 함께 보고만 한다.
- 수리 시 **금지**: 어설션 삭제·약화, `wait_for_timeout` 추가/증량, `skip`/`xfail` 마킹, 검증 셀렉터를 항상 존재하는 것으로 바꿔치기.
- judge는 항상 **별도 세션**에서 실행한다 (수리 에이전트의 대화 맥락을 물려주지 않는다).
- CI 헤드리스에서는 Confluence(MCP OAuth)를 건드리지 않는다. repo 수정 + PR까지만.
- 민감 정보, 토큰, 운영 설정은 출력하지 않는다.

## 코드 스타일
- 현재 코드 스타일을 따른다.
- 불필요한 대규모 리팩토링을 피한다.
- 공개 API 변경 시 문서와 테스트를 함께 갱신한다.