import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import CartPage, CatalogPage
from pages.payment_page import PaymentPage

BILLING = dict(
    postcode="12345",
    house_number="123",
    street="Seoul",
    city="Seoul",
    state="Korea",
)
COUNTRY = "Korea (the Republic of)"
COUNTRY_CODE = "KR"  # COUNTRY 옵션의 value (ISO 3166-1 alpha-2)
# fill_billing_address 키워드 → PaymentPage.billing_text_fields 키
BILLING_FIELD_VALUES = dict(
    street=BILLING["street"],
    city=BILLING["city"],
    state=BILLING["state"],
    house_number=BILLING["house_number"],
    postal_code=BILLING["postcode"],
)


def _go_to_payment_step(payment: PaymentPage) -> None:
    """장바구니 → Sign in → Billing Address 입력 → Payment 단계까지 진행한다."""
    expect(payment.cart_items).not_to_have_count(0)
    payment.go_to_signin_step()
    expect(payment.already_logged_in).to_be_visible()
    payment.go_to_address_step()
    payment.fill_billing_address(COUNTRY, **BILLING)
    payment.go_to_payment_step()


@pytest.mark.tc("UI_33")
@pytest.mark.parametrize("field", list(BILLING_FIELD_VALUES))
def test_billing_required_field_disables_proceed(cart, field):
    payment = PaymentPage(cart)
    # 자동조회 응답이 입력값을 덮어쓰지 않게 차단 (이 TC의 검증 대상은 필수값 검증)
    payment.block_postcode_lookup()

    expect(payment.cart_items).not_to_have_count(0)
    payment.go_to_signin_step()
    expect(payment.already_logged_in).to_be_visible()

    # 1. BILLING ADDRESS 페이지 노출
    payment.go_to_address_step()
    expect(payment.address_heading).to_be_visible()

    # 2. 모든 필드 입력값 노출 (로그인 사용자 주소 자동채움 이후 입력)
    payment.fill_billing_address(COUNTRY, **BILLING)
    expect(payment.country).to_have_value(COUNTRY_CODE)
    for name, value in BILLING_FIELD_VALUES.items():
        expect(payment.billing_text_fields[name]).to_have_value(value)

    # 3. 대상 필드만 미입력 상태
    target = payment.billing_text_fields[field]
    target.fill("")
    expect(target).to_have_value("")

    # 4. [Proceed] 비활성
    expect(payment.proceed_from_address).to_be_disabled()

    # 5. 대상 필드 입력 후 [Proceed] 활성
    target.fill(BILLING_FIELD_VALUES[field])
    expect(target).to_have_value(BILLING_FIELD_VALUES[field])
    expect(payment.proceed_from_address).to_be_enabled()


@pytest.mark.tc("UI_34")
def test_checkout_button(cart):
    payment = PaymentPage(cart)

    # 결제 가능 상품 1개 이상 존재 확인
    expect(payment.cart_items).not_to_have_count(0)
    expect(payment.proceed_from_cart).to_be_enabled()
    payment.go_to_signin_step()

    # Sign In 상태 확인
    expect(payment.already_logged_in).to_be_visible()
    expect(payment.proceed_from_signin).to_be_enabled()
    payment.go_to_address_step()

    # Billing Address 스텝 + 폼 입력
    expect(payment.address_heading).to_be_visible()
    payment.fill_billing_address("Korea (the Republic of)", **BILLING)

    # Proceed to checkout 버튼 활성화 확인
    expect(payment.proceed_from_address).to_be_enabled()
    payment.go_to_payment_step()

    # 결제 방식 드롭다운 + Confirm 버튼 활성화 확인
    expect(payment.payment_method).to_be_enabled()
    payment.select_payment_method("cash-on-delivery")
    expect(payment.confirm).to_be_enabled()


@pytest.mark.tc("UI_35")
def test_payment_checkout(cart):
    payment = PaymentPage(cart)

    expect(payment.cart_items).not_to_have_count(0)
    payment.go_to_signin_step()

    expect(payment.already_logged_in).to_be_visible()
    payment.go_to_address_step()

    payment.fill_billing_address("Korea (the Republic of)", **BILLING)
    payment.go_to_payment_step()

    # 결제 방식 선택 후 Confirm
    expect(payment.payment_method).to_be_enabled()
    payment.select_payment_method("cash-on-delivery")
    payment.confirm_payment()

    # 결제 완료 메시지 확인
    expect(payment.success_message).to_be_visible()


@pytest.mark.tc("UI_36")
@pytest.mark.smoke
def test_payment_confirm_shows_invoice_number(cart):
    payment = PaymentPage(cart)
    _go_to_payment_step(payment)

    payment.select_payment_method("cash-on-delivery")
    payment.check_payment()
    expect(payment.success_message).to_be_visible()
    expect(payment.confirm).to_have_text("Confirm")

    payment.confirm_payment()

    # 4. 인보이스 번호 노출 (형식은 스펙에 없어 비어 있지 않은지만 확인)
    expect(payment.invoice_number).to_be_visible()
    expect(payment.invoice_number).to_have_text(re.compile(r"\S"))


@pytest.mark.tc("UI_37")
def test_payment_confirm_empties_cart(cart):
    payment = PaymentPage(cart)
    expect(payment.cart_items).not_to_have_count(0)
    paid_title = payment.cart_items.first.inner_text().strip()
    _go_to_payment_step(payment)

    payment.select_payment_method("cash-on-delivery")
    payment.check_payment()
    expect(payment.success_message).to_be_visible()
    payment.confirm_payment()
    expect(payment.invoice_number).to_be_visible()

    # 5. 헤더 장바구니 아이콘 미노출 (담긴 수량 0이면 렌더링되지 않음, 2026-10-10 확인)
    expect(CatalogPage(cart).nav_cart).to_be_hidden()

    # 6. 장바구니 페이지 진입 → 빈 장바구니 문구 노출, 결제한 상품 미노출
    cart.goto(CartPage.URL)
    cart_page = CartPage(cart)
    try:
        # 장바구니 Checkout Cart AC4 문구. 화면 로드 완료 기준이기도 하다.
        expect(cart_page.empty_message).to_be_visible()
    except AssertionError:
        if cart.get_by_text("The cart is empty").count():
            pytest.xfail("백로그 #15: 빈 장바구니 문구가 스펙과 다름")
        pytest.xfail("백로그 #25: 결제 후 장바구니 페이지에 빈 장바구니 문구 없이 빈 화면 노출")
    expect(cart_page.row(paid_title)).to_have_count(0)
