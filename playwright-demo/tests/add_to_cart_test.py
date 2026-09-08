import re
import pytest
from playwright.sync_api import expect


@pytest.mark.tc("QA-09")
def test_cart_button(cart_ready):
    page = cart_ready
    # 장바구니 버튼 활성화 확인
    expect(page.get_by_role("button", name="Add to cart")).to_be_enabled()

    page.get_by_role("button", name="Add to cart").click()
    page.wait_for_timeout(1000)
    # 장바구니 추가 토스트 메시지 확인
    expect(page.get_by_label("Product added to shopping cart.")).to_be_visible()


@pytest.mark.tc("QA-10")
def test_cart_check(cart_ready):
    page = cart_ready
    # 수량 1개 이상 확인
    expect(page.locator('[data-test="quantity"]')).to_have_value("1")

    page.get_by_role("button", name="Add to cart").click()
    page.locator('[data-test="nav-cart"]').click()

    # 장바구니 페이지 이동 확인
    expect(page).to_have_url("https://practicesoftwaretesting.com/checkout")

    cart_items = page.locator('tr:has([data-test="product-title"])')
    # 장바구니 리스트 1개 이상 확인
    expect(cart_items).not_to_have_count(0)

    product = page.locator('[data-test="product-title"]')
    # 리스트 내 추가 상품 확인
    expect(product).to_contain_text(re.compile("hammer", re.IGNORECASE))