---
name: test-triage
description: UI(Playwright)·API(httpx) pytest 실패를 real-bug / selector-drift / timing / spec-change / test-bug / env 로 분류하고 원인을 분석한다. 전체 실행 뒤나 실패를 고치기 전에 먼저 실행. 코드는 수정하지 않고, 분류 결과를 백로그, 노션 "이슈 검수" 후보, Slack에 기록한다.
argument-hint: "[test-runs/<일시> | latest | ui|api <nodeid 조각>]"
model: opus
---

# /test-triage
대상: `$ARGUMENTS`
- `test-runs/<일시>-<ui|api>` 또는 `latest ui|api`: 전체 실행 보관본의 모든 실패와 xfail. 1~9번을 모두 한다.
- `ui|api <nodeid 조각>`: 작업 중 실패 몇 건만 빠르게 본다. `test-results/`를 읽고 1~6번만 한다(노션, Slack 없음).
- 비어 있으면 `latest`다.

사라(QA 리더)가 메인 세션에서 직접 한다. 원인 분석이 이 단계의 핵심이라 서브에이전트에 맡기지 않는다. 코드, TC, 마커 수정과 `skip`/`xfail` 추가는 루트 "실패 분류와 가드레일"대로 하지 않는다.

## 1. 입력 수집
1. 실패 목록
   - 보관본: `<대상>/report.json`의 실패와 xfail 항목. UI 증거는 `<대상>/tests-*/`(trace, 스크린샷)와 `<대상>/dom-snapshots/`
   - 작업 중: UI `playwright-demo/.venv/bin/python scripts/failures.py [nodeid조각]`, API `api-demo/test-results/report.json`
   - `report.json`이 없거나 오래됐으면 사용자에게 재실행을 요청한다(전체 실행은 승인 지점).
2. xfail 상태 변화: `XPASS(strict)` 실패와, 테스트 안 `pytest.xfail`로 고정했던 테스트가 통과로 바뀐 것을 따로 모은다(5번 출력의 "백로그 갱신 대상").
3. TC 기대결과: 종류별 구글 시트(주소는 각 폴더 `CLAUDE.md`)에서 마커 ID 행을 읽는다. 시트에 접근하지 못하면 멈추고 보고한다.
4. 코드: 실패한 테스트 함수와 의존 코드(UI `pages/*.py`, API `clients/`, `schemas/`, `conftest.py`). API는 `api-demo/api-docs.json`도 본다.
5. 실패 증거: UI는 trace와 스크린샷을 먼저 본다. 재실행보다 증거 확인이 먼저다.

## 2. 백로그 대조
- 실패 메시지와 TC ID로 `.claude/docs/backlog/00_index.md`에서 같은 원인의 항목을 찾는다.
- 있으면 다시 분석하지 않는다. 분류는 그 항목을 따르고, 항목의 "마지막 확인" 날짜만 갱신한다. 증상이 항목과 다르면 새로 분석한다.

## 3. 같은 원인 묶기
- 남은 실패를 예외 종류와 메시지 요지(상태 코드, 셀렉터, 에러 문구)로 묶는다. ex: 여러 테스트의 동시 5xx, 같은 셀렉터 타임아웃
- 묶음당 한 번 분류하고, 묶음에 속한 테스트를 모두 적는다.

## 4. 분류 (정확히 하나 + 확신도 high/med/low)
- **real-bug**: 테스트와 환경은 정상인데 앱/API가 TC 기대와 다르게 동작한다.
- **selector-drift**: (UI) 로케이터가 실패했고, 페이지에 이름만 바뀐 대응 요소가 있다.
- **timing**: 테스트의 대기 방식이 틀려 재실행하면 통과한다.
- **spec-change**: 테스트가 바뀐 TC나 스펙의 옛 기대를 검증한다. `spec analysis/analysis-log.md`와 기능 파일 "변경 이력"에서 최근 변경을 확인한다.
- **test-bug**: 테스트, Page Object, client, schema 코드 오류다. ex: 헤더 누락, id 하드코딩
- **env**: 테스트 바깥 문제다. ex: 사이트 다운, `ReadTimeout`, 5xx, DB 리셋, 계정 잠금, 사전 조건 데이터 없음

헷갈릴 때
- 대응 요소가 아예 없으면 selector-drift가 아니라 real-bug 가능성이 높다.
- 재실행해도 실패하면 timing이 아니다. 서버가 응답하지 못했으면 env다.
- 같은 조건에서 앱 동작이 달라지면 간헐 결함(real-bug)이다. 등급과 추적은 `.claude/guides/issue-severity.md`의 간헐 결함 규칙을 따른다.
- 테스트 코드가 명백히 틀렸으면 test-bug가 우선이다.
- API 응답이 스펙과 다르면 real-bug 또는 spec-change다. real-bug로 정하기 전에 헤더 같은 클라이언트 설정부터 의심한다.
- 스펙이 동작을 정의하지 않았거나 불일치 유형 B, C면 분류는 real-bug(low)로 두고 리포트 그룹을 "안건"으로 적는다.

