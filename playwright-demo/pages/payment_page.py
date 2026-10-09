from playwright.sync_api import Page, expect


class PaymentPage:
    """체크아웃 위저드 (cart → sign-in → address → payment).

    각 단계 진행 버튼은 앱에서 data-test="proceed-1/2/3", 결제 확정은 "finish".
    """

    # 우편번호 자동조회 API (country+postal_code+house_number 입력 시 debounce 300ms 후 호출)
    POSTCODE_LOOKUP_PATTERN = "**/postcode-lookup**"

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
        self.postcode_lookup_loading = page.locator('[data-test="postcode-lookup-loading"]')
        self.proceed_from_address = page.locator('[data-test="proceed-3"]')
        # 비울 수 있는 필수 텍스트 필드 (UI_33). Country는 placeholder 옵션이 disabled라
        # UI로 빈 값을 고를 수 없어 제외한다(2026-10-10 확인).
        self.billing_text_fields = {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "house_number": self.house_number,
            "postal_code": self.postcode,
        }

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
    def fill_billing_address(
        self,
        country: str,
        *,
        postcode: str,
        house_number: str,
        street: str,
        city: str,
        state: str,
    ) -> None:
        self.country.select_option(label=country)
        self.postcode.fill(postcode)
        self.house_number.fill(house_number)
        # country+postcode+house_number 입력 시 자동 주소조회가 트리거되어
        # street/city/state 를 덮어쓸 수 있으므로, 조회 로딩이 끝난 뒤 나머지 입력.
        expect(self.postcode_lookup_loading).to_be_hidden()
        self.street.fill(street)
        self.city.fill(city)
        self.state.fill(state)

    def block_postcode_lookup(self) -> None:
        """우편번호 자동조회 요청을 차단한다.

        자동조회 응답이 입력 직후 street/city/state 를 덮어써(2026-10-10 확인) 입력값 검증이
        흔들린다. 필수값 검증 TC(UI_33)처럼 자동조회가 검증 대상이 아닐 때만 쓴다.
        """
        self.page.route(self.POSTCODE_LOOKUP_PATTERN, lambda route: route.abort())

    def select_payment_method(self, value: str) -> None:
        # value 예: "cash-on-delivery", "bank-transfer"
        self.payment_method.select_option(value)

    def check_payment(self) -> None:
        self.check_payment_button.click()

    def confirm_payment(self) -> None:
        self.confirm.click()
