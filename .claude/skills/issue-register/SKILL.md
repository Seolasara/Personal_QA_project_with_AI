---
name: issue-register
description: 이슈 등록 파이프라인. 사용자가 승인된 이슈의 Jira 등록을 요청하거나 /issue-register를 실행할 때 쓴다. 노션 "이슈 검수" DB에서 검토 결과가 "승인"인 real-bug 행만 Jira에 등록하고 키를 기록한다.
context: fork
agent: Issue-Reporter
argument-hint: "[비워 두면 승인된 행 전체]"
---

# /issue-register
대상: 노션 "이슈 검수" DB(`collection://beb91aef-0900-4169-95f4-4bbbedc2d1fc`)에서 상태가 "검수 대기"이고 아래 중 하나인 행.
- 검토 결과 "승인"이고 사라 분류가 real-bug
- 검토 결과 "분류 수정"이고 수정 분류가 real-bug이며, 백로그 항목이 `01_real-bug.md`에 있음(사라가 test-triage 10번으로 반영한 뒤)
작업 순서와 업무 규칙은 `.claude/agents/Issue-Reporter.md`를 따르고, 등록 방법은 아래를 따른다.

## 1. 대상 읽기
- "검토 결과"가 있는 행을 모두 읽고, 등록 대상만 처리한다. 검토 결과가 비어 있는 행은 건드리지 않는다.
- 등록하지 않고 보고만 하는 행
  - 승인된 안건: 보고의 "wiki 안건 대상"에 적는다(결과 보고서의 안건 섹션에서 쓴다).
  - "분류 수정" 중 수정 분류가 real-bug가 아니거나 백로그가 아직 반영되지 않은 행: "분류 수정 대기"로 보고한다.
  - 반려, 보류: 건수만 보고한다.

## 2. Jira 등록 (real-bug 행)
1. 등록 직전에 Jira 중복을 다시 찾는다(test-triage "7. Jira 중복 검색"과 같은 JQL). 같은 현상이 있으면 등록하지 않고 근거에 기존 키를 적고 보고한다.
2. `.claude/guides/jira-issue-format.md`대로 만든다.
   - 프로젝트 `QA`, 이슈 유형 "버그", 우선순위는 행의 중요도
   - 레이블과 에픽, 증거 형식은 종류 폴더 `CLAUDE.md`(UI: `ui`, QA-5, 스크린샷 / API: `api`, QA-6, 요청과 응답 원문). 스펙 불일치면 `spec-mismatch`도 붙인다.
   - 제목은 노션 "이슈 제목", 본문은 노션 행의 "Jira 초안" 부분을 그대로 옮긴다(`.claude/guides/notion-test-record-format.md` 3-1). 문장을 새로 쓰거나 고치지 않는다.
   - Jira 초안이 없거나 9개 섹션이 다 차 있지 않으면 등록하지 않고 "초안 미완성"으로 보고한다.
   - 노션 이미지 줄은 빼고 옮긴다. 대신 UI 이슈는 보관본 스크린샷(`[스크린샷/로그]`에 적힌 경로)을 Jira 첨부로 올린다.
     1. `executeWrite`로 `uploadAttachmentToJiraIssue`(`issueIdOrKey`, `filePath`)를 호출해 `uploadCommand`를 받는다.
     2. Bash로 `uploadCommand`를 실행하고 응답의 `data.id`를 받는다. 토큰이 든 명령은 출력하지 않는다.
     3. 같은 작업을 `fileId`로 다시 호출해 첨부한다.
3. 생성 후 노션 행에 "Jira 키", "Jira 링크"를 쓰고 상태를 "등록 완료"로 바꾼다. 연결된 "테스트 실행" 행의 진행 상태도 "등록 완료"로 바꾼다(그 실행의 승인 행이 모두 처리됐을 때).
4. 백로그 항목의 "분류와 상태"에 `Jira <키> 등록(YYYY-MM-DD)`을 적는다.

## 3. Slack
- 행의 백로그 번호로 가장 최근 보관본의 `slack.json`을 찾을 수 있으면 그 스레드에 `*Jira 등록*` 답글로 `• <키> <제목> (<중요도>)`를 올린다. 없으면 건너뛴다.

## 4. 완료 기준
- 등록 대상 행이 모두 "등록 완료"이거나, 중복으로 등록하지 않은 사유가 근거에 있다.
- 등록한 이슈의 키가 노션 행과 백로그에 모두 있다.

# 다음 단계
- 결과 보고서 작성은 `/report-write`(만들 예정)다. 보고 끝에 "결과 보고서를 작성할지" 한 줄로 묻는다.
