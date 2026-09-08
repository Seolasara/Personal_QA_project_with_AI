import pytest
from playwright.sync_api import expect
from pages.payment_page import PaymentPage


@pytest.mark.tc("QA-11")
def test_checkout_button(cart):
    payment = PaymentPage(cart)

    # 결제 가능 상품 1개 이상 존재 확인
    expect(payment.product).not_to_have_count(0)
    expect(payment.button1).to_be_enabled()

    payment.cart_step()

    # Sign In 상태 확인
    expect(payment.confirmation).to_be_visible()
    expect(payment.button2).to_be_enabled()
    payment.signin_step()

    # Billing Address 스텝 확인
    expect(payment.address).to_be_visible()

    # Billing Address 폼 채우기
    payment.filling_address(
        "Korea (the Republic of)",
        postcode = "12345",
        house = "123",
        street = "Seoul",
        city = "Seoul",
        state = "Korea"
    )

    # Proceed to checkout 버튼 활성화 확인
    expect(payment.button3).to_be_enabled()
    payment.address_step()

    # 결제 방식 드롭다운 확인
    expect(payment.dropdown2).to_be_enabled()
    payment.payment_step("Cash on Delivery")

    # Confirm 버튼 활성화 확인
    expect(payment.confirm).to_be_enabled()


@pytest.mark.tc("QA-12")
def test_payment_checkout(cart):
    payment = PaymentPage(cart)

    # 결제 가능 상품 1개 이상 존재 확인
    expect(payment.product).not_to_have_count(0)
    expect(payment.button1).to_be_enabled()

    payment.cart_step()

    # Sign In 상태 확인
    expect(payment.confirmation).to_be_visible()
    expect(payment.button2).to_be_enabled()
    payment.signin_step()

    # Billing Address 스텝 확인
    expect(payment.address).to_be_visible()

    # Billing Address 폼 채우기
    payment.filling_address(
        "Korea (the Republic of)",
        postcode = "12345",
        house = "123",
        street = "Seoul",
        city = "Seoul",
        state = "Korea"
    )
    payment.address_step()

    # 결제 방식, Confirm 버튼 클릭
    expect(payment.dropdown2).to_be_enabled()
    payment.payment_step("Cash on Delivery")
    payment.confirm_button()

    # 결제 완료 메시지 확인
    expect(payment.message).to_be_visible()