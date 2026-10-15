import json
from pathlib import Path

import pytest
from playwright.sync_api import expect

from config import SITE_URL, TOOLSHOP_EMAIL, TOOLSHOP_PASSWORD
from pages.catalog_page import CatalogPage, ProductDetailPage
from pages.login_page import LoginPage

HOME_URL = SITE_URL
SNAPSHOT_DIR = Path(__file__).parent / "test-results" / "dom-snapshots"


def pytest_html_results_table_header(cells):
    cells.insert(1, "<th>TC</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(1, f"<td>{getattr(report, 'tc_id', '') or ''}</td>")


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

    # TC 마커를 리포트에 실어 pytest-html 표의 TC 컬럼에 노출
    marker = item.get_closest_marker("tc")
    report.tc_id = marker.args[0] if marker else ""

    # call 실패 + fixture(setup) 실패 모두 대상
    if report.when not in ("call", "setup") or not report.failed:
        return

    # setup 도중 실패면 funcargs 가 아직 없을 수 있음 → best effort.
    # 그 경우 pytest-playwright 의 trace.zip(retain-on-failure)이 폴백.
    try:
        page = item.funcargs.get("page")
    except Exception:
        page = None
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
def blocked_login_requests(login_page):
    """로그인 페이지 진입 상태에서 로그인 API 요청을 기록하고 차단한다.

    클라이언트 검증 TC(공란, 비밀번호 길이)용. 요청이 서버에 닿지 않아
    클라이언트 검증이 깨져도 로그인 실패가 쌓여 계정이 잠기지 않는다(3회 잠금).
    반환값: 시도된 로그인 요청 URL 목록 (비어 있으면 미전송).
    """
    attempts = []

    def _block(route):
        attempts.append(route.request.url)
        route.abort()

    login_page.page.route(LoginPage.LOGIN_API_PATTERN, _block)
    yield attempts
    login_page.page.unroute(LoginPage.LOGIN_API_PATTERN, _block)


@pytest.fixture
def loggedin_home(login_page):
    login_page.login(TOOLSHOP_EMAIL, TOOLSHOP_PASSWORD)
    login_page.page.get_by_title("Practice Software Testing - Toolshop").click()
    return login_page.page


@pytest.fixture
def catalog(loggedin_home) -> CatalogPage:
    return CatalogPage(loggedin_home)


@pytest.fixture
def guest_catalog(page) -> CatalogPage:
    """비로그인 상태로 메인 페이지에 진입해 첫 상품 목록이 그려진 상태.

    로그인이 필요 없는 상품 조회 TC(필터, 정렬, 검색)용. 계정 잠금과 무관하게 동작한다.
    """
    guest = CatalogPage(page)
    guest.open_loaded()
    return guest


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
    # 담은 상품이 없으면 헤더 장바구니 아이콘이 없어 정리할 것도 없다(클릭하면 30초 대기 뒤 teardown error)
    if not page.locator('[data-test="nav-cart"]').count():
        return
    # 장바구니 조회 응답까지 기다린 뒤 삭제한다. 응답 전에 count()로 보면 0건으로 보고 정리를 건너뛴다(2026-10-13)
    product_detail.open_cart_loaded()
    page.locator("a.btn.btn-danger").first.click()


@pytest.fixture
def cart_two_items(catalog):
    """서로 다른 상품 2종(Hammer, Pliers 카테고리 첫 상품)을 담고 장바구니 페이지로 이동한 상태의 page.

    장바구니는 브라우저 context의 sessionStorage(cart_id)에 묶여 테스트마다 새로 시작하므로 cleanup은 두지 않는다.
    """
    for category in ("Hammer", "Pliers"):
        catalog.open()
        catalog.filter_by_category(category)
        catalog.open_first_product()
        detail = ProductDetailPage(catalog.page)
        detail.add()
        expect(detail.added_toast).to_be_visible()
    catalog.open_cart_loaded()
    return catalog.page


@pytest.fixture
def cart(product_detail):
    """상품을 장바구니에 담고 체크아웃(장바구니) 페이지로 이동한 상태의 page."""
    product_detail.add()
    product_detail.open_cart_loaded()
    return product_detail.page


@pytest.fixture
def guest_product_detail(guest_catalog) -> ProductDetailPage:
    """비로그인 상태로 Hammer 카테고리 첫 상품의 상세 페이지까지 진입한 상태.

    로그인이 필요 없는 상세 화면 TC(UI_54~UI_58, UI_60)용. 계정 잠금과 무관하게 동작한다.
    """
    guest_catalog.check_category("Hammer")
    guest_catalog.open_first_product()
    detail = ProductDetailPage(guest_catalog.page)
    expect(detail.add_to_cart).to_be_visible()
    return detail


@pytest.fixture
def guest_cart(guest_product_detail):
    """비로그인 상태로 상품을 장바구니에 담고 체크아웃(장바구니) 페이지로 이동한 상태의 page (UI_81, UI_82).

    장바구니는 브라우저 context 의 sessionStorage 에 묶여 테스트마다 새로 시작하므로 cleanup 은 두지 않는다.
    """
    guest_product_detail.add()
    expect(guest_product_detail.added_toast).to_be_visible()
    guest_product_detail.open_cart_loaded()
    return guest_product_detail.page
