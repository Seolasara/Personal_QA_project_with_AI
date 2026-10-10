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

## 2. 보고서 형식
- `.claude/guides/test-report-format.md`를 따른다(섹션 6개: Summary, Scope, Result와 커버리지, BTS Status, 실패 분류, 사인오프와 다음 조치).

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
