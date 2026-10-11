import pytest
from playwright.sync_api import expect

from config import TOOLSHOP_EMAIL, TOOLSHOP_PASSWORD
from pages.login_page import LoginPage


@pytest.mark.tc("UI_01")
@pytest.mark.smoke
def test_landing_page(page):
    page.goto("https://practicesoftwaretesting.com")
    expect(page).to_have_title("Practice Software Testing - Toolshop - v5.0")


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_02")
def test_empty_credentials(login_page, blocked_login_requests):
    expect(login_page.form).to_be_visible()
    expect(login_page.email).to_have_value("")
    expect(login_page.password).to_have_value("")

    login_page.login_button.click()

    expect(login_page.email_error).to_be_visible()
    expect(login_page.email_error).to_contain_text("required")
    expect(login_page.password_error).to_be_visible()
    expect(login_page.password_error).to_contain_text("required")
    # 로그인 요청 미전송, 페이지 이동 없음
    assert blocked_login_requests == []
    expect(login_page.page).to_have_url(login_page.LOGIN_URL)


# 도메인 없는 잘못된 이메일 형식
@pytest.mark.tc("UI_03")
def test_invalid_email_format(login_page):
    login_page.submit("customer2", TOOLSHOP_PASSWORD)

    expect(login_page.email_error).to_be_visible()
    expect(login_page.page.get_by_text("Email format is invalid")).to_be_visible()


# 도메인 포함 잘못된 이메일 형식
@pytest.mark.tc("UI_04")
def test_invalid_email(login_page):
    login_page.submit("customer23@practicesoftwaretesting.com", TOOLSHOP_PASSWORD)

    expect(login_page.login_error).to_be_visible()
    expect(login_page.page.get_by_text("Invalid email or password")).to_be_visible()


@pytest.mark.tc("UI_05")
def test_invalid_password(login_page):
    login_page.submit(TOOLSHOP_EMAIL, "welcome02")

    expect(login_page.login_error).to_be_visible()
    expect(login_page.page.get_by_text("Invalid email or password")).to_be_visible()


# 비밀번호 길이 경계: 1자, 200자 (클라이언트 검증, 로그인 요청은 fixture가 차단)
@pytest.mark.spec_undefined
@pytest.mark.tc("UI_06")
def test_password_length_invalid(login_page, blocked_login_requests):
    expect(login_page.form).to_be_visible()

    login_page.submit(TOOLSHOP_EMAIL, "a")

    expect(login_page.email).to_have_value(TOOLSHOP_EMAIL)
    expect(login_page.password).to_have_attribute("type", "password")
    expect(login_page.password_error).to_be_visible()
    expect(login_page.password_error).to_contain_text("length")

    login_page.password.fill("a" * 200)
    expect(login_page.password).to_have_attribute("type", "password")
    expect(login_page.password).to_have_value("a" * 200)
    login_page.login_button.click()

    expect(login_page.password_error).to_be_visible()
    expect(login_page.password_error).to_contain_text("length")


@pytest.mark.tc("UI_07")
@pytest.mark.smoke
def test_login(login_page):
    login_page.login(TOOLSHOP_EMAIL, TOOLSHOP_PASSWORD)

    expect(login_page.page).to_have_url("https://practicesoftwaretesting.com/account")
    expect(login_page.page.get_by_role("heading", name="My account")).to_be_visible()
    expect(login_page.page.get_by_role("button", name="Jack Howe")).to_be_visible()


@pytest.mark.tc("UI_08")
def test_loggedin_home(loggedin_home):
    page = loggedin_home
    expect(page).to_have_url("https://practicesoftwaretesting.com/")
    expect(page.get_by_role("button", name="Jack Howe")).to_be_visible()


@pytest.mark.tc("UI_40")
def test_login_form_elements(login_page):
    expect(login_page.page).to_have_url(login_page.LOGIN_URL)
    expect(login_page.form).to_be_visible()

    expect(login_page.email).to_be_visible()
    expect(login_page.password).to_be_visible()
    expect(login_page.google_sign_in).to_be_visible()


