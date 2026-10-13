---
name: test-repair
description: 실패 수리. /test-triage가 test-bug, selector-drift, timing으로 분류한 실패를 고칠 때나 /test-repair를 실행할 때 쓴다. Script-Writer가 원인에 맞게 테스트 코드를 고치고, 실패를 숨기지 않았는지 diff로 점검한 뒤 보고한다.
context: fork
agent: Script-Writer
argument-hint: "[test-runs/<일시>-<ui|api> | ui|api <TC ID>:<분류> ...]"
---

# /test-repair
대상: `$ARGUMENTS`
- `test-runs/<일시>-<ui|api>`: 그 보관본 `triage-report.md`에서 "조치: 수리 대상"인 묶음 전부
- `ui|api <TC ID>:<분류> ...`: 사라가 triage한 뒤 직접 넘긴 실패(ex: `ui UI_24:selector-drift`)
- 비어 있으면 대상을 묻는다.
작업 순서와 업무 규칙은 `.claude/agents/Script-Writer.md`를 따르고, 수리 방법은 아래 규칙을 따른다. 이 스킬은 실패를 고치는 일만 한다. TC가 바뀌어 스크립트를 맞추는 일은 `/script-write`다.

## 1. 원칙
- 분류가 test-bug, selector-drift, timing인 실패만 고친다. 분류가 없거나 real-bug, spec-change, env, 안건이면 고치지 않고 보고한다(분류는 `/test-triage`가 먼저).
- 기대값의 기준은 TC 시트의 기대결과다. 라이브 동작에 맞춰 어설션을 바꾸지 않는다.
- 금지: 어설션 삭제·약화, `skip`, 새 `xfail`, 고정 대기(`wait_for_timeout`, `sleep`), 재시도로 통과 만들기(예외: `pytest.ini`의 환경 시간 초과 한정 재시도, 2026-10-13 사용자 결정. 테스트 코드에 재시도를 넣는 것은 계속 금지), timeout만 늘리는 수리
- 고칠 수 있는 것은 테스트 폴더의 코드(테스트, Page Object, client, schema, fixture)뿐이다. TC 시트, 백로그, 스펙 분석은 고치지 않는다.

## 2. 분류별 수리 방법
1. selector-drift (UI)
   - 흐름 지도(`.claude/docs/flows/ui-flows.md`)와 라이브 화면(`browser_snapshot`)으로 이름만 바뀐 대응 요소를 찾는다.
   - Page Object의 셀렉터만 바꾼다. `data-test`를 우선 쓴다. 테스트 본문은 고치지 않는다.
   - 대응 요소가 없으면 고치지 않는다(3번 멈춤 조건).
2. timing
   - 테스트가 무엇을 기다려야 하는지(응답, 요소 상태, 값 변화) 찾아 그 조건을 명시적으로 기다리게 바꾼다. ex: `/postcode-lookup` 응답 대기
   - 원인을 모르면 고치지 않고 trace 근거와 함께 보고한다.
3. test-bug
   - TC 기대결과와 코드를 대조해 틀린 코드를 고친다. ex: 헤더 누락, id 하드코딩, 잘못 옮긴 기대값
   - 어설션의 기대값을 바꾸면 보고에 TC 시트 기대결과 원문을 근거로 붙인다.

## 3. 멈춤 조건 (고치지 않고 보고)
- 수리 중 앱이 TC나 스펙과 다르게 동작한다는 증거가 나왔다 → "real-bug 의심"으로 근거와 함께 보고한다. 사라가 `/test-triage`로 다시 분류한다.
- 어설션 기대값을 바꿔야 하는데 TC 시트에 근거가 없다.
- TC 스텝대로 따라갈 수 없다 → "TC 수정 필요"
- 공유 파일의 구조 변경이 필요하다 → Script-Writer 워크플로 4번대로 계획을 보고한다.

## 4. 점검
1. `git diff -U0 -- playwright-demo api-demo | python3 scripts/repair_guard.py`: 오류 0건이어야 한다. "주의"(기대값 변경, timeout 변경)는 보고의 "사람 확인 필요"에 옮긴다.
2. `python3 scripts/script_lint.py <고친 테스트 파일>`: 오류 0건
3. 고친 테스트만 단독으로 3회 실행해 모두 같은 결과인지 본다.
   - 결제를 확정하는 TC와 로그인 실패 TC(계정 잠금 위험)는 1회만 실행한다.
4. xfail이 걸린 테스트를 건드렸으면 `--runxfail`로 1회 실행해 실패 원인이 백로그 항목과 같은지 확인한다.

## 5. 기록과 보고
- 보관본이 대상이면 `<대상>/repair-report.md`에 묶음마다 쓴다.
```markdown
### <TC ID> — <분류>
- 원인: <한 줄>
- 수정: <파일:함수> / <바꾼 내용 요지>
- 근거: <TC 기대결과 원문, trace, 흐름 지도 등>
- 점검: repair_guard 오류 <N>, 주의 <N> / script_lint 오류 <N> / 실행 <통과 N회/전체 N회>
- 사람 확인 필요: 없음 | <기대값 변경, 멈춤 사유>
```
- 보고(Script-Writer "결과 보고" 형식에 더해)
  - 수리 완료, 멈춤(real-bug 의심, TC 수정 필요), 사람 확인 필요 목록을 나눠 쓴다.
  - 수리 기록은 judge를 만들 때 채점 데이터로 쓰므로 지우지 않는다.

## 6. 다음 단계 (사라, 메인 세션)
- "사람 확인 필요"와 멈춤 건을 사용자에게 올린다. real-bug 의심은 `/test-triage`로 다시 분류한다.
- 노션 "테스트 실행" 행의 "근거와 자료"에 수리 결과 한 줄을 적고, Slack 실행 스레드에 `*수리 결과*` 답글을 올린다.
- 커밋 단위와 메시지를 제안하고 승인받아 커밋한다.
