import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import CartPage


@pytest.mark.tc("QA-09")
def test_cart_button(cart_ready):
    detail = cart_ready

    # 장바구니 버튼 활성화 확인
    expect(detail.add_to_cart).to_be_enabled()

    detail.add()
    # 장바구니 추가 토스트 메시지 확인 (expect 자동 대기)
    expect(detail.added_toast).to_be_visible()


@pytest.mark.tc("QA-10")
def test_cart_check(cart_ready):
    detail = cart_ready

    # 수량 1개 이상 확인
    expect(detail.quantity).to_have_value("1")

    detail.add()
    detail.open_cart()

    cart_page = CartPage(detail.page)
    # 장바구니 페이지 이동 확인
    expect(detail.page).to_have_url(CartPage.URL)
    # 장바구니 리스트 1개 이상 확인
    expect(cart_page.rows).not_to_have_count(0)
    # 리스트 내 추가 상품 확인
    expect(cart_page.product_titles).to_contain_text(re.compile("hammer", re.IGNORECASE))
