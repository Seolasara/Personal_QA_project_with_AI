# Personal QA Project

개인 QA 프로세스 + QA AI 에이전트 + LLM judge 평가를 하나로 묶은 프로젝트.
테스트 대상은 공개 데모 사이트 <https://practicesoftwaretesting.com> (Toolshop).

## 목적

1. 테스트케이스(TC)를 코드로 관리하고 Confluence와 동기화한다.
2. Playwright(pytest) UI 자동화 스크립트를 유지한다.
3. 에이전트가 테스트 실패를 분류(triage)하고, 스펙/셀렉터 변경으로 인한 실패를 수리한다.
4. LLM judge가 에이전트의 수리 결과를 채점한다.

## 레포 구조

| 경로 | 내용 |
|---|---|
| `testcases/*.md` | TC 원본. yaml frontmatter + 마크다운 본문. **이게 원본, Confluence는 렌더 뷰.** |
| `testplan.md` | 테스트 플랜 |
| `traceability.md` | TC ↔ 테스트 노드ID 매트릭스 (마커 스캔으로 생성, 직접 편집 금지) |
| `scripts/` | 유지보수 스크립트 (`gen_traceability.py` 등) |
| `playwright-demo/` | pytest + Playwright 스크립트. **pytest는 이 디렉토리를 rootdir로 실행.** |
| `playwright-demo/pages/` | Page Object. 셀렉터는 전부 여기 모은다. |
| `playwright-demo/tests/` | 테스트. 셀렉터를 테스트 본문에 직접 쓰지 않는다. |
| `eval/` | 결함주입 eval set + judge 골든셋 |
| `.claude/skills/`, `.claude/commands/` | 에이전트 워크플로 |

## 테스트 실행

```bash
cd playwright-demo
source .venv/bin/activate            # 또는 .venv/bin/pytest 직접 호출
pytest                               # 전체
pytest -m smoke                      # PR 게이트용 빠른 서브셋
pytest -m tc                         # TC 연결된 테스트만
pytest tests/payment_test.py -k checkout
```

- 실패 시 `test-results/`에 trace(zip)와 스크린샷이 남는다.
- 머신리더블 결과: `test-results/report.json` (pytest-json-report).
- 의존성: `requirements.txt` + `playwright install chromium`. playwright 버전은 핀 고정.

## TC 포맷

`testcases/QA-NN.md` — ID는 Confluence "Test Case 설계" 표(page 360539)와 맞춰 `QA-01` ~ 유지.

```markdown
---
id: QA-12
title: Confirm 버튼 클릭 시 결제 완료 확인
priority: P1            # P1(상) / P2(중) / P3(하)
component: payment     # main | login | product | cart | payment | logout
confluence_page_id: 360539            # sync 대상 (없으면 미발행)
automation:
  status: automated                   # automated | manual | planned
  test: playwright-demo/tests/payment_test.py::test_payment_checkout
---
## 조건
- ...
## 스텝
1. <행동> → <기대결과>
## 비고
- ...
```

테스트 쪽에서 `@pytest.mark.tc("QA-12")`로 역참조한다. `python scripts/gen_traceability.py`로
`traceability.md`를 재생성하며, frontmatter의 `test`와 실제 마커가 어긋나면 non-zero로 종료한다(CI 게이트).
TC를 바꾸면 연결된 테스트의 어설션이 여전히 기대결과와 맞는지 확인한다.

## Playwright 컨벤션

- 셀렉터 우선순위: `[data-test="..."]` > `get_by_role` > `get_by_label`/`get_by_text`. XPath·CSS nth 금지.
- 모든 셀렉터는 Page Object에 둔다. 테스트 본문에는 행위와 어설션만.
- `wait_for_timeout` 금지. `expect(...)`의 자동 대기 또는 `wait_for_url`/`to_be_visible` 사용.
- Page Object의 속성 이름은 의미 기반으로 (`proceed_from_cart`, `billing_postcode`). `button1/button2` 금지.
- fixture는 `conftest.py`. cleanup은 `yield` 뒤에.

## Confluence 연동

- `.mcp.json`에 Atlassian 공식 Remote MCP 서버 등록됨 (`https://mcp.atlassian.com/v2/mcp`, OAuth).
- 최초 사용: Claude Code에서 `/mcp` → `atlassian` → Authenticate (브라우저 OAuth).
- 동기화 방향: **원본은 `testcases/*.md`.** `/tc-sync push`로 Confluence에 발행, `/tc-sync pull`로 Confluence 스펙 변경을 repo에 반영(자동 수리 금지, `needs-review` 표시).
- CI 헤드리스에서는 OAuth 불가 → CI는 Confluence를 건드리지 않는다. 나중에 필요하면 API 토큰 + Confluence REST를 별도 시크릿으로.

## 에이전트 가드레일 (중요)

- 실패는 반드시 **먼저 분류**한다: `real-bug` / `selector-drift` / `timing` / `spec-change` / `test-bug`.
- **`real-bug`로 분류되면 코드를 수정하지 않는다.** 이슈/PR에 근거와 함께 보고만 한다.
- 수리 시 **금지**: 어설션 삭제·약화, `wait_for_timeout` 추가/증량, `skip`/`xfail` 마킹, 검증 셀렉터를 항상 존재하는 것으로 바꿔치기.
- 에이전트는 **draft PR만** 생성한다. main 직접 push·머지·auto-merge 금지.
- judge는 항상 **별도 세션**에서 실행한다 (수리 에이전트의 대화 맥락을 물려주지 않는다).
- CI 헤드리스에서는 Confluence(MCP OAuth)를 건드리지 않는다. repo 수정 + PR까지만.

## 알려진 기술부채 (정리 대상)

- `utils/`: 비어 있음.
- `pages/catalog_page.py` `CartPage.remove_buttons`: 장바구니 행 삭제 버튼에 앱이 `data-test`를 안 줘서 `a.btn.btn-danger` 클래스 셀렉터 사용 중.
- 결제 `checkPayment()`(앱): 첫 Confirm 클릭 시 `of(this.state)`(undefined)를 반환 → 상황에 따라 Confirm 2회가 필요할 수 있음. **real-bug 후보** — 재현되면 수리하지 말고 보고.
- Billing Address: 로그인 사용자 주소 자동채움(`getDetails`) + 우편번호 자동조회가 폼 입력과 race. 현재는 `wait_for_load_state("networkidle")` + 로딩 대기로 우회.

### 정리 완료 (2026-09-08, PR #2)

- ~~`filling_address()` `self.city.fill(state)` 버그~~ → 수정, `fill_billing_address()`로 이름 변경.
- ~~`button1/button2/button3` 동일 셀렉터~~ → `proceed_from_cart/signin/address` + `[data-test="proceed-1/2/3"]`.
- ~~`conftest.py` 도달 불가 `return page`~~ → 제거.
- ~~`product_search_test.py`, `add_to_cart_test.py` 셀렉터 흩어짐~~ → `pages/catalog_page.py`로 집약.
- ~~`login_page.login()`이 실패 케이스에도 `/account` URL 대기~~ → `submit()`/`login()` 분리.
