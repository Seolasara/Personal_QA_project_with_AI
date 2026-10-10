# 작성 가이드
산출물을 쓸 때 따르는 형식 모음이다. 해당 산출물을 쓰는 단계에서만 그 파일을 읽는다. 문체는 전역 "문서 문체"를 따른다.

- [backlog-format.md](backlog-format.md): `.claude/docs/backlog/`의 항목 작성 형식. `test-triage`가 분류 결과를 기록할 때 쓴다.
- [jira-issue-format.md](jira-issue-format.md): Jira 버그 이슈 제목과 본문 형식. real-bug 이슈 초안을 쓸 때 쓴다.
- [notion-test-record-format.md](notion-test-record-format.md): 노션 "테스트 실행" 행과 "이슈 검수" 행의 속성, 본문, 증거(스크린샷, 로그) 형식. `/test-run`, `/test-triage`가 쓴다.
- [test-report-format.md](test-report-format.md): Confluence 테스트 결과 보고서의 섹션과 채우는 법. `/report-write`가 쓴다.
- [issue-severity.md](issue-severity.md): 이슈 중요도(High/Medium/Low) 판정 기준. 백로그, Jira, 결과 보고서가 같이 쓴다.
- TC 작성 형식은 `.claude/skills/tc-write/SKILL.md`에 있다.
- 이 폴더는 `CLAUDE.md`처럼 자동으로 읽히지 않는다. 스킬과 에이전트가 필요한 단계에서 파일을 지정해 읽는다.
