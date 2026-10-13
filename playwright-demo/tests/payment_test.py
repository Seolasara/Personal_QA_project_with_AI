import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage
from pages.payment_page import PaymentPage

COUNTRY = "Korea (the Republic of)"
COUNTRY_CODE = "KR"  # COUNTRY 옵션의 value (ISO 3166-1 alpha-2)
POSTCODE = "12345"
HOUSE_NUMBER = "123"


def _go_to_address_step(payment: PaymentPage) -> None:
    """장바구니 → Sign in(로그인 상태) → Billing Address 단계까지 진행한다."""
    expect(payment.cart_items).not_to_have_count(0)
    payment.go_to_signin_step()
    expect(payment.already_logged_in).to_be_visible()
    payment.go_to_address_step()
    expect(payment.address_heading).to_be_visible()


def _fill_address_by_lookup(payment: PaymentPage) -> None:
    """Country, Postcode, House number 를 입력하고, 조회 결과로 Street, City, State 가 채워졌는지 확인한다."""
    lookup = payment.fill_address_by_lookup(COUNTRY, postcode=POSTCODE, house_number=HOUSE_NUMBER)
    expect(payment.street).to_have_value(lookup["street"])
    expect(payment.city).to_have_value(lookup["city"])
    expect(payment.state).to_have_value(lookup["state"])


def _expect_lookup_inputs(payment: PaymentPage) -> None:
    """2. 입력 필드 내 입력한 값 노출 (Country, Postcode, House number)."""
    expect(payment.country).to_have_value(COUNTRY_CODE)
    expect(payment.selected_country).to_have_text(COUNTRY)
    expect(payment.postcode).to_have_value(POSTCODE)
    expect(payment.house_number).to_have_value(HOUSE_NUMBER)


def _go_to_payment_step(payment: PaymentPage) -> None:
    """Billing Address 를 우편번호 조회로 채우고 Payment 단계까지 진행한다."""
    _go_to_address_step(payment)
    _fill_address_by_lookup(payment)
    payment.go_to_payment_step()
    expect(payment.payment_method).to_be_visible()


@pytest.mark.tc("UI_33")
def test_billing_required_field_disables_proceed(cart):
    payment = PaymentPage(cart)

    # 1. BILLING ADDRESS 페이지 정상 노출
    _go_to_address_step(payment)

    lookup = payment.fill_address_by_lookup(COUNTRY, postcode=POSTCODE, house_number=HOUSE_NUMBER)
    # 2. [Country] 필드에 선택한 국가 노출
    expect(payment.country).to_have_value(COUNTRY_CODE)
    expect(payment.selected_country).to_have_text(COUNTRY)
    # 3. [Postcode] 필드에 입력한 값 노출
    expect(payment.postcode).to_have_value(POSTCODE)
    # 4. [House number] 필드에 입력한 값 노출
    expect(payment.house_number).to_have_value(HOUSE_NUMBER)
    # 5. [Street], [City], [State] 필드에 값이 채워진 상태로 노출 (우편번호 조회 결과)
    expect(payment.street).to_have_value(lookup["street"])
    expect(payment.city).to_have_value(lookup["city"])
    expect(payment.state).to_have_value(lookup["state"])
    for field in (payment.street, payment.city, payment.state):
        expect(field).not_to_have_value("")

    # 6. [Postcode] 필드 값 미입력 상태 노출
    payment.clear_postcode()
    expect(payment.postcode).to_have_value("")
    # 7. 비활성 상태의 [Proceed to checkout] 버튼 노출
    expect(payment.proceed_from_address).to_be_visible()
    expect(payment.proceed_from_address).to_be_disabled()

    # 8. [Postcode] 필드에 입력한 값 노출
    payment.refill_postcode(POSTCODE)
    expect(payment.postcode).to_have_value(POSTCODE)
    # 9. 활성 상태의 [Proceed to checkout] 버튼 노출
    expect(payment.proceed_from_address).to_be_visible()
    expect(payment.proceed_from_address).to_be_enabled()


