---
name: issue-register
description: 이슈 등록 파이프라인. 사용자가 승인된 이슈의 Jira 등록을 요청하거나 /issue-register를 실행할 때 쓴다. 노션 "이슈 검수" DB에서 승인된 real-bug 행만 Jira에 등록하고 키를 기록한다.
context: fork
agent: Issue-Reporter
argument-hint: "[비워 두면 승인된 행 전체]"
---

# /issue-register
대상: 노션 "이슈 검수" DB(`collection://beb91aef-0900-4169-95f4-4bbbedc2d1fc`)에서 "승인"이 체크되고 상태가 "검수 대기" 또는 "승인"인 행.
작업 순서와 업무 규칙은 `.claude/agents/Issue-Reporter.md`를 따르고, 등록 방법은 아래를 따른다.

## 1. 대상 읽기
- 위 조건의 행을 읽는다. 승인 체크가 없는 행은 읽기만 하고 건드리지 않는다.
- 분류가 "안건"인 승인 행은 Jira에 올리지 않는다. 상태를 "승인"으로 두고 보고의 "wiki 안건 대상"에 적는다(결과 보고서의 안건 섹션에서 쓴다).

## 2. Jira 등록 (real-bug 행)
1. 등록 직전에 Jira 중복을 다시 찾는다(test-triage "7. Jira 중복 검색"과 같은 JQL). 같은 현상이 있으면 등록하지 않고 행의 상태를 "보류"로, 근거에 기존 키를 적고 보고한다.
2. `.claude/guides/jira-issue-format.md`대로 만든다.
   - 프로젝트 `QA`, 이슈 유형 "버그", 우선순위는 행의 중요도
   - 레이블과 에픽, 증거 형식은 종류 폴더 `CLAUDE.md`(UI: `ui`, QA-5, 스크린샷 / API: `api`, QA-6, 요청과 응답 원문). 스펙 불일치면 `spec-mismatch`도 붙인다.
   - 본문의 Test Environment, Steps, Expected, Actual은 행과 백로그 항목, 보관본에서 채운다. 확인 일시를 적는다.
   - 첨부 파일은 올리지 않는다. 증거는 보관본 경로와 원문 요지를 본문에 적고, 스크린샷 첨부가 필요하면 보고의 `ask_user`에 올린다.
3. 생성 후 노션 행에 "Jira 키", "Jira 링크"를 쓰고 상태를 "등록 완료"로 바꾼다.
4. 백로그 항목의 "분류와 상태"에 `Jira <키> 등록(YYYY-MM-DD)`을 적는다.

## 3. Slack
- 행의 백로그 번호로 가장 최근 보관본의 `slack.json`을 찾을 수 있으면 그 스레드에 `*Jira 등록*` 답글로 `• <키> <제목> (<중요도>)`를 올린다. 없으면 건너뛴다.

## 4. 완료 기준
- 승인된 real-bug 행이 모두 "등록 완료" 또는 "보류"(사유 있음)다.
- 등록한 이슈의 키가 노션 행과 백로그에 모두 있다.

# 다음 단계
- 결과 보고서 작성은 `/report-write`(만들 예정)다. 보고 끝에 "결과 보고서를 작성할지" 한 줄로 묻는다.
