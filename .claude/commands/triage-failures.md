---
description: 최근 pytest 실패를 real-bug / selector-drift / timing / spec-change / test-bug 로 분류 (수정 안 함)
argument-hint: "[nodeid 조각 - 특정 실패만]"
---

`test-triage` 스킬을 사용해 최근 테스트 실패를 분류한다. **코드는 수정하지 않는다.**

대상: `$ARGUMENTS` (비어 있으면 `test-results/report.json`의 모든 실패)

## 절차

1. `test-triage` 스킬을 로드한다.
2. `playwright-demo/.venv/bin/python scripts/failures.py $ARGUMENTS` 실행.
   - `report.json` 이 없거나 오래됐으면 사용자에게 `pytest` 재실행을 먼저 요청.
3. 스킬의 "입력 수집" 순서대로 각 실패에 대해:
   TC(`testcases/<tc>.md`) → 테스트 함수 → Page Object → `dom_snapshot` 을 읽는다.
4. `timing` 이 의심되면 해당 nodeid 를 1회 재실행해 재현성을 확인.
5. 스킬의 분류 기준으로 각 실패를 **정확히 하나**로 분류하고 확신도를 매긴다.
6. `test-results/triage-report.md` 작성 + 콘솔 요약.
7. `real-bug` 가 있으면 GitHub 이슈 본문 초안을 제시 (이슈 생성은 사용자 승인 후).

## 제약

- 테스트 / POM / TC / 앱 코드 수정 금지 (draft PR 포함).
- 분류가 애매하면 확신도를 `low` 로 낮추고 근거를 상세히. 추측으로 단정하지 않는다.
- 이 커맨드의 산출물은 `triage-report.md` 하나. 수리는 `/repair` 가 따로 한다.