@pytest.mark.tc("UI_34")
def test_checkout_button(cart):
    payment = PaymentPage(cart)
    _go_to_payment_step(payment)

    payment.select_payment_method("cash-on-delivery")

    # 5-1. 드롭다운 박스 내 "Cash on Delivery" 텍스트 정상 노출
    expect(payment.selected_payment_method).to_have_text("Cash on Delivery")
    # 5-2. 활성 상태의 [Check payment] 버튼 정상 노출
    expect(payment.check_payment_button).to_be_visible()
    expect(payment.check_payment_button).to_have_text("Check payment")
    expect(payment.check_payment_button).to_be_enabled()


@pytest.mark.tc("UI_35")
def test_payment_checkout(cart):
    payment = PaymentPage(cart)
    _go_to_payment_step(payment)

    payment.select_payment_method("cash-on-delivery")
    expect(payment.check_payment_button).to_have_text("Check payment")
    response = payment.check_payment_and_wait()

    # 6-1. 결제 요청 정상 처리
    assert response.ok, f"결제 검증 요청 실패: {response.status}"
    # 6-2. "Payment was successful" 인라인 메시지 정상 노출
    expect(payment.success_message).to_be_visible()
    expect(payment.success_message).to_have_text("Payment was successful")


@pytest.mark.flaky(reruns=0)  # 재시도 제외: 인보이스 중복 생성
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

    # 7. 인보이스 번호 노출 (형식은 스펙에 없어 비어 있지 않은지만 확인)
    expect(payment.invoice_number).to_be_visible()
    expect(payment.invoice_number).to_have_text(re.compile(r"\S"))


@pytest.mark.flaky(reruns=0)  # 재시도 제외: 인보이스 중복 생성
@pytest.mark.tc("UI_37")
def test_payment_confirm_empties_cart(cart):
    payment = PaymentPage(cart)
    expect(payment.cart_items).not_to_have_count(0)
    _go_to_payment_step(payment)

    payment.select_payment_method("cash-on-delivery")
    payment.check_payment()
    expect(payment.success_message).to_be_visible()
    expect(payment.confirm).to_have_text("Confirm")
    payment.confirm_payment()
    expect(payment.invoice_number).to_be_visible()

    # 5. 헤더 장바구니 아이콘 미노출 (담긴 수량 0이면 렌더링되지 않음, 2026-10-10 확인)
    expect(CatalogPage(cart).nav_cart).to_be_hidden()


@pytest.mark.tc("UI_85")
def test_billing_city_state_empty_disables_proceed(cart):
    payment = PaymentPage(cart)
    _go_to_address_step(payment)

    lookup = payment.fill_address_by_lookup(COUNTRY, postcode=POSTCODE, house_number=HOUSE_NUMBER)
    # 2. 입력 필드 내 입력한 값 노출
    _expect_lookup_inputs(payment)

    payment.clear_fields(payment.city, payment.state)
    # 3. [City], [State] 필드 값 미입력 상태 노출, [Street] 필드 값 유지
    expect(payment.city).to_have_value("")
    expect(payment.state).to_have_value("")
    expect(payment.street).to_have_value(lookup["street"])
    # 4. 비활성 상태의 [Proceed to checkout] 버튼 노출
    expect(payment.proceed_from_address).to_be_visible()
    expect(payment.proceed_from_address).to_be_disabled()


@pytest.mark.tc("UI_86")
def test_payment_method_dropdown_lists_five_methods(cart):
    payment = PaymentPage(cart)
    _go_to_payment_step(payment)

    payment.open_payment_methods()
    # 2. 드롭다운에 5개의 결제 방법 노출
    expect(payment.payment_method_choices).to_have_text(
        ["Bank Transfer", "Cash on Delivery", "Credit Card", "Buy Now Pay Later", "Gift Card"]
    )


