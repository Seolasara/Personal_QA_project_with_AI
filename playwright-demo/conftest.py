import pytest
from pages.login_page import LoginPage

@pytest.fixture
def login_page(page):
    page.goto("https://practicesoftwaretesting.com")
    page.get_by_role("link", name="Sign In").click()

    return LoginPage(page)


@pytest.fixture
def loggedin_home(login_page):
    login_page.login("customer2@practicesoftwaretesting.com", "welcome01")
    login_page.page.get_by_title("Practice Software Testing - Toolshop").click()

    return login_page.page


@pytest.fixture
def cart_ready(loggedin_home):
    page = loggedin_home
    page.get_by_role("checkbox", name="Hammer").check()
    product_list = page.locator('[data-test="filter_completed"]')
    products = product_list.locator('[data-test^="product-"]')
    products.first.click()

    yield loggedin_home

    page.locator('[data-test="nav-cart"]').click()
    page.locator("a.btn.btn-danger").click()

    return page


@pytest.fixture
def cart(loggedin_home):
    page = loggedin_home
    page.get_by_role("checkbox", name="Hammer").check()
    product_list = page.locator('[data-test="filter_completed"]')
    products = product_list.locator('[data-test^="product-"]')
    products.first.click()
    page.get_by_role("button", name="Add to cart").click()
    page.locator('[data-test="nav-cart"]').click()

    return page