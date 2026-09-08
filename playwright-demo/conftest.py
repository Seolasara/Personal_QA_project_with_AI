import pytest

from pages.catalog_page import CatalogPage, ProductDetailPage
from pages.login_page import LoginPage

HOME_URL = "https://practicesoftwaretesting.com"


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
