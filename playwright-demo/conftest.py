import json
from pathlib import Path

import pytest

from pages.catalog_page import CatalogPage, ProductDetailPage
from pages.login_page import LoginPage

HOME_URL = "https://practicesoftwaretesting.com"
SNAPSHOT_DIR = Path(__file__).parent / "test-results" / "dom-snapshots"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 실패 시 DOM 스냅샷을 남긴다 (에이전트 triage/수리 입력용).

    trace.zip 은 전체 DOM 을 담지만 무겁다. 여기서는 셀렉터 수리에 바로 쓰이는
    고신호 정보만 추린다: 현재 URL, 페이지에 실제 존재하는 data-test 속성 목록,
    보이는 얼럿/에러/메시지 텍스트.
    결과: test-results/dom-snapshots/<slug>.json
    """
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    if page is None:
        return

    try:
        data_test = page.locator("[data-test]").evaluate_all(
            "els => Array.from(new Set(els.map(e => e.getAttribute('data-test')).filter(Boolean))).sort()"
        )
        alerts = page.locator(
            ".alert, [role='alert'], [data-test$='error'], [data-test$='-message']"
        ).all_inner_texts()
        snapshot = {
            "nodeid": item.nodeid,
            "url": page.url,
            "title": page.title(),
            "data_test_present": data_test,
            "visible_alerts": [t.strip() for t in alerts if t.strip()],
        }
    except Exception as exc:  # 페이지가 이미 닫혔거나 네비게이션 중
        snapshot = {"nodeid": item.nodeid, "snapshot_error": repr(exc)}

    slug = (
        item.nodeid.replace("/", "_").replace("::", "__")
        .replace("[", "_").replace("]", "").replace(" ", "_")
    )
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    (SNAPSHOT_DIR / f"{slug}.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8"
    )


@pytest.fixture
def login_page(page):
    page.goto(HOME_URL)
    page.get_by_role("link", name="Sign In").click()
    return LoginPage(page)


@pytest.fixture
def loggedin_home(login_page):
    login_page.login("customer2@practicesoftwaretesting.com", "welcome01")
    login_page.page.get_by_title("Practice Software Testing - Toolshop").click()
    return login_page.page


@pytest.fixture
def catalog(loggedin_home) -> CatalogPage:
    return CatalogPage(loggedin_home)


@pytest.fixture
def product_detail(catalog) -> ProductDetailPage:
    """Hammer 카테고리 첫 상품의 상세 페이지까지 진입한 상태."""
    catalog.filter_by_category("Hammer")
    catalog.open_first_product()
    return ProductDetailPage(catalog.page)


@pytest.fixture
def cart_ready(product_detail):
    """상품 상세 진입 상태 (장바구니 담기 직전).

    cleanup: 테스트가 장바구니에 담았으면 비운다.
    """
    yield product_detail

    page = product_detail.page
    page.locator('[data-test="nav-cart"]').click()
    remove_buttons = page.locator("a.btn.btn-danger")
    if remove_buttons.count():
        remove_buttons.first.click()


@pytest.fixture
def cart(product_detail):
    """상품을 장바구니에 담고 체크아웃(장바구니) 페이지로 이동한 상태의 page."""
    product_detail.add()
    product_detail.open_cart()
    return product_detail.page
