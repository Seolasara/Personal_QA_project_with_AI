---
name: test-triage
description: Playwright(pytest) 테스트 실패를 real-bug / selector-drift / timing / spec-change / test-bug 로 분류한다. 실패를 고치기 전에 항상 먼저 실행. 코드는 절대 수정하지 않고 근거와 함께 분류만 한다.
---

# 테스트 실패 Triage

CLAUDE.md 가드레일: **실패는 반드시 먼저 분류한다. `real-bug`면 코드를 수정하지 않는다.**
이 스킬은 분류만 한다. 수리는 별도(`test-repair`).

## 입력 수집 (이 순서대로)

1. `playwright-demo/.venv/bin/python scripts/failures.py [nodeid조각]`
   → 실패별 `nodeid`, `tc`, `longrepr`(assertion + Playwright call log + aria snapshot), `dom_snapshot`, `artifacts`.
2. `tc` 값으로 `testcases/<TC>.md` 를 읽는다 — **기대결과(expected)** 가 판단 기준.
3. 실패한 테스트 함수 본문 + 그 테스트가 쓰는 Page Object(`playwright-demo/pages/*.py`)를 읽는다.
4. `dom_snapshot` JSON 이 있으면 읽는다 — 실패 시점에 페이지에 **실제 존재한** `data-test` 목록.
5. 필요하면 같은 테스트를 1회 재실행해 재현성을 본다 (timing 판정용):
   `playwright-demo/.venv/bin/pytest <nodeid> -q`

## 분류 기준

정확히 하나로 분류한다. 확신도(high/med/low)도 함께.

| 분류 | 신호 | 예 |
|---|---|---|
| **real-bug** | 셀렉터·타이밍 문제 없음. 앱이 TC 기대결과와 **다르게** 동작. aria snapshot 상 기대한 상태가 실제로 없음. | "Payment was successful" 가 떠야 하는데 에러 메시지가 뜸. Confirm 눌렀는데 아무 일 없음. |
| **selector-drift** | 로케이터가 아무것도 못 찾음(`element(s) not found`). dom_snapshot / aria snapshot 에 **이름만 바뀐 대응 요소**가 보임(`nav-cart`→`cart-nav`, role/text 변경). | POM 이 `[data-test="proceed"]` 인데 페이지엔 `proceed-3` 만 있음. |
| **timing** | 재실행하면 통과. `Timeout ... exceeded` 인데 요소는 결국 나타남. 비동기 로드/애니메이션/네트워크 레이스. 어설션 대상 자체는 맞음. | 토스트가 뜨기 전에 확인. `networkidle` 전에 폼 입력. |
| **spec-change** | 테스트 어설션이 **현재 TC 기대결과와 모순**. TC(또는 Confluence)가 바뀌었고 테스트가 옛 기대를 검증 중. | TC: 타이틀 "...Toolshop...", 테스트: "...Toolshow...". |
| **test-bug** | 앱은 정상. 테스트/POM 로직 오류 — 잘못된 fixture, 잘못된 어설션, POM 메서드 오용, 잘못된 대기. | 성공 경로 대기(`wait_for_url`)를 실패 케이스에 사용. `self.city.fill(state)`. |

경계 판단:
- `element(s) not found` 라고 무조건 selector-drift 아님. dom_snapshot 에 대응 요소가 **없으면** → 그 요소가 있어야 할 상태에 앱이 도달 못 한 것 → real-bug 가능성.
- `Timeout` 이라고 무조건 timing 아님. 재실행해도 계속 실패하고 요소가 끝내 안 나타나면 → real-bug 또는 selector-drift.
- 테스트 코드가 명백히 틀렸으면(오타, 오용) selector-drift 보다 test-bug 가 우선.

## 출력

`test-results/triage-report.md` 에 쓰고, 콘솔에 요약. 실패 1건당:

```markdown
### <nodeid>
- **TC**: <QA-NN> — <title>
- **분류**: <category>  (확신도: <high|med|low>)
- **근거**:
  - 실패: `<assertion 한 줄>`
  - 기대(TC): <expected 요약>
  - dom_snapshot: <관련 관찰 — 대응 요소 유무>
  - 재현: <재실행 결과 / 안 함>
- **권장 조치**:
  - selector-drift/timing/test-bug → `/repair <nodeid>` (수리 대상)
  - real-bug → **수리 금지. GitHub 이슈로 보고** (아래 초안)
  - spec-change → `/tc-sync` 로 TC 확인 후 사람이 결정
```

`real-bug` 가 하나라도 있으면 이슈 본문 초안을 함께 제시:
제목 `[real-bug] <TC> <한줄>`, 본문에 재현 절차 / 기대(TC 인용) / 실제(aria snapshot 인용) / 관련 아티팩트 경로.

## 하지 말 것

- 테스트·POM·TC·앱 코드 수정 (draft 포함)
- `skip`/`xfail` 추가
- "일단 재시도" 로 넘기기 — timing 이면 timing 이라고 근거를 대고 분류
- 여러 분류 동시 부여 — 가장 근본적인 원인 하나
