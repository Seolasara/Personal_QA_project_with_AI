# MCP 서버 현황
이 프로젝트에서 쓰는 MCP 서버의 등록 위치와 용도다. 확인 날짜 2026-10-12. 서버를 추가하거나 빼면 이 파일도 고친다. 계정과 토큰 값은 쓰지 않는다.

## 1. 등록 위치
1. 프로젝트(루트 `.mcp.json`)
   - `atlassian`: Confluence, Jira. HTTP, OAuth(`https://mcp.atlassian.com/v2/mcp`). 최초 사용 시 `/mcp`에서 인증한다.
   - `playwright`: 브라우저 조작. stdio(`npx @playwright/mcp@latest`). `/flow-map` 흐름 탐색과 스크립트 작성 중 라이브 확인에 쓴다.
2. 사용자 레벨(`~/.claude.json`, 모든 프로젝트에서 보임)
   - `notion`: 노션 DB(테스트 실행, 이슈 검수, 업무 일지)와 페이지 읽기·쓰기
   - `slack`: 실행 결과 채널 메시지와 스레드 답글
3. 계정 커넥터(claude.ai)
   - Google Sheets: TC 시트 읽기·쓰기
   - Claude Docs, Google Drive: 이 프로젝트에서는 쓰지 않는다(Drive는 인증이 안 된 상태).

## 2. 누가 무엇을 쓰나
- 사라(메인 세션): Confluence(QA plan, 결과 보고서), Jira 검색·수정, 노션, Slack, Google Sheets
- TC-Writer: Google Sheets
- Script-Writer: Google Sheets, Playwright(라이브 확인)
- Document-Analyzer: 노션(분석 실행 이력)
- Issue-Reporter: Jira 등록, 노션 행 갱신, Slack 스레드 답글

## 3. 알려진 제약
- Confluence 초안(draft)은 API로 읽고 고칠 수 있지만, 한 번도 게시하지 않은 초안을 게시본으로 바꾸는 것은 API로 안 된다. 게시는 사용자가 한다.
- Slack 파일(HTML 리포트) 업로드는 MCP에 없어서 루트 `.env`의 `SLACK_BOT_TOKEN`으로 Slack API를 직접 호출한다(`/test-run` 5번).
- 노션과 Jira의 이미지 첨부는 MCP가 업로드 주소만 주고 파일 전송은 `curl`로 한다. 방법은 `.claude/guides/notion-test-record-format.md` 4번과 `.claude/skills/issue-register/SKILL.md`에 있다.
- 결제 확정은 TC 테스트 코드와 `/flow-map`에서만 허용한다. 그 밖의 Playwright MCP 탐색에서는 확정하지 않는다(루트 `CLAUDE.md`).

## 4. 상태 확인
- 터미널에서 `claude mcp list`로 연결 상태를 본다. VS Code 확장 세션에서는 `/mcp`로 본다.
