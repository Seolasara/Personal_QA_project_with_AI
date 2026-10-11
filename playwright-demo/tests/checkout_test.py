"""체크아웃 Sign in 단계와 Billing Address 자동 채움 (UI_81~UI_84)."""
import pytest
from playwright.sync_api import expect

from config import TOOLSHOP_EMAIL, TOOLSHOP_PASSWORD
from pages.login_page import LoginPage
from pages.payment_page import PaymentPage


def _go_to_signin_step(payment: PaymentPage) -> None:
    """장바구니(상품 1건 이상) → Sign in 단계로 진행한다."""
    expect(payment.cart_items).not_to_have_count(0)
    payment.go_to_signin_step()


def _expect_login_form_hidden(payment: PaymentPage) -> None:
    for element in (
        payment.signin_heading,
        payment.signin_email,
        payment.signin_password,
        payment.signin_login_button,
    ):
        expect(element).to_be_hidden()


@pytest.mark.tc("UI_81")
def test_guest_signin_step_shows_login_form(guest_cart):
    payment = PaymentPage(guest_cart)

    # 1. 메인 > 장바구니 > Sign in
    _go_to_signin_step(payment)

    # 2. 로그인 폼 노출: "Login" 제목, [Email address], [Password] 필드, [Login] 버튼
    expect(payment.signin_heading).to_be_visible()
    expect(payment.signin_email).to_be_visible()
    expect(payment.signin_password).to_be_visible()
    expect(payment.signin_login_button).to_be_visible()
    expect(payment.signin_login_button).to_have_value("Login")


@pytest.mark.tc("UI_82")
def test_guest_login_in_signin_step_proceeds_to_billing(guest_cart):
    payment = PaymentPage(guest_cart)
    _go_to_signin_step(payment)

    # 2. [Email address] 필드에 입력한 값 노출
    payment.fill_signin_email(TOOLSHOP_EMAIL)
    expect(payment.signin_email).to_have_value(TOOLSHOP_EMAIL)

    # 3. [Password] 필드에 입력한 값 마스킹 상태로 노출
    payment.fill_signin_password(TOOLSHOP_PASSWORD)
    expect(payment.signin_password).to_have_value(TOOLSHOP_PASSWORD)
    expect(payment.signin_password).to_have_attribute("type", "password")

    # 4-1. Sign in 단계의 로그인 폼 미노출 / 4-2. [Proceed to checkout] 버튼 노출
    payment.submit_signin()
    expect(payment.proceed_from_signin).to_be_visible()
    _expect_login_form_hidden(payment)

    # 5. BILLING ADDRESS 페이지 정상 노출
    payment.open_address_step()
    expect(payment.address_heading).to_be_visible()


@pytest.mark.tc("UI_83")
def test_loggedin_signin_step_shows_message_and_proceed(cart):
    payment = PaymentPage(cart)
    user_name = LoginPage(cart).header_user_menu.inner_text().strip()
    assert user_name, "사전 조건: 헤더에 로그인한 사용자 이름이 보여야 한다"

    _go_to_signin_step(payment)

    # 2-3. [Proceed to checkout] 버튼 노출
    expect(payment.proceed_from_signin).to_be_visible()
    # 2-2. 로그인 폼 미노출
    _expect_login_form_hidden(payment)
    # 2-1. "You are already signed in as" 안내 문구와 로그인한 사용자 이름 노출 (스펙 AC5)
    expect(payment.signin_message).to_contain_text(f"You are already signed in as {user_name}")


@pytest.mark.tc("UI_84")
def test_loggedin_billing_prefilled_with_account_address(cart):
    payment = PaymentPage(cart)
    _go_to_signin_step(payment)

    # 1. BILLING ADDRESS 페이지 정상 노출
    payment.open_address_step()
    expect(payment.address_heading).to_be_visible()

    address = payment.fetch_account()["address"]
    assert address["street"] and address["city"], "사전 조건: 계정에 Street와 City 주소가 등록되어 있어야 한다"

    # 2. [Street] 필드에 계정 주소 값이 채워진 상태로 노출
    expect(payment.street).to_have_value(address["street"])
    # 3. [City] 필드에 계정 주소 값이 채워진 상태로 노출
    expect(payment.city).to_have_value(address["city"])
    # 4. [Country] 필드에 계정 국가 값이 선택된 상태로 노출
    expect(payment.selected_country).to_have_text(address["country"])
