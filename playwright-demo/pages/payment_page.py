from playwright.sync_api import Page, Response, expect
from config import API_URL


class PaymentPage:
    """체크아웃 위저드 (cart → sign-in → address → payment).

    각 단계 진행 버튼은 앱에서 data-test="proceed-1/2/3", 결제 확정은 "finish".
    """

    # 우편번호 자동조회 API (country+postal_code+house_number 입력 시 debounce 300ms 후 호출)

    def __init__(self, page: Page):
        self.page = page

        # step 1: cart
        self.cart_items = page.locator('[data-test="product-title"]')
        self.proceed_from_cart = page.locator('[data-test="proceed-1"]')

        # step 2: sign-in (이미 로그인된 상태)
        self.already_logged_in = page.get_by_text("already logged in")
        self.proceed_from_signin = page.locator('[data-test="proceed-2"]')

        # step 3: billing address (모든 필드 required)
        self.address_heading = page.get_by_role(
            "heading", name="Billing Address", level=3
        )
        self.country = page.locator('[data-test="country"]')
        self.postcode = page.locator('[data-test="postal_code"]')
        self.house_number = page.locator('[data-test="house_number"]')
        self.street = page.locator('[data-test="street"]')
        self.city = page.locator('[data-test="city"]')
        self.state = page.locator('[data-test="state"]')
        self.proceed_from_address = page.locator('[data-test="proceed-3"]')

        # step 4: payment
        self.payment_method = page.locator('[data-test="payment-method"]')
        self.confirm = page.locator('[data-test="finish"]')
        self.success_message = page.locator('[data-test="payment-success-message"]')
        # 같은 finish 버튼이 첫 클릭 전에는 "Check payment", 결제 검증 성공 후에는 "Confirm" 라벨이 된다.
        self.check_payment_button = page.locator('[data-test="finish"]')

        # 결제 완료 (인보이스). 앱에 data-test 가 없다. 번호 span 의 id="invoice-number" 는
        # innerHTML 주입 시 제거되어 없으므로(2026-10-10 확인) 템플릿 컨테이너 id 아래 span 을 쓴다.
        self.order_confirmation = page.locator("#order-confirmation")
        self.invoice_number = self.order_confirmation.locator("span")

    # --- 단계 이동 --------------------------------------------------------
    def go_to_signin_step(self) -> None:
        self.proceed_from_cart.click()

    def go_to_address_step(self) -> None:
        self.proceed_from_signin.click()
        expect(self.address_heading).to_be_visible()
        # 로그인 사용자는 저장된 주소가 비동기로 자동 채워진다(getDetails).
        # 그 전에 폼을 채우면 값이 덮어써지므로 네트워크가 잦아들 때까지 대기.
        self.page.wait_for_load_state("networkidle")

    def go_to_payment_step(self) -> None:
        # 우편번호 자동조회(debounce 300ms) 등으로 유효성 재계산이 늦을 수 있음.
        expect(self.proceed_from_address).to_be_enabled()
        self.proceed_from_address.click()

    # --- 폼 입력 --------------------------------------------------------
    # --- 우편번호 조회 결과를 쓰는 Billing 입력 (UI_33~UI_37) ---------------
    # Country, Postcode, House number 를 채우면 GET /postcode-lookup 응답으로
    # Street, City, State 가 덮어써진다. Postcode 를 비울 때는 조회가 일어나지 않는다(2026-10-10 확인).
    @property
    def selected_country(self):
        return self.country.locator("option:checked")

    def _is_postcode_lookup(self, response: Response) -> bool:
        return "/postcode-lookup" in response.url and response.request.method == "GET"

    def fill_address_by_lookup(self, country: str, *, postcode: str, house_number: str) -> dict:
        """Country, Postcode, House number 를 입력하고 우편번호 조회 응답(JSON)을 돌려준다.

        조회 결과가 Street, City, State 에 반영될 때까지 기다린다.
        """
        self.country.select_option(label=country)
        self.postcode.fill(postcode)
        with self.page.expect_response(self._is_postcode_lookup) as info:
            self.house_number.fill(house_number)
        return self._wait_lookup_applied(info.value)

    def refill_postcode(self, postcode: str) -> dict:
        """Postcode 만 다시 입력하고 우편번호 조회 응답(JSON)을 돌려준다."""
        with self.page.expect_response(self._is_postcode_lookup) as info:
            self.postcode.fill(postcode)
        return self._wait_lookup_applied(info.value)

    def clear_postcode(self) -> None:
        self.postcode.fill("")

    def _wait_lookup_applied(self, response: Response) -> dict:
        lookup = response.json()
        expect(self.state).to_have_value(lookup["state"])
        return lookup

    # --- 결제 방법과 결제 검증 (UI_34, UI_35) ----------------------------
    @property
    def selected_payment_method(self):
        return self.payment_method.locator("option:checked")

    def check_payment_and_wait(self) -> Response:
        """[Check payment]를 누르고 결제 검증 요청(POST /payment/check)의 응답을 돌려준다."""
        with self.page.expect_response(
            lambda r: "/payment/check" in r.url and r.request.method == "POST"
        ) as info:
            self.check_payment_button.click()
        return info.value

    def select_payment_method(self, value: str) -> None:
        # value 예: "cash-on-delivery", "bank-transfer"
        self.payment_method.select_option(value)

    def check_payment(self) -> None:
        self.check_payment_button.click()

    def confirm_payment(self) -> None:
        self.confirm.click()

    # --- Billing 필수값 비움, 결제 방법 목록, 단계 표시 (UI_85~UI_91) ----------
    # Street, City, State 를 비울 때는 우편번호 조회가 일어나지 않는다(2026-10-11 확인).
    def clear_fields(self, *fields) -> None:
        for field in fields:
            field.fill("")

    @property
    def payment_method_choices(self):
        """안내 옵션("Choose your payment method")을 뺀 결제 방법 옵션."""
        return self.payment_method.locator('option:not([value=""])')

    def open_payment_methods(self) -> None:
        self.payment_method.click()

    @property
    def monthly_installments(self):
        # Buy Now Pay Later 선택 시에만 렌더링된다(2026-10-11 확인).
        return self.page.locator('[data-test="monthly_installments"]')

    # 상단 단계 표시. 앱에 data-test 가 없어 wizard 컴포넌트 클래스를 쓴다.
    # 라벨은 DOM 텍스트가 "Cart" 이고 CSS 로 대문자 표시되므로 innerText 로 비교한다.
    @property
    def step_labels(self):
        return self.page.locator("aw-wizard-navigation-bar .label")

    @property
    def step_numbers(self):
        return self.page.locator("aw-wizard-navigation-bar .step-indicator")

    # --- Sign in 단계 로그인 폼과 안내 문구, Billing 자동 채움 (UI_81~UI_84) ----
    # 비로그인 상태의 Sign in 단계에는 제목 "Login"과 로그인 폼이 나온다(2026-10-11 확인).
    @property
    def signin_heading(self):
        return self.page.get_by_role("heading", name="Login", level=3, exact=True)

    @property
    def signin_email(self):
        return self.page.locator('[data-test="email"]')

    @property
    def signin_password(self):
        return self.page.locator('[data-test="password"]')

    @property
    def signin_login_button(self):
        # input[type=submit] value="Login"
        return self.page.locator('[data-test="login-submit"]')

    @property
    def signin_message(self):
        # 로그인 상태 안내 문구. 앱에 data-test 가 없어 [Proceed to checkout](proceed-2)이 있는 단계의 문단을 쓴다.
        return self.page.locator("aw-wizard-step", has=self.proceed_from_signin).locator("p")

    def fill_signin_email(self, email: str) -> None:
        self.signin_email.fill(email)

    def fill_signin_password(self, password: str) -> None:
        self.signin_password.fill(password)

    def submit_signin(self) -> None:
        self.signin_login_button.click()

    API_URL = API_URL

    def open_address_step(self) -> None:
        """Sign in 단계 [Proceed to checkout]을 누르고 Billing Address 제목이 보일 때까지 기다린다."""
        self.proceed_from_signin.click()
        expect(self.address_heading).to_be_visible()

    def fetch_account(self) -> dict:
        """로그인한 브라우저의 토큰(localStorage auth-token)으로 GET /users/me 를 호출해 계정 정보(JSON)를 돌려준다.

        Billing 진입 시 /users/me 재호출 여부가 로그인 경로마다 달라(2026-10-11 확인) 응답 대기 대신 직접 조회한다.
        """
        token = self.page.evaluate("() => localStorage.getItem('auth-token')")
        response = self.page.request.get(
            f"{self.API_URL}/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.ok, f"GET /users/me 실패: {response.status}"
        return response.json()
