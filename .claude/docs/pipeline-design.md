# QA 파이프라인 설계 (스킬과 서브에이전트)
갱신 2026-10-14. 스킬이 단계 순서와 승인 지점을 관리하고, 서브에이전트는 형식이 정해진 작업만 맡습니다. 사라(메인 세션)가 QA 리더로 실행, 분석, 보고를 직접 합니다.

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
   2. `/flow-map <영향 범위>`: 바뀐 화면의 흐름 지도를 갱신합니다(UI만). 분석 결과의 `flow_map_targets`가 있으면 사라가 묻지 않고 이어서 실행합니다(2026-10-14).
   3. `/tc-write`: TC-Writer가 분석 파일과 흐름 지도를 대조해 TC를 추가하거나 고칩니다. 승인 ① 후 시트에 씁니다.
   4. `/script-write`: Script-Writer가 확정된 TC의 스크립트를 씁니다.
   5. Smoke와 회귀: `pytest -m smoke`로 핵심 흐름을 보고, 통과하면 영향 받은 종류의 회귀 TC를 이어서 실행합니다. TC 변경이 없으면 흐름 확인 뒤 한 번의 승인으로 둘 다 실행합니다(2026-10-14).
   6. Iteration 흐름으로 넘어갑니다.
   - 흐름 지도는 smoke를 대신하지 않습니다. 지도는 화면 기록(TC 설계 입력)이고, smoke는 기대결과 대비 Pass/Fail 판정입니다.
   - 서비스 레포가 외부 소유라 웹훅이 없어서, 이벤트 감지는 수동 실행입니다.
2. Iteration 흐름 (최대 3회, 결과 보고서 형식은 `.claude/guides/test-report-format.md`)
   1. `/test-run`: 승인 ② 후 UI, API를 따로 전체 실행하고 보관, Slack 요약, 노션 실행 행을 남깁니다.
   2. `/test-triage`: 사라가 실패를 6분류하고 노션 "이슈 검수"에 real-bug와 안건 후보를 올립니다.
   3. `/test-repair`: 수리 대상(test-bug, selector-drift, timing)을 Script-Writer가 고칩니다. 사용자 검토와 별개로 진행합니다.
   4. 승인 ③: 사용자가 노션에서 검토합니다. "검토 끝"이면 아래가 자동으로 이어집니다.
   5. `/issue-register`: Issue-Reporter가 승인된 real-bug를 Jira에 등록하고, 사라가 xfail을 풀고 `issue` 마커를 붙입니다.
   6. `/report-write`: 사라가 Iteration 보고서 초안을 쓰고, 승인 ④ 후 게시합니다. 게시 후 lessons 회고를 합니다.
   - Iteration 2, 3은 `issue` 마커 테스트를 반드시 포함해 재검증합니다.
3. CI 흐름 (GitHub Actions, 2026-10-13)
   - API: `.github/workflows/api-regression.yml`을 [Run workflow]로 수동 실행합니다. 사이트 사전 점검 → `qa-tests` 이미지 빌드 → 회귀 TC(`scripts/regression_set.py`) 또는 전체 실행 → 아티팩트(30일)와 Slack 요약 순서입니다. 계정은 저장소 Secrets로만 주입합니다.
   - UI: GitHub 러너에서는 Cloudflare 봇 검증 페이지가 떠서 실행할 수 없습니다(2026-10-14 확인). 워크플로우는 비활성화했고 UI는 로컬 컨테이너로 실행합니다.
   - CI 헤드리스에서는 Confluence를 건드리지 않습니다(루트 가드레일).
4. flaky 대책 (2026-10-13)
   1. 조건 대기 수리: 원인이 테스트 타이밍이면 `/test-repair`로 응답이나 화면 상태를 기다리게 고칩니다(ex: 장바구니 이동 뒤 `open_cart_loaded()`).
   2. 환경 시간 초과 재시도: 각 폴더 `pytest.ini`의 `pytest-rerunfailures` 설정이 환경 시간 초과만 최대 2회 다시 실행합니다. 재시도 후 통과는 `rerun`(flaky)으로 따로 셉니다. 남은 error는 `/test-run`의 수동 재실행 규칙을 따릅니다.
   3. 격리(quarantine): 원인을 고치기 전까지 `quarantine` 마커를 붙인 테스트는 CI에서 빌드를 막지 않는 별도 단계로 돌립니다. 지금 붙은 테스트는 없습니다.

## 3. 스킬 (`.claude/skills/`)
1. `/spec-analysis`: 스펙과 소스 분석, 변경분 분석(Document-Analyzer, fork)
2. `/flow-map`: UI 흐름 지도(`.claude/docs/flows/ui-flows.md`) 작성과 갱신(sonnet). 데모 사이트 결제 확정은 허용합니다.
3. `/tc-write`: TC 초안, 기계 점검, 보고, 시트 쓰기(TC-Writer, fork)
4. `/script-write`: 스크립트 작성과 기계 점검(Script-Writer)
5. `/test-run`: 전체 실행, 보관, Slack, 노션 기록(서브에이전트 없음)
6. `/test-triage`: 실패 분류, 백로그 대조, 노션 이슈 검수, 사용자 검토 반영(opus, 사라 직접)
7. `/test-repair`: 수리 대상 실패를 원인에 맞게 수리하고 `repair_guard.py`로 실패 숨김을 점검(Script-Writer, fork)
8. `/issue-register`: 승인된 real-bug의 Jira 등록(Issue-Reporter)
9. `/report-write`: Iteration·최종 결과 보고서(사라 직접)

## 4. 서브에이전트 (`.claude/agents/`)
1. Document-Analyzer: 스펙, 소스 분석과 변경 영향 분석
2. TC-Writer(sonnet): TC 초안. 흐름 지도와 대조하고 Playwright로 직접 따라가지 않습니다.
3. Script-Writer: 스크립트 작성과 실패 수리. 따라갈 수 없는 TC는 "TC 수정 필요"로 돌려보냅니다.
4. Issue-Reporter(sonnet): 노션 Jira 초안을 그대로 Jira에 옮기고 키를 기록합니다.

## 5. 남은 것
1. 수리와 LLM judge (목표 2)
   - 수리: `/test-repair`로 만들었고(2026-10-10), UI_25 등 장바구니 타이밍 flaky 수리에 처음 썼습니다(2026-10-13).
   - judge: 보류합니다(2026-10-10 사용자 결정). TC를 늘리고 CI로 돌려 보면서 필요성이 확인되면 설계합니다. 만들 때는 수리 채점부터 시작하고, 실패 분류는 real-bug를 test-bug로 내리는 판정을 judge가 혼자 확정하지 못하게 합니다.
2. Test-Runner: 자동화하지 않은 수동 TC를 Playwright MCP로 실행합니다. 수동 TC가 생길 때까지 보류합니다.
3. CI 자동 트리거: 지금은 수동 실행만 있습니다. PR smoke, 야간 API 회귀 순서로 붙입니다. 서비스 레포 변경 감지도 후속 과제입니다.
4. 로컬 Toolshop(docker-compose): CI에서 앱과 DB를 직접 띄우면 사이트 지연, DB 리셋, Cloudflare 차단이 함께 해소됩니다. UI CI는 이 작업 뒤에 다시 켭니다.