# 백로그 #24: 스펙 미정의, 시트 기대결과(라이브 확인 동작) 기준
@pytest.mark.spec_undefined
@pytest.mark.tc("UI_41")
def test_sign_in_link_hidden_after_login(login_page):
    expect(login_page.header_sign_in).to_be_visible()

    login_page.login(TOOLSHOP_EMAIL, TOOLSHOP_PASSWORD)

    expect(login_page.header_sign_in).to_be_hidden()


# 클라이언트 필수값 검증: 로그인 요청은 fixture가 차단·기록한다(계정 잠금 방지)
@pytest.mark.spec_undefined
@pytest.mark.tc("UI_72")
def test_empty_email_required_error(login_page, blocked_login_requests):
    expect(login_page.form).to_be_visible()

    login_page.password.fill(TOOLSHOP_PASSWORD)

    expect(login_page.email).to_have_value("")
    expect(login_page.password).to_have_attribute("type", "password")
    expect(login_page.password).to_have_value(TOOLSHOP_PASSWORD)

    login_page.login_button.click()

    expect(login_page.email_error).to_be_visible()
    expect(login_page.email_error).to_contain_text("Email is required")
    # 로그인 요청 미전송, 페이지 이동 없음
    assert blocked_login_requests == []
    expect(login_page.page).to_have_url(login_page.LOGIN_URL)


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_73")
def test_empty_password_required_error(login_page, blocked_login_requests):
    expect(login_page.form).to_be_visible()

    login_page.email.fill(TOOLSHOP_EMAIL)

    expect(login_page.email).to_have_value(TOOLSHOP_EMAIL)
    expect(login_page.password).to_have_value("")

    login_page.login_button.click()

    expect(login_page.password_error).to_be_visible()
    expect(login_page.password_error).to_contain_text("Password is required")
    # 로그인 요청 미전송, 페이지 이동 없음
    assert blocked_login_requests == []
    expect(login_page.page).to_have_url(login_page.LOGIN_URL)


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_74")
def test_password_visibility_toggle(login_page):
    expect(login_page.form).to_be_visible()

    login_page.password.fill("abc12345")
    expect(login_page.password).to_have_attribute("type", "password")
    expect(login_page.password).to_have_value("abc12345")

    login_page.password_toggle.click()
    expect(login_page.password).to_have_attribute("type", "text")
    expect(login_page.password).to_have_value("abc12345")

    login_page.password_toggle.click()
    expect(login_page.password).to_have_attribute("type", "password")
    expect(login_page.password).to_have_value("abc12345")


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_75")
def test_forgot_password_link(login_page):
    expect(login_page.page).to_have_url(login_page.LOGIN_URL)
    expect(login_page.form).to_be_visible()

    login_page.forgot_password_link.click()

    expect(login_page.page).to_have_url(login_page.FORGOT_PASSWORD_URL)
    expect(login_page.forgot_password_heading).to_be_visible()
    expect(login_page.forgot_password_email).to_be_visible()
    expect(login_page.forgot_password_submit).to_be_visible()
    expect(login_page.forgot_password_submit).to_have_value("Set New Password")


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_76")
def test_register_link(login_page):
    expect(login_page.page).to_have_url(login_page.LOGIN_URL)
    expect(login_page.form).to_be_visible()

    login_page.register_link.click()

    expect(login_page.page).to_have_url(login_page.REGISTER_URL)
    expect(login_page.register_heading).to_be_visible()


@pytest.mark.tc("UI_79")
def test_header_sign_in_opens_login_page(page):
    page.goto(LoginPage.HOME_URL)
    login_page = LoginPage(page)

    login_page.header_sign_in.click()

    expect(page).to_have_url(LoginPage.LOGIN_URL)
    expect(login_page.heading).to_be_visible()
