import pytest
from playwright.sync_api import expect

from config import SITE_URL, TOOLSHOP_EMAIL, TOOLSHOP_PASSWORD
from pages.login_page import LoginPage


@pytest.mark.tc("UI_38")
def test_logout(loggedin_home):
    page = loggedin_home

    # 헤더 유저 이름
    usermenu = page.locator('[data-test="nav-menu"]')
    expect(usermenu).to_be_visible()
    usermenu.click()

    # Sign out 버튼 클릭
    sign_out = page.locator('[data-test="nav-sign-out"]')
    expect(sign_out).to_be_visible()
    sign_out.click()

    # 로그아웃 확인
    expect(page).to_have_url(f"{SITE_URL}/")
    expect(usermenu).not_to_be_visible()


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_39")
def test_logout_shows_header_sign_in(loggedin_home):
    header = LoginPage(loggedin_home)
    expect(header.header_sign_in).to_be_hidden()

    # 2. 헤더 유저 이름 클릭 → [Sign out] 노출
    header.header_user_menu.click()
    expect(header.header_sign_out).to_be_visible()

    # 3. [Sign out] 클릭 → 로그아웃
    header.header_sign_out.click()
    expect(header.header_user_menu).to_be_hidden()

    # 4. 헤더에 [Sign in] 링크 노출
    expect(header.header_sign_in).to_be_visible()


@pytest.mark.tc("UI_77")
def test_relogin_after_logout(loggedin_home):
    login_page = LoginPage(loggedin_home)

    # 1~2. 헤더 유저 이름 → [Sign out]
    login_page.header_user_menu.click()
    login_page.header_sign_out.click()

    # 2. 메인 페이지로 리다이렉팅, 비로그인 상태 UI
    expect(login_page.page).to_have_url(LoginPage.HOME_URL)
    expect(login_page.header_user_menu).to_be_hidden()
    expect(login_page.header_sign_in).to_be_visible()

    # 3. 헤더 [Sign in] → 로그인 페이지
    login_page.header_sign_in.click()
    expect(login_page.page).to_have_url(LoginPage.LOGIN_URL)
    expect(login_page.form).to_be_visible()

    # 4. 같은 계정 입력
    login_page.email.fill(TOOLSHOP_EMAIL)
    login_page.password.fill(TOOLSHOP_PASSWORD)
    expect(login_page.email).to_have_value(TOOLSHOP_EMAIL)
    expect(login_page.password).to_have_attribute("type", "password")
    expect(login_page.password).to_have_value(TOOLSHOP_PASSWORD)

    # 5. [Login] → My account 이동, 헤더 사용자명 노출
    login_page.login_button.click()
    expect(login_page.page).to_have_url(LoginPage.ACCOUNT_URL)
    expect(login_page.account_heading).to_be_visible()
    expect(login_page.header_user_menu).to_be_visible()
    expect(login_page.header_user_menu).not_to_have_text("")
