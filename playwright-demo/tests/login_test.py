import pytest
from playwright.sync_api import expect


@pytest.mark.tc("QA-01")
def test_landing_page(page):
    page.goto("https://practicesoftwaretesting.com")
    expect(page).to_have_title("Practice Software Testing - Toolshop - v5.0")


# 도메인 없는 잘못된 이메일 형식
@pytest.mark.tc("QA-02")
def test_invalid_email_format(login_page):
    login_page.login("customer2", "welcome01")

    expect(login_page.page.locator("#email-error")).to_be_visible()
    expect(login_page.page.get_by_text("Email format is invalid")).to_be_visible()

# 도메인 포함 잘못된 이메일 형식
@pytest.mark.tc("QA-03")
def test_invalid_email(login_page):
    login_page.login("customer23@practicesoftwaretesting.com", "welcome01")

    expect(login_page.page.locator('[data-test="login-error"]')).to_be_visible()
    expect(login_page.page.get_by_text("Invalid email or password")).to_be_visible()


@pytest.mark.tc("QA-04")
def test_invalid_password(login_page):
    login_page.login("customer2@practicesoftwaretesting.com", "welcome02")

    expect(login_page.page.locator('[data-test="login-error"]')).to_be_visible()
    expect(login_page.page.get_by_text("Invalid email or password")).to_be_visible()


@pytest.mark.tc("QA-05")
def test_login(login_page):
    login_page.login("customer2@practicesoftwaretesting.com", "welcome01")

    expect(login_page.page).to_have_url("https://practicesoftwaretesting.com/account")
    expect(login_page.page.get_by_role("heading", name="My account")).to_be_visible()
    expect(login_page.page.get_by_role("button", name="Jack Howe")).to_be_visible()


@pytest.mark.tc("QA-06")
def test_loggedin_home(loggedin_home):
    page = loggedin_home
    expect(page).to_have_url("https://practicesoftwaretesting.com/")
    expect(page.get_by_role("button", name="Jack Howe")).to_be_visible()