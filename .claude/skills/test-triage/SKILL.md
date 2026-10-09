---
name: test-triage
description: UI(Playwright)·API(httpx) pytest 실패를 real-bug / selector-drift / timing / spec-change / test-bug / env 로 분류한다. 실패를 고치기 전에 항상 먼저 실행. 코드는 수정하지 않고 근거와 함께 분류만 한다.
argument-hint: "[ui|api] [nodeid 조각 - 특정 실패만]"
---

# 테스트 실패 Triage

분류만 한다. 코드·TC는 수정하지 않는다 (CLAUDE.md 가드레일).

## 실행 인자
- 대상: `$ARGUMENTS`. 비어 있으면 UI·API 양쪽 `test-results/report.json`의 모든 실패를 대상으로 한다.
- `report.json`이 없거나 오래됐으면 사용자에게 `pytest` 재실행을 먼저 요청한다.

## 입력 수집
1. 실패 목록
   - UI: `playwright-demo/.venv/bin/python scripts/failures.py [nodeid조각]` (longrepr, aria snapshot, dom_snapshot 포함)
   - API: `api-demo/test-results/report.json` 의 실패 항목 (assertion, pydantic `ValidationError`, httpx 예외)
2. TC 기대결과: 종류별 구글 스프레드시트(주소는 각 폴더 `CLAUDE.md`)에서 마커 ID 행을 찾는다. `UI_`는 `UI-TC` 탭, `API_`는 `API-TC` 탭. 시트에 접근 못 하면 멈추고 보고한다.
3. 코드: 실패한 테스트 함수와 그 의존 코드 (UI는 `pages/*.py`, API는 `clients/`·`schemas/`·`conftest.py`). API는 `api-demo/api-docs.json` 스펙도 확인한다.
4. 재현이 필요하면 1회 재실행한다. 로그인 실패 케이스는 계정 잠금 위험으로 재실행하지 않는다.

## 분류 (정확히 하나 + 확신도 high/med/low)
| 분류 | 판단 기준 |
|---|---|
| **real-bug** | 테스트·환경은 정상인데 앱/API가 TC 기대와 다르게 동작 |
| **selector-drift** | (UI) 로케이터 실패, 페이지에 이름만 바뀐 대응 요소가 있음 |
| **timing** | 재실행하면 통과, 테스트의 대기 방식이 틀림 |
| **spec-change** | 테스트가 바뀐 TC/스펙의 옛 기대를 검증 중 |
| **test-bug** | 테스트·POM·클라이언트·스키마 코드 오류 (헤더 누락, ID 하드코딩 등) |
| **env** | 테스트 바깥 문제: 사이트 다운, `ReadTimeout`, 5xx, 계정 잠금 |

헷갈릴 때:
- 대응 요소가 아예 없으면 selector-drift가 아니라 real-bug 가능성.
- 재실행해도 실패하면 timing이 아니다. 서버가 응답 못 했으면 env.
- 테스트 코드가 명백히 틀렸으면 test-bug가 우선.
- API 응답이 스펙과 다르면 real-bug(API가 틀림) 또는 spec-change(스펙이 낡음). real-bug로 정하기 전에 헤더 같은 클라이언트 설정부터 의심한다.

원인 태그(선택): `contract`(스펙과 구조 다름), `auth`(401/403/잠금), `data`(데이터 의존), `header`(요청 헤더 문제).

## 출력
`<playwright-demo|api-demo>/test-results/triage-report.md` + 콘솔 요약. 실패 1건당:

```markdown
### <nodeid>
- TC: <ID> — <기능>
- 분류: <category> (확신도) / 태그: <tag|없음>
- 근거: 실패 메시지 / 기대(TC·스펙) / 관찰(dom_snapshot 또는 실제 응답) / 재현 결과
- 조치: test-bug·timing·selector-drift → 수리 대상(사람 판단) | real-bug → 수리 금지, 이슈 초안 | spec-change → 사람이 결정 | env → 환경 복구 후 재실행
```

real-bug가 있으면 `.claude/guides/jira-issue-format.md`를 읽고 그 형식으로 이슈 초안을 제시한다. 등록은 사용자 승인(Notion "이슈 검수" DB) 후에 한다.

## 백로그 기록
- 새로 발견했거나 분류가 바뀐 항목은 `.claude/guides/backlog-format.md`를 읽고 `.claude/docs/backlog/`의 상태별 파일에 기록한다. `00_index.md`에서 중복을 먼저 찾는다.
- 순서: 분류 → 스펙과 라이브 비교 → real-bug인지 test-bug인지 판단 → 해당 파일에 항목 추가 → 인덱스 갱신.
- 백로그 기록은 사용자가 승인하기 전에 해도 된다. Jira 등록은 하지 않는다.

산출물은 `triage-report.md`와 콘솔 요약뿐이다. 분류가 애매하면 확신도를 `low`로 낮추고 근거를 상세히 쓴다.

## 하지 말 것
- 코드·TC 수정, `skip`/`xfail` 추가
- 근거 없이 "재시도"로 넘기기
- 분류 여러 개 부여
