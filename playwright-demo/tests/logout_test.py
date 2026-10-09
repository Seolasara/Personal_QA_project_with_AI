import pytest
from playwright.sync_api import expect

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
    expect(page).to_have_url("https://practicesoftwaretesting.com/")
    expect(usermenu).not_to_be_visible()


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