재실행
- 원인을 가리는 데 필요하면 1회만 한다.
- 재실행하지 않는 것: 로그인 실패 TC(계정 잠금 위험)
- 승인 후 재실행하는 것: 결제 확정 TC(지울 수 없는 인보이스 생성). trace로 먼저 판단한다.

원인 태그(선택): `contract`(스펙과 구조 다름), `auth`(401/403/잠금), `data`(데이터 의존), `header`(요청 헤더 문제)

## 5. 출력
보관본이면 `<대상>/triage-report.md`, 작업 중이면 `<playwright-demo|api-demo>/test-results/triage-report.md`와 콘솔 요약. 묶음 하나당 아래 형식으로 쓴다.

```markdown
### <묶음 요지 한 줄>
- 대상: <nodeid> (TC <ID> — <기능>), ...
- 분류: <category> (확신도) / 리포트 그룹: 리얼버그|테스트버그|flaky|안건 / 태그: <tag|없음>
- 중요도: High|Medium|Low (real-bug만, `.claude/guides/issue-severity.md`)
- 백로그: 기존 #N | 신규 #N | 없음
- 근거: 실패 메시지 / 기대(TC·스펙) / 관찰(trace, dom_snapshot 또는 실제 응답) / 재현 결과
- 조치: test-bug·timing·selector-drift → 수리 대상 | real-bug → 수리 금지, 이슈 초안 | spec-change → 사람이 결정 | env → 환경 복구 후 재실행 | 안건 → wiki 안건
```

- 리포트 그룹은 루트 "실패 분류와 가드레일"의 4그룹 매핑을 따른다.
- 맨 끝에 "백로그 갱신 대상"을 따로 쓴다. XPASS나 통과로 바뀐 xfail 테스트와 해당 백로그 번호다.
- 분류가 애매하면 확신도를 `low`로 낮추고 근거를 자세히 쓴다. 근거 없이 "재시도"로 넘기지 않는다.
- real-bug가 있으면 `.claude/guides/jira-issue-format.md` 형식으로 이슈 초안을 제시한다. 등록은 사용자 승인(Notion "이슈 검수" DB) 후에 한다.

## 6. 백로그 기록
- 새로 발견했거나 분류가 바뀐 항목은 `.claude/guides/backlog-format.md` 형식으로 `.claude/docs/backlog/`의 상태별 파일에 쓰고 `python3 scripts/backlog_index.py`로 인덱스를 갱신한다.
- 순서: 분류 → 스펙과 라이브 비교 → real-bug인지 test-bug인지 판단 → 항목 추가 → 인덱스 갱신
- 백로그 기록은 사용자 승인 전에 해도 된다. Jira 등록은 하지 않는다.

## 7. Jira 중복 검색 (보관본만)
- real-bug 묶음마다 `project = QA AND type = 버그 AND (summary ~ "<핵심어>" OR text ~ "<TC ID>")`로 찾는다. 검색만 하고 등록하지 않는다.
- 같은 현상의 이슈가 있으면 노션 행의 "근거"에 "Jira 중복 후보: <키>"를 적는다.

## 8. 노션 기록 (보관본만)
1. "테스트 실행" DB(`collection://de613125-b2b2-40af-842a-9f1265e9376c`)에서 이 실행의 행(보관 경로가 `<대상>`)을 찾는다. 없으면 만든다(속성은 `/test-run` 6번과 같다).
   - 본문은 `.claude/guides/notion-test-record-format.md` 2번(요약, 통과 현황, 실패 현황과 이슈·백로그 링크, xfail, 근거와 자료)으로 쓴다.
   - "진행 상태"를 "검토 대기"로 바꾼다.
2. "이슈 검수" DB(`collection://beb91aef-0900-4169-95f4-4bbbedc2d1fc`)에 실패 묶음마다 행을 올린다. 리포트 그룹과 관계없이 모두 올린다(사용자가 분류를 바로잡을 수 있게).
   - 같은 백로그 번호의 행이 있고 상태가 "종료"가 아니면 새로 만들지 않는다. "테스트 실행" 관계에 이번 실행을 더하고 "근거"를 갱신한다.
   - 백로그 상태에 Jira 키가 있는 real-bug는 "기존 이슈 재현(키)"를 근거에 적고 상태를 "등록 완료"로 둔다.
   - 본문은 `.claude/guides/notion-test-record-format.md` 3번(real-bug는 Jira 초안 + 검토 메모, 그 밖은 검토 메모)과 4번(스크린샷)을 따른다.
   - 새 행의 속성
     - 이슈 제목: `jira-issue-format.md`의 제목 형식(`[UI|API] 어떤 기능에서 어떤 현상`)
     - 구분, TC ID, 사라 분류(6분류 또는 안건), 중요도(real-bug만)
     - 기대결과, 실제결과: 시트 TC와 실제 관찰을 명사형 한두 줄로
     - 재현 절차: TC 스텝을 번호로
     - 근거: 한 줄 요약(` / `로 3개 이내) + "(상세는 검토 메모 2번)"
     - 백로그 `#N`, 테스트 실행일, 테스트 실행(관계), 상태 "검수 대기"
     - 검토 결과, 수정 분류, 검토 의견은 비워 둔다(사용자 칸).
