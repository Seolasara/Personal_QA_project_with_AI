from playwright.sync_api import expect


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
