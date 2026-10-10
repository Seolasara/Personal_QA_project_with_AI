---
name: report-write
description: 테스트 결과 보고서 파이프라인. 사용자가 결과 보고서 작성을 요청하거나 /report-write를 실행할 때, 또는 test-triage 10번에서 이슈 등록이 끝났을 때 쓴다. 전체 실행 보관본, 분류 결과, 노션, Jira로 Confluence 결과 보고서 초안을 만들고 승인 후 게시한다.
argument-hint: "[test-runs/<일시> | latest]"
---

# /report-write
대상: `$ARGUMENTS` (ex: `test-runs/2026-10-10-0239`). 비어 있거나 `latest`면 `test-runs/`의 가장 최근 폴더다.
사라(QA 리더)가 메인 세션에서 직접 쓴다. 초안은 Confluence 임시 저장(draft)으로 만들고, 게시는 사용자 승인(승인 ④) 뒤에 한다. 문체는 전역 "문서 문체"를 따른다.

## 1. 입력
- 보관본: `<대상>/ui|api/report.json`, `<대상>/triage-report.md`, `<대상>/slack.json`
- 노션: "테스트 실행" 행(보관 경로가 `<대상>`)과 연결된 "이슈 검수" 행(사라 분류, 검토 결과, Jira 키)
- Jira(`QA` 프로젝트): 남은 이슈 `project = QA AND type = 버그 AND statusCategory != Done ORDER BY priority DESC`
- TC 커버리지: 시트 CSV(루트 `CLAUDE.md`의 CSV 주소)로 `python3 scripts/tc_marker_check.py --ui <UI.csv> --api <API.csv>`
- 사인오프 기준: 각 QA plan(UI 65702, API 5996545)의 사인오프 기준. 미해결 High 결함 0건이 기본이다.
- 시작 전 확인: 노션 "이슈 검수"에 이 실행의 "분류 수정 대기"나 등록 안 된 승인 real-bug가 남아 있으면 쓰지 않고 그 목록을 보고한다.

## 2. 보고서 구성
위치: Confluence "Test Result Report"(11665420) 하위, 제목 `Test Result Report (YYYY-MM-DD)`. 템플릿 "Test result Report Template"(11632643)의 섹션 순서를 따르고 4~6번을 덧붙인다.
1. Test Result Summary
   - Test Period(실행 일시), Environment(사이트 URL, 브라우저, 도구 버전), Build / Version(커밋과 브랜치), Tester(사라 AI, 검토자), Comment(사인오프 판정 한 줄)
2. Test Scope
   - UI, API별 대상 기능(대분류)과 TC 수, 자동/수동 TC 수, 제외 범위
3. Test Result (TC 커버리지 포함)
   - Total, Pass, Fail, Blocked, xfail, Pass Rate(통과/전체). Blocked는 실행하지 못한 TC(수동 미실행, 사전 조건 미충족)
   - 대분류별 표: 대분류, 전체, 통과, 실패, xfail
   - 커버리지: 시트 TC 수 대비 자동화된 TC 수
4. BTS Status
   - 이번 실행에서 새로 등록한 이슈: 키, 제목, 중요도, TC
   - 남은 이슈(위 JQL) 표: 키, 제목, 중요도, 상태, 관련 TC. 표 위에 JQL을 적는다.
   - Known Issues: xfail로 고정된 백로그 항목과 Jira 키
5. 실패 분류
   - 리포트 그룹(리얼버그, 테스트버그, flaky, 안건)별 건수와 TC, 처리 결과(등록, 수리, 보류). 노션 이슈 행 링크를 붙인다.
   - 안건: 스펙 판단이 필요한 항목과 백로그 링크. 승인된 안건은 wiki 안건 문서 대상으로 표시한다.
6. 사인오프와 다음 조치
   - 판정: 사인오프 기준 충족 여부와 근거(미해결 High 결함 수)
   - 다음 조치: 보류 항목, 수리 대상, 다음 실행 계획

## 3. 작성 절차
1. 1번 입력을 모아 수치를 맞춘다. report.json 합계, 노션 실행 행, Slack 본문의 숫자가 같은지 확인한다.
2. Confluence 쓰기 전에 `getContentFormatGuide`(createConfluencePage)를 한 번 읽고, 표가 있으므로 HTML 본문으로 쓴다.
3. `createConfluenceContent`(contentType page, `draft: true`, parent `parentContentId: 11665420`)로 초안을 만든다.
4. 사용자에게 초안 링크와 요약(판정, 핵심 수치, 남은 이슈)을 보고하고 게시 승인을 묻는다.
5. 승인되면 게시한다. 게시 후
   - 노션 "테스트 실행" 행의 진행 상태를 "보고서 완료"로 바꾸고 본문 "근거와 자료"에 보고서 링크를 넣는다.
   - Slack 실행 스레드에 `*결과 보고서*` 답글로 링크와 판정을 올린다.
- CI 헤드리스에서는 Confluence를 건드리지 않는다(루트 가드레일).

## 4. 완료 기준
- 2번 섹션이 모두 채워졌거나, 빈 섹션에 이유가 적혀 있다.
- 숫자가 보관본, 노션, Slack과 일치한다.
- 남은 이슈 표의 키가 Jira와 같고, 노션·백로그와 서로 링크된다.