@pytest.mark.tc("UI_87")
@pytest.mark.spec_undefined
def test_no_payment_method_disables_check_payment(cart):
    payment = PaymentPage(cart)
    _go_to_payment_step(payment)

    # 2. 결제 방법 드롭다운에 "Choose your payment method" 노출
    expect(payment.selected_payment_method).to_have_text("Choose your payment method")
    # 3. 비활성 상태의 [Check payment] 버튼 노출
    expect(payment.check_payment_button).to_be_visible()
    expect(payment.check_payment_button).to_have_text("Check payment")
    expect(payment.check_payment_button).to_be_disabled()


@pytest.mark.tc("UI_88")
def test_switch_bnpl_to_cod_resets_fields(cart):
    payment = PaymentPage(cart)
    _go_to_payment_step(payment)

    payment.select_payment_method("buy-now-pay-later")
    # 2-1. 드롭다운에 "Buy Now Pay Later" 노출
    expect(payment.selected_payment_method).to_have_text("Buy Now Pay Later")
    # 2-2. [Monthly Installments] 드롭다운 노출
    expect(payment.monthly_installments).to_be_visible()
    # 3. 비활성 상태의 [Check payment] 버튼 노출
    expect(payment.check_payment_button).to_have_text("Check payment")
    expect(payment.check_payment_button).to_be_disabled()

    payment.select_payment_method("cash-on-delivery")
    # 4. 드롭다운에 "Cash on Delivery" 노출
    expect(payment.selected_payment_method).to_have_text("Cash on Delivery")
    # 5-1. [Monthly Installments] 드롭다운 미노출
    expect(payment.monthly_installments).to_be_hidden()
    # 5-2. 활성 상태의 [Check payment] 버튼 노출
    expect(payment.check_payment_button).to_have_text("Check payment")
    expect(payment.check_payment_button).to_be_enabled()


@pytest.mark.tc("UI_89")
@pytest.mark.spec_undefined
def test_payment_step_indicator(cart):
    payment = PaymentPage(cart)
    _go_to_payment_step(payment)

    # 2. 상단에 결제 단계가 번호와 함께 노출 (CART 1, SIGN IN 2, BILLING ADDRESS 3, PAYMENT 4)
    expect(payment.step_labels).to_have_text(
        ["CART", "SIGN IN", "BILLING ADDRESS", "PAYMENT"], use_inner_text=True
    )
    expect(payment.step_numbers).to_have_text(["1", "2", "3", "4"])
    for label in payment.step_labels.all():
        expect(label).to_be_visible()


@pytest.mark.tc("UI_90")
def test_billing_street_state_empty_disables_proceed(cart):
    payment = PaymentPage(cart)
    _go_to_address_step(payment)

    lookup = payment.fill_address_by_lookup(COUNTRY, postcode=POSTCODE, house_number=HOUSE_NUMBER)
    # 2. 입력 필드 내 입력한 값 노출
    _expect_lookup_inputs(payment)

    payment.clear_fields(payment.street, payment.state)
    # 3. [Street], [State] 필드 값 미입력 상태 노출, [City] 필드 값 유지
    expect(payment.street).to_have_value("")
    expect(payment.state).to_have_value("")
    expect(payment.city).to_have_value(lookup["city"])
    # 4. 비활성 상태의 [Proceed to checkout] 버튼 노출
    expect(payment.proceed_from_address).to_be_visible()
    expect(payment.proceed_from_address).to_be_disabled()


@pytest.mark.tc("UI_91")
def test_billing_street_city_empty_disables_proceed(cart):
    payment = PaymentPage(cart)
    _go_to_address_step(payment)

    lookup = payment.fill_address_by_lookup(COUNTRY, postcode=POSTCODE, house_number=HOUSE_NUMBER)
    # 2. 입력 필드 내 입력한 값 노출
    _expect_lookup_inputs(payment)

    payment.clear_fields(payment.street, payment.city)
    # 3. [Street], [City] 필드 값 미입력 상태 노출, [State] 필드 값 유지
    expect(payment.street).to_have_value("")
    expect(payment.city).to_have_value("")
    expect(payment.state).to_have_value(lookup["state"])
    # 4. 비활성 상태의 [Proceed to checkout] 버튼 노출
    expect(payment.proceed_from_address).to_be_visible()
    expect(payment.proceed_from_address).to_be_disabled()
