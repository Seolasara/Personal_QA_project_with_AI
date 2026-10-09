from playwright.sync_api import Page


class LoginPage:
    """로그인 페이지 (`/auth/login`)."""

    LOGIN_URL = "https://practicesoftwaretesting.com/auth/login"
    ACCOUNT_URL = "https://practicesoftwaretesting.com/account"
    # 로그인 API 요청 감시용 URL 패턴 (api.practicesoftwaretesting.com/users/login)
    LOGIN_API_PATTERN = "**/users/login"

    def __init__(self, page: Page):
        self.page = page

        self.form = page.locator('[data-test="login-form"]')
        self.email = page.get_by_label("Email address")
        self.password = page.get_by_label("Password *")
        self.login_button = page.get_by_role("button", name="Login")
        self.google_sign_in = page.get_by_role("button", name="Sign in with Google")

        # 헤더의 [Sign in] 링크 (로그인 상태 반영 확인용)
        self.header_sign_in = page.locator('[data-test="nav-sign-in"]')
        # 로그인 상태의 헤더 유저 이름 메뉴와 그 안의 [Sign out] (로그아웃 TC용)
        self.header_user_menu = page.locator('[data-test="nav-menu"]')
        self.header_sign_out = page.locator('[data-test="nav-sign-out"]')

        # 검증용
        self.email_error = page.locator('[data-test="email-error"]')
        self.password_error = page.locator('[data-test="password-error"]')
        self.login_error = page.locator('[data-test="login-error"]')

    def submit(self, email: str, password: str) -> None:
        """자격증명 입력 후 제출만 한다. 성공/실패 대기는 호출측 책임."""
        self.email.fill(email)
        self.password.fill(password)
        self.login_button.click()

    def login(self, email: str, password: str) -> None:
        """성공 경로 전용. `/account` 도달까지 대기한다."""
        self.submit(email, password)
        self.page.wait_for_url(self.ACCOUNT_URL, timeout=10000)
