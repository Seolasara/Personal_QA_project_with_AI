class LoginPage:
    def __init__(self, page):
        self.page = page

        self.email = page.get_by_label("Email address")
        self.password = page.get_by_label("Password *")
        self.login_button = page.get_by_role("button", name="Login")

    def login(self, email, password):
        self.email.fill(email)
        self.password.fill(password)
        self.login_button.click()
        self.page.wait_for_url("https://practicesoftwaretesting.com/account", timeout=10000)
