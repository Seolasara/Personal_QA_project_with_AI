# playwright-demo

이 폴더의 가드레일/PR 정책/triage 분류 기준은 루트 [../CLAUDE.md](../CLAUDE.md)를 따른다. (중복 기술 금지)

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
  `python ../scripts/gen_test_report.py` → `test-results/test-report.md`.
- 의존성: `requirements.txt` + `playwright install chromium` (버전 핀 고정).
- 테스트 계정: 코드에 하드코딩하지 않는다. `config.py`가 `.env`(gitignore 대상)에서 읽는다.
  최초 1회 `cp .env.example .env` 후 값 채우기. CI는 `.env` 대신 같은 이름의 환경변수를 시크릿으로 주입.

## Playwright 컨벤션
- 셀렉터 우선순위: `[data-test="..."]` > `get_by_role` > `get_by_label`/`get_by_text`. XPath·CSS nth 금지.
- 모든 셀렉터는 Page Object에. 테스트 본문에는 행위와 어설션만.
- `wait_for_timeout` 금지. `expect(...)` 자동 대기 또는 `wait_for_url`/`to_be_visible` 사용.
- Page Object 속성명은 의미 기반 (`proceed_from_cart`, `billing_postcode`). `button1/button2` 금지.
- fixture는 `conftest.py`. cleanup은 `yield` 뒤에.

## 이 폴더의 기술부채
- `pages/catalog_page.py` `CartPage.remove_buttons`: `data-test` 없어 `a.btn.btn-danger` 클래스 셀렉터 사용 중.
- 결제 `checkPayment()`(앱): 첫 Confirm 클릭 시 `of(this.state)`(undefined) 반환 가능. **real-bug 후보 — 재현되면 수리하지 말고 보고.**
- Billing Address: 로그인 사용자 주소 자동채움 + 우편번호 자동조회가 폼 입력과 race. `networkidle` + 로딩 대기로 우회 중.