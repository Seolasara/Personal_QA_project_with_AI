# playwright-demo

UI e2e(Playwright) 테스트의 구조와 규칙이다. 프로젝트 공통 QA 규칙은 루트 [CLAUDE.md](../CLAUDE.md)를 따른다.

## 스펙 기준
- UI 스펙은 `v5.md`(Sprint 5 User Stories & Acceptance Criteria, 2026-10-08 받음)다. 기능별 사본은 `.claude/docs/specs/v5/`, 분석은 `.claude/docs/spec analysis/ui/`에 있다.
- 화면 흐름(진입 경로, 상태 조건, 실제 UI 표기)은 흐름 지도 `.claude/docs/flows/ui-flows.md`를 본다.
- QA plan: wiki "UI Test QA Plan"(Confluence 65702)
- TC ID 접두어 `UI_`, 마커 `@pytest.mark.tc("UI_NN")`, 시트: UI 스프레드시트 https://docs.google.com/spreadsheets/d/1G7ICKjMaS2MvQH2xS0IjcS-VQAAA_N1_YTQ8qtF0k44/edit?usp=sharing 의 `UI-TC` 탭
- Jira: 레이블 `ui`, 에픽 QA-5(UI 테스트 이슈). 증거는 스크린샷.
- 계정: customer2(`TOOLSHOP_EMAIL`)를 쓴다. API 계정과 분리해 계정 잠금이 서로 영향 주지 않게 한다.

## 테스트 실행
```bash
cd playwright-demo
source .venv/bin/activate
pytest
pytest -m smoke     # 핵심 흐름 5개(Iteration 진입 판정, PR 게이트)
pytest -m tc        # TC 연결된 테스트만
pytest -m "not spec_undefined"   # /test-run 전체 실행 기준
pytest tests/payment_test.py -k checkout
```
- 대상 환경: 기본은 운영 사이트다. 로컬 Toolshop(결함 주입 측정 등)에 돌릴 때만 스크립트를 고치지 않고 환경변수로 주소를 바꾼다. API 테스트는 `API_BASE_URL`(`api-demo/config.py`).
  - `TOOLSHOP_SITE_URL=http://localhost:4200 TOOLSHOP_API_URL=http://localhost:8091 pytest --base-url http://localhost:4200`
- 실패 시 `test-results/`에 trace(zip)/스크린샷.
- 머신리더블: `test-results/report.json`. 사람용: `test-results/report.html`,
  `python3 ../scripts/gen_test_report.py --type ui` → `test-results/test-report.md`.
- 의존성: `playwright-demo/requirements.txt` + `playwright install chromium` (버전 핀 고정).
- 컨테이너 실행: 루트 `Dockerfile`의 이미지 `qa-tests`. 명령은 `.claude/skills/test-run/SKILL.md` 3번(Iteration 3부터 기본).
- 테스트 계정: 코드에 하드코딩하지 않는다. `config.py`가 `.env`(gitignore 대상)에서 읽는다.
  최초 1회 `cp .env.example .env` 후 값 채우기. CI는 `.env` 대신 같은 이름의 환경변수를 시크릿으로 주입.
- CI: `.github/workflows/ui-regression.yml`은 비활성 상태다. GitHub 러너에서 Cloudflare 봇 검증 페이지가 떠서 실행할 수 없다(2026-10-14). UI는 로컬 컨테이너로 실행한다.
  - trace(`trace.zip`)에는 로그인 입력(계정 이메일, 비밀번호)이 남는다. 공개 저장소 아티팩트나 외부 채널에 올리지 않는다.
- 재시도와 격리
  - `pytest.ini`의 `--reruns=2 --only-rerun`이 `Page.goto`, `Page.wait_for_url`, 응답 대기 시간 초과만 다시 실행한다. 어설션 실패는 재시도하지 않는다.
  - 계정 잠금(로그인 실패 UI_02~06)이나 인보이스(결제 확정 UI_36, UI_37)가 생기는 테스트는 `@pytest.mark.flaky(reruns=0)`로 재시도에서 뺀다. 같은 위험이 있는 테스트를 새로 쓰면 같이 붙인다.
  - `quarantine` 마커: 원인을 고치기 전까지 격리한 flaky 테스트. CI에서 빌드를 막지 않는 별도 단계로 돈다.

## Playwright 컨벤션
- 셀렉터 우선순위: `[data-test="..."]` > `get_by_role` > `get_by_label`/`get_by_text`. XPath·CSS nth 금지.
- 모든 셀렉터는 Page Object에. 테스트 본문에는 행위와 어설션만.
- `wait_for_timeout` 금지. `expect(...)` 자동 대기, `wait_for_url`, 응답 대기(`expect_response`)를 쓴다.
- UI 전용 수리 금지: 검증 대상 셀렉터를 항상 존재하는 요소로 바꿔치기(공통 금지는 루트 가드레일과 `/test-repair`).
- Page Object 속성명은 의미 기반 (`proceed_from_cart`, `postcode`). `button1/button2` 금지.
- fixture는 `conftest.py`. cleanup은 `yield` 뒤에.
- Playwright MCP는 새 화면의 셀렉터와 동작을 확인하는 탐색에만 쓴다. 최종 산출물은 재실행 가능한 pytest 코드다. MCP가 없으면 임시 probe 스크립트로 확인하고 repo에 남기지 않는다.

## 데이터와 계정 주의
- 장바구니는 브라우저 context의 sessionStorage(`cart_id`)에 묶여 테스트마다 새로 시작하므로 따로 정리하지 않는다.
- 장바구니로 이동한 뒤 행을 확인하는 흐름은 `open_cart_loaded()`로 장바구니 조회 응답(`GET /carts/{id}`)까지 기다린다. 장바구니 화면이 지연 로드된 뒤 조회해서, 사이트가 느리면 행 확인이 먼저 끝난다(2026-10-13). 빈 장바구니로 가는 흐름에는 쓰지 않는다(조회 요청이 없다).
- 결제를 확정하는 테스트(UI_36, UI_37, smoke의 UI_36)는 실행할 때마다 인보이스를 남긴다. 삭제할 수 없으니 반복 실행하지 않는다.
- 로그인 실패 TC(UI_02~06)는 연속 재실행하지 않는다(3회 실패 시 계정 잠금). 잠기면 백로그 #8로 해제한다.
- 데모 DB 리셋 중에는 정상 계정 로그인도 401이 날 수 있다(env, 백로그 #17). 관리자 API로 `failed_login_attempts`가 0인지(잠금 위험 없음) 확인한 뒤 1회 재실행한다(2026-10-10 확인).

## 이 폴더의 기술부채 (상세는 백로그)
- #5 장바구니 삭제 버튼은 `data-test`가 없어 `a.btn.btn-danger` 클래스 셀렉터를 쓴다.
- #7 Billing Address 자동채움과 우편번호 조회 race: Street, City, State는 직접 입력하지 않고 `/postcode-lookup` 응답을 기다려 조회 결과를 쓴다.
- #6 결제 `checkPayment()` undefined 반환 가능성(판단 보류, 2026-10-10 미재현). 재현되면 수리하지 말고 보고한다.
