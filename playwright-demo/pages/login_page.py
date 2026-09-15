from playwright.sync_api import Page


class LoginPage:
    """로그인 페이지 (`/auth/login`)."""

    ACCOUNT_URL = "https://practicesoftwaretesting.com/account"

    def __init__(self, page: Page):
        self.page = page

        self.email = page.get_by_label("Email address")
        self.password = page.get_by_label("Password *")
        self.login_button = page.get_by_role("button", name="Login")

        # 검증용
        self.email_error = page.locator('[data-test="email-error"]')
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
