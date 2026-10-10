import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import CartPage, to_amount
from pages.payment_page import PaymentPage


@pytest.mark.tc("UI_24")
def test_cart_button(cart_ready):
    detail = cart_ready

    # 장바구니 버튼 활성화 확인
    expect(detail.add_to_cart).to_be_enabled()

    detail.add()
    # 장바구니 추가 토스트 메시지 확인 (expect 자동 대기)
    expect(detail.added_toast).to_be_visible()


@pytest.mark.tc("UI_25")
def test_cart_quantity_from_detail(cart_ready):
    detail = cart_ready
    product_name = detail.name.inner_text().strip()

    # 2. 수량 입력란에 "3" 입력 후 입력란 밖 클릭 → 수량 "3" 노출
    detail.set_quantity("3")
    expect(detail.quantity).to_have_value("3")

    detail.add()
    expect(detail.added_toast).to_be_visible()
    detail.open_cart()

    # 4. 장바구니 리스트 내 해당 상품 수량 "3" 노출
    cart_page = CartPage(detail.page)
    expect(cart_page.row(product_name)).to_have_count(1)
    expect(cart_page.row_quantity(product_name)).to_have_value("3")


@pytest.mark.tc("UI_26")
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


@pytest.mark.tc("UI_27")
def test_cart_quantity_update_totals(cart):
    cart_page = CartPage(cart)

    # 1. 장바구니 리스트에 상품 노출
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()
    unit_price = to_amount(cart_page.row_unit_price(product_name).inner_text())
    expected_line_total = f"${unit_price * 3:.2f}"

    cart_page.set_row_quantity(product_name, "3")

    # 2-1. "Product quantity updated." 토스트 메시지 노출
    expect(cart_page.quantity_updated_toast).to_be_visible()
    # 2-2. 수량 "3" 노출
    expect(cart_page.row_quantity(product_name)).to_have_value("3")
    # 3-1. 단가 3배의 행 합계 금액 노출
    expect(cart_page.row_line_price(product_name)).to_have_text(expected_line_total)
    # 3-2. 카트 합계 금액이 행 합계 금액과 동일하게 갱신
    expect(cart_page.cart_total).to_have_text(expected_line_total)


@pytest.mark.tc("UI_28")
def test_cart_quantity_corrected_to_bounds(cart):
    cart_page = CartPage(cart)

    # 1. 장바구니 리스트에 상품 노출
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()
    quantity = cart_page.row_quantity(product_name)

    # 2. 수량 "0" 입력 후 입력란 밖 클릭 → 수량 "1"로 보정되어 노출
    cart_page.set_row_quantity(product_name, "0")
    expect(quantity).to_have_value("1")

    # 3. 수량 "1000000000" 입력 후 입력란 밖 클릭 → 수량 "999999999"로 보정되어 노출
    cart_page.set_row_quantity(product_name, "1000000000")
    try:
        expect(quantity).to_have_value("999999999")
    except AssertionError:
        if quantity.input_value() == "99":
            pytest.xfail("백로그 #16: 수량 상한이 스펙(999999999)과 다름. 실제 상한 99로 보정됨")
        raise


@pytest.mark.tc("UI_29")
def test_cart_total_with_two_products(cart_two_items):
    cart_page = CartPage(cart_two_items)

    # 1. 장바구니 리스트에 상품 2종 이상 노출
    expect(cart_page.rows).to_have_count(2)
    titles = [t.strip() for t in cart_page.product_titles.all_inner_texts()]
    assert len(set(titles)) == 2, f"서로 다른 상품 2종이 아님: {titles}"

    # 2. 각 행 합계 금액이 해당 상품 단가와 수량의 곱과 동일하게 노출
    line_totals = []
    for title in titles:
        unit_price = to_amount(cart_page.row_unit_price(title).inner_text())
        quantity = int(cart_page.row_quantity(title).input_value())
        line_total = round(unit_price * quantity, 2)
        expect(cart_page.row_line_price(title)).to_have_text(f"${line_total:.2f}")
        line_totals.append(line_total)

    # 3. 카트 합계 금액이 각 행 합계 금액의 합과 동일하게 노출
    expect(cart_page.cart_total).to_have_text(f"${sum(line_totals):.2f}")


@pytest.mark.tc("UI_30")
def test_cart_remove_one_recalculates_total(cart_two_items):
    cart_page = CartPage(cart_two_items)

    # 1. 장바구니 리스트에 상품 2종 이상 노출
    expect(cart_page.rows).to_have_count(2)
    removed, remaining = [t.strip() for t in cart_page.product_titles.all_inner_texts()]
    remaining_line_total = cart_page.row_line_price(remaining).inner_text().strip()

    cart_page.remove_item(removed)

    # 2. 선택한 상품 행이 제거된 상태로 노출, 나머지 상품 행은 유지된 상태로 노출
    expect(cart_page.row(removed)).to_have_count(0)
    expect(cart_page.row(remaining)).to_have_count(1)
    expect(cart_page.rows).to_have_count(1)

    # 3. 카트 합계 금액이 남은 상품 행 합계 금액과 동일하게 변경되어 노출
    expect(cart_page.row_line_price(remaining)).to_have_text(remaining_line_total)
    expect(cart_page.cart_total).to_have_text(remaining_line_total)


@pytest.mark.tc("UI_31")
@pytest.mark.xfail(
    strict=True,
    reason="백로그 #15: 빈 장바구니 문구가 스펙(\"Your shopping cart is empty\")과 다름. 실제 \"The cart is empty. Nothing to display.\"",
)
def test_cart_remove_last_item_shows_empty(cart):
    cart_page = CartPage(cart)

    # 1. 장바구니 리스트에 상품 1건 노출
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()

    cart_page.remove_item(product_name)

    # 2-1. 상품 행 제거
    expect(cart_page.row(product_name)).to_have_count(0)
    expect(cart_page.rows).to_have_count(0)
    # 2-2. "Your shopping cart is empty" 문구 노출
    expect(cart_page.empty_message).to_be_visible()


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_32")
def test_cart_remove_all_hides_proceed_to_checkout(cart):
    cart_page = CartPage(cart)
    checkout = PaymentPage(cart)

    # 1. 장바구니 리스트에 상품 1건 노출
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()

    # 2. [Proceed to checkout] 버튼 노출
    expect(checkout.proceed_from_cart).to_be_visible()

    cart_page.remove_item(product_name)

    # 3. 상품 행이 제거된 상태로 노출
    expect(cart_page.row(product_name)).to_have_count(0)
    expect(cart_page.rows).to_have_count(0)
    # 4. [Proceed to checkout] 버튼 미노출 상태로 노출
    expect(checkout.proceed_from_cart).to_be_hidden()
