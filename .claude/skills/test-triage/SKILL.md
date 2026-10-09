---
name: test-triage
description: UI(Playwright)·API(httpx) pytest 실패를 real-bug / selector-drift / timing / spec-change / test-bug / env 로 분류한다. 실패를 고치기 전에 항상 먼저 실행. 코드는 수정하지 않고 근거와 함께 분류만 한다.
argument-hint: "[ui|api] [nodeid 조각 - 특정 실패만]"
---

# /test-triage
대상: `$ARGUMENTS`. 비어 있으면 UI·API 양쪽 `test-results/report.json`의 모든 실패를 대상으로 한다.
분류만 한다. 코드, TC, 마커 수정과 `skip`/`xfail` 추가는 루트 "실패 분류와 가드레일"대로 하지 않는다.

## 1. 입력 수집
1. 실패 목록
   - UI: `playwright-demo/.venv/bin/python scripts/failures.py [nodeid조각]` (longrepr, aria snapshot, dom_snapshot 포함)
   - API: `api-demo/test-results/report.json`의 실패 항목 (assertion, pydantic `ValidationError`, httpx 예외)
   - `report.json`이 없거나 오래됐으면 사용자에게 재실행을 요청한다(전체 실행은 승인 지점).
2. xfail 상태 변화: `XPASS(strict)` 실패와, 테스트 안 `pytest.xfail`로 고정했던 테스트가 통과로 바뀐 것을 따로 모은다(5번 출력의 "백로그 갱신 대상").
3. TC 기대결과: 종류별 구글 시트(주소는 각 폴더 `CLAUDE.md`)에서 마커 ID 행을 읽는다. 시트에 접근하지 못하면 멈추고 보고한다.
4. 코드: 실패한 테스트 함수와 의존 코드(UI `pages/*.py`, API `clients/`, `schemas/`, `conftest.py`). API는 `api-demo/api-docs.json`도 본다.
5. 실패 증거: UI는 `test-results/`의 trace와 스크린샷을 먼저 본다. 재실행보다 증거 확인이 먼저다.

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
`<playwright-demo|api-demo>/test-results/triage-report.md`와 콘솔 요약. 묶음 하나당 아래 형식으로 쓴다.

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