3. 사용자는 "검토 결과"(승인, 반려, 보류, 분류 수정)를 고른다. 체크 시점은 알림으로 받지 않고, 사용자가 `/issue-register`를 실행하거나 검토 완료를 알리면 그때 읽는다.

## 9. Slack (보관본만)
- `<대상>/slack.json`의 실행 메시지 스레드에 분류 결과를 답글로 올린다. 명사형으로 짧게, 아래 모양으로 쓴다.
```
*분류 결과*
• [UI|API] <TC>
    ◦ <분류>(<리포트 그룹>, <원인 요지>)
    ◦ 백로그 <#N>
    ◦ 노션 <이슈 검수 행 링크|이슈 검수>
• xpass <N>건, xfail <N>건 유지

*Next to-do-list*
• 노션 이슈 검수 대기 <N>건(<사라 분류별 건수>)
• 검토 결과 선택 후 /issue-register
• 수리 대상: <TC>(<분류>)
• 실행 요약: <테스트 실행 행 링크|테스트 실행 YYYY-MM-DD HH:MM>
```
- 백로그 링크를 넣으려면 백로그 변경을 커밋·push한 뒤 올린다(커밋은 승인 지점이라 링크 없이 번호만 써도 된다).

## 10. 사용자 검토 반영 (사용자가 "검토 끝"을 알리거나 진행을 요청할 때)
노션 "이슈 검수"의 검토 결과대로 아래 순서를 멈추지 않고 진행한다. 사용자가 진행을 요청한 것이 이 순서 전체(백로그 커밋, Jira 등록, xfail 커밋, 보고서 초안)의 승인이다. 보고서 게시(승인 ④)만 따로 묻는다. 검토 결과가 비어 있는 행은 건드리지 않는다.
1. 검토 결과 반영
   - 승인: real-bug면 등록 대상. 안건이면 결과 보고서의 안건 섹션 대상
   - 분류 수정: "수정 분류"가 비어 있으면 "검토 의견"에서 읽어 채운다. 백로그 항목의 분류와 파일 위치를 고치고(`backlog-format.md` 4번) 인덱스를 갱신한다. real-bug로 바뀌면 중요도를 정하고 Jira 초안을 확인해 등록 대상으로 둔다.
   - 반려: 백로그 항목을 `05_done.md`로 옮기고 이슈 행 상태를 "종료"로 바꾼다.
   - 보류: 그대로 두고 결과 보고서의 미결 항목에 적는다.
   - 백로그를 고쳤으면 커밋·push한다(Jira 본문의 백로그 링크가 열리게).
2. Jira 등록: 등록 대상이 있으면 `/issue-register`를 실행한다. 보고를 받아 링크, 첨부 등 빠진 곳을 사라가 확인하고 바로잡는다.
3. xfail 고정: 새로 등록된 real-bug의 테스트를 `script-write` SKILL.md "xfail 규칙"대로 고정한다.
   - 테스트 전체가 그 불일치만 검증하면 `xfail(strict=True, reason="백로그 #N(Jira 키)")`, 일부면 그 비교만 `pytest.xfail`로 감싸고 알려진 증상일 때만 xfail한다.
   - 해당 테스트만 1회 실행해 xfail을 확인하고 `script_lint.py`를 돌린다. 백로그 "현재 테스트" 줄을 갱신하고 커밋·push한다.
4. 결과 보고서: 등록 대상이 모두 "등록 완료"(또는 사유가 있는 미등록)이고 "분류 수정 대기"가 없으면 `/report-write`로 이어간다. 남은 것이 있으면 그 목록을 보고하고 멈춘다.
5. 단계마다 Slack 실행 스레드에 짧게 올리고, 노션 "테스트 실행" 행의 진행 상태를 갱신한다.

## 다음 단계
- 사용자가 노션 "이슈 검수"의 "검토 대기" 보기에서 "검토 결과"를 고른다(승인 ③). 그 뒤 `/issue-register`(Issue-Reporter)가 승인된 real-bug를 Jira에 등록한다. "분류 수정" 행은 사라가 백로그와 분류를 먼저 고친다.
- 결과 보고서는 사라가 `/report-write`로 쓴다. 테스트버그·flaky 묶음은 수리 대상 목록으로 보고 끝에 적는다.
