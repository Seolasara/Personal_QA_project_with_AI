# playwright-demo

UI e2e(Playwright) 테스트의 구조와 규칙이다. 프로젝트 공통 QA 규칙은 루트 [CLAUDE.md](../CLAUDE.md)를 따른다.

## 스펙 기준
- UI 스펙은 `v5.md`(Sprint 5 User Stories & Acceptance Criteria)다. 기능별로 나눈 사본: `.claude/docs/specs/v5/`(목록은 `00_index.md`) (원본: testsmith-io/practice-software-testing `docs/user-stories/v5.md`, 2026-10-08 받음). 근거는 `.claude/docs/spec analysis/ui/`에 있다.
- QA plan: wiki "UI Test QA Plan"(Confluence 65702)
- TC ID 접두어 `UI_`, 마커 `@pytest.mark.tc("UI_NN")`, 시트: UI 스프레드시트 https://docs.google.com/spreadsheets/d/1G7ICKjMaS2MvQH2xS0IjcS-VQAAA_N1_YTQ8qtF0k44/edit?usp=sharing 의 `UI-TC` 탭
- Jira: 레이블 `ui`, 에픽 QA-5(UI 테스트 이슈). 증거는 스크린샷.
- 계정: customer2(`TOOLSHOP_EMAIL`)를 쓴다. API 계정과 분리해 계정 잠금이 서로 영향 주지 않게 한다.

## 테스트 실행
```bash
cd playwright-demo
source .venv/bin/activate
pytest
pytest -m smoke     # PR 게이트용 빠른 서브셋
pytest -m tc        # TC 연결된 테스트만
pytest tests/payment_test.py -k checkout
```
- 실패 시 `test-results/`에 trace(zip)/스크린샷.
- 머신리더블: `test-results/report.json`. 사람용: `test-results/report.html`,
  `python3 ../scripts/gen_test_report.py --type ui` → `test-results/test-report.md`.
- 의존성: `requirements.txt` + `playwright install chromium` (버전 핀 고정).
- 테스트 계정: 코드에 하드코딩하지 않는다. `config.py`가 `.env`(gitignore 대상)에서 읽는다.
  최초 1회 `cp .env.example .env` 후 값 채우기. CI는 `.env` 대신 같은 이름의 환경변수를 시크릿으로 주입.

## Playwright 컨벤션
- 셀렉터 우선순위: `[data-test="..."]` > `get_by_role` > `get_by_label`/`get_by_text`. XPath·CSS nth 금지.
- 모든 셀렉터는 Page Object에. 테스트 본문에는 행위와 어설션만.
- 수리 시 금지: `wait_for_timeout` 추가/증량, 검증 셀렉터를 항상 존재하는 것으로 바꿔치기.
- `wait_for_timeout` 금지. `expect(...)` 자동 대기 또는 `wait_for_url`/`to_be_visible` 사용.
- Page Object 속성명은 의미 기반 (`proceed_from_cart`, `billing_postcode`). `button1/button2` 금지.
- fixture는 `conftest.py`. cleanup은 `yield` 뒤에.
- 장바구니는 브라우저 context의 sessionStorage(`cart_id`)에 묶여 테스트마다 새로 시작한다.
- Playwright MCP는 새 화면의 셀렉터와 동작을 확인하는 탐색에만 쓴다. 최종 산출물은 재실행 가능한 pytest 코드다. MCP가 없으면 임시 probe 스크립트로 확인하고 repo에 남기지 않는다.

## 이 폴더의 기술부채
- `pages/catalog_page.py` `CartPage.remove_buttons`: `data-test` 없어 `a.btn.btn-danger` 클래스 셀렉터 사용 중.
- 결제 `checkPayment()`(앱): 첫 Confirm 클릭 시 `of(this.state)`(undefined) 반환 가능. **real-bug 후보 — 재현되면 수리하지 말고 보고.**
- Billing Address: 로그인 사용자 주소 자동채움 + 우편번호 자동조회가 폼 입력과 race(백로그 #7). Street, City, State는 직접 입력하지 않고 `/postcode-lookup` 응답을 기다려 조회 결과를 쓴다.

## 아직 안 한 것
- `scripts/script_lint.py`, `tc_marker_check.py`, `gen_test_report.py`는 UI와 API만 다룬다. 새 테스트 종류가 생기면 확장한다.
