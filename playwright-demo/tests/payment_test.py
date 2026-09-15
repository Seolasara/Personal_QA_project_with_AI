import pytest
from playwright.sync_api import expect

from pages.payment_page import PaymentPage

BILLING = dict(
    postcode="12345",
    house_number="123",
    street="Seoul",
    city="Seoul",
    state="Korea",
)


@pytest.mark.tc("QA-11")
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


@pytest.mark.tc("QA-12")
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
