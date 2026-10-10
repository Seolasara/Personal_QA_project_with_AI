# QA 파이프라인 설계 (스킬과 서브에이전트)
갱신 2026-10-10. 스킬이 단계 순서와 승인 지점을 관리하고, 서브에이전트는 형식이 정해진 작업만 맡습니다. 사라(메인 세션)가 QA 리더로 실행, 분석, 보고를 직접 합니다.

## 1. 공통 원칙
1. 역할
   - 사라(메인 세션): 테스트 실행, 실패 분류와 원인 분석, 결과 보고서, 사용자 보고와 승인 요청
   - 서브에이전트: 형식이 정해진 일(문서 분석, TC 초안, 스크립트, Jira 등록)만 합니다. 다른 서브에이전트를 부를 수 없어서 주고받기는 스킬과 사라가 중계합니다.
2. 승인 지점, 판단 기준, 산출물 위치, 분류 체계는 루트 `CLAUDE.md`에 있고, 이 문서에 다시 쓰지 않습니다.
3. 스킬과 서브에이전트를 고르는 기준
   - 순서와 절차를 고정할 일은 스킬로 둡니다.
   - 독립된 판단, 권한 제한, 모델 지정이 필요한 일만 서브에이전트로 둡니다.
4. 사용자 판단이 바뀐 곳은 `.claude/docs/lessons.md`에 쌓고, Iteration 회고에서 2회 이상 반복된 유형만 규칙으로 올립니다.

## 2. 흐름
1. 변경 이벤트 흐름 (새 기능, 서비스 레포 PR, 스펙 변경)
   1. `/spec-analysis update`: Document-Analyzer가 변경 영향(기능, 범위, 리스크)을 분석합니다.
   2. `/flow-map <영향 범위>`: 바뀐 화면의 흐름 지도를 갱신합니다(UI만).
   3. `/tc-write`: TC-Writer가 분석 파일과 흐름 지도를 대조해 TC를 추가하거나 고칩니다. 승인 ① 후 시트에 씁니다.
   4. `/script-write`: Script-Writer가 확정된 TC의 스크립트를 씁니다.
   5. Smoke: `pytest -m smoke`로 핵심 흐름이 통과하는지 보고 Iteration 진입을 판정합니다.
   6. Iteration 흐름으로 넘어갑니다.
   - 흐름 지도는 smoke를 대신하지 않습니다. 지도는 화면 기록(TC 설계 입력)이고, smoke는 기대결과 대비 Pass/Fail 판정입니다.
   - 서비스 레포가 외부 소유라 웹훅이 없어서, 이벤트 감지는 수동 실행입니다.
2. Iteration 흐름 (최대 3회, 결과 보고서 형식은 `.claude/guides/test-report-format.md`)
   1. `/test-run`: 승인 ② 후 UI, API를 따로 전체 실행하고 보관, Slack 요약, 노션 실행 행을 남깁니다.
   2. `/test-triage`: 사라가 실패를 6분류하고 노션 "이슈 검수"에 real-bug와 안건 후보를 올립니다.
   3. 승인 ③: 사용자가 노션에서 검토합니다. "검토 끝"이면 아래가 자동으로 이어집니다.
   4. `/issue-register`: Issue-Reporter가 승인된 real-bug를 Jira에 등록하고, 사라가 xfail을 풀고 `issue` 마커를 붙입니다.
   5. `/report-write`: 사라가 Iteration 보고서 초안을 쓰고, 승인 ④ 후 게시합니다. 게시 후 lessons 회고를 합니다.
   - Iteration 2, 3은 `issue` 마커 테스트를 반드시 포함해 재검증합니다.

## 3. 스킬 (`.claude/skills/`)
1. `/spec-analysis`: 스펙과 소스 분석, 변경분 분석(Document-Analyzer, fork)
2. `/flow-map`: UI 흐름 지도(`.claude/docs/flows/ui-flows.md`) 작성과 갱신(sonnet). 데모 사이트 결제 확정은 허용합니다.
3. `/tc-write`: TC 초안, 기계 점검, 보고, 시트 쓰기(TC-Writer, fork)
4. `/script-write`: 스크립트 작성과 기계 점검(Script-Writer)
5. `/test-run`: 전체 실행, 보관, Slack, 노션 기록(서브에이전트 없음)
6. `/test-triage`: 실패 분류, 백로그 대조, 노션 이슈 검수, 사용자 검토 반영(opus, 사라 직접)
7. `/issue-register`: 승인된 real-bug의 Jira 등록(Issue-Reporter)
8. `/report-write`: Iteration·최종 결과 보고서(사라 직접)

## 4. 서브에이전트 (`.claude/agents/`)
1. Document-Analyzer: 스펙, 소스 분석과 변경 영향 분석
2. TC-Writer(sonnet): TC 초안. 흐름 지도와 대조하고 Playwright로 직접 따라가지 않습니다.
3. Script-Writer: 스크립트 작성. 따라갈 수 없는 TC는 "TC 수정 필요"로 돌려보냅니다.
4. Issue-Reporter(sonnet): 노션 Jira 초안을 그대로 Jira에 옮기고 키를 기록합니다.

## 5. 남은 것
1. 수리 + LLM judge (목표 2)
   - 수리: test-triage에서 `test-bug`, `selector-drift`, `timing`으로 분류된 실패를 고치는 단계입니다. 지금은 사라가 직접 고칩니다. 반복되면 `/test-repair` 스킬(수리 에이전트)로 고정합니다.
   - judge: 수리 결과(diff, 실패 로그, TC)를 받아 "실패를 숨기지 않았는지, 원인에 맞는 수리인지"를 채점합니다. 루트 규칙대로 별도 세션에서 실행합니다.
2. Test-Runner: 자동화하지 않은 수동 TC를 Playwright MCP로 실행합니다. 수동 TC가 생길 때까지 보류합니다.
3. Smoke 대상 지정: `smoke` 마커는 `pytest.ini`에 등록되어 있지만 붙은 테스트가 없습니다. 핵심 흐름 TC에 마커를 붙여야 Smoke 단계가 동작합니다.
4. 정기 자동 실행(CI, 서비스 레포 변경 감지): 후속 과제입니다.
