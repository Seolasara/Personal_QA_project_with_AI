import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import CartPage, CatalogPage, ProductDetailPage, to_amount
from pages.login_page import LoginPage
from pages.payment_page import PaymentPage
from config import SITE_URL


@pytest.mark.tc("UI_24")
@pytest.mark.smoke
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
    detail.open_cart_loaded()

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
    detail.open_cart_loaded()

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
@pytest.mark.issue("QA-11")  # 백로그 #16: 수량 상한 99. 고쳐질 때까지 실패로 집계
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
    expect(quantity).to_have_value("999999999")


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
@pytest.mark.issue("QA-10")  # 백로그 #15: 빈 장바구니 문구가 스펙과 다름. 고쳐질 때까지 실패로 집계
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


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_64")
def test_cart_negative_quantity_corrected_to_one(cart):
    cart_page = CartPage(cart)

    # 1. 장바구니 리스트에 상품 노출
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()

    cart_page.set_row_quantity(product_name, "-3")

    # 2-1. "Product quantity updated." 토스트 메시지 노출
    expect(cart_page.quantity_updated_toast).to_be_visible()
    # 2-2. 수량 "1"로 보정되어 노출
    expect(cart_page.row_quantity(product_name)).to_have_value("1")


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_65")
def test_cart_same_product_twice_badge_two(product_detail):
    detail = product_detail
    header = CatalogPage(detail.page)

    # 2. [Add to cart] 클릭 → "Product added to shopping cart." 토스트 노출
    detail.add()
    expect(detail.added_toast).to_be_visible()

    # 3. [Add to cart] 한 번 더 클릭 → 토스트가 한 번 더 노출
    detail.add()
    expect(detail.added_toast).to_have_count(2)

    # 4. 헤더 장바구니 아이콘 배지에 "2" 노출
    expect(header.cart_badge).to_have_text("2")


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_66")
def test_cart_header_icon_and_badge_after_add(guest_catalog):
    catalog = guest_catalog

    # 1. 빈 장바구니 상태의 메인 헤더에 장바구니 아이콘 미노출
    expect(catalog.nav_cart).to_be_hidden()

    # 2. 메인 > 상품 상세 페이지
    catalog.filter_by_category("Hammer")
    catalog.open_first_in_stock_product()
    detail = ProductDetailPage(catalog.page)

    # 3. [Add to cart] 클릭 → "Product added to shopping cart." 토스트 노출
    detail.add()
    expect(detail.added_toast).to_be_visible()

    # 4. 헤더에 장바구니 아이콘과 배지 "1" 노출
    expect(catalog.nav_cart).to_be_visible()
    expect(catalog.cart_badge).to_have_text("1")


@pytest.mark.tc("UI_67")
def test_cart_table_columns(cart):
    cart_page = CartPage(cart)

    # 1. 장바구니 페이지 정상 이동
    expect(cart).to_have_url(CartPage.URL)
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()

    # 2-1. 표에 "Item", "Quantity", "Price", "Total" 컬럼 노출
    for column in ("Item", "Quantity", "Price", "Total"):
        expect(cart_page.column_header(column)).to_be_visible()

    # 2-2. 상품 행에 상품명, 수량 입력란, 가격, 행 합계, [X] 버튼 노출
    assert product_name, "상품명이 비어 있음"
    expect(cart_page.product_titles.first).to_be_visible()
    expect(cart_page.row_quantity(product_name)).to_be_editable()
    expect(cart_page.row_unit_price(product_name)).to_have_text(re.compile(r"^\$\d"))
    expect(cart_page.row_line_price(product_name)).to_have_text(re.compile(r"^\$\d"))
    expect(cart_page.row_remove_button(product_name)).to_be_visible()


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_68")
def test_cart_remove_last_item_shows_deleted_toast(cart):
    cart_page = CartPage(cart)
    header = CatalogPage(cart)

    # 1. 장바구니 리스트에 상품 1건 노출
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()

    cart_page.remove_item(product_name)

    # 2-1. "Product deleted." 토스트 메시지 노출
    expect(cart_page.deleted_toast).to_be_visible()
    # 2-2. 헤더 장바구니 아이콘 미노출
    expect(header.nav_cart).to_be_hidden()


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_69")
def test_cart_continue_shopping_goes_home(cart):
    cart_page = CartPage(cart)
    home = CatalogPage(cart)

    # 1. 장바구니 리스트에 상품 노출
    expect(cart_page.rows).not_to_have_count(0)

    cart_page.continue_shopping.click()

    # 2. 메인 페이지 정상 이동
    expect(cart).to_have_url(f"{SITE_URL}/")
    expect(home.listed_names.first).to_be_visible()


@pytest.mark.spec_undefined
@pytest.mark.tc("UI_70")
def test_cart_kept_after_logout(cart):
    cart_page = CartPage(cart)
    header = LoginPage(cart)
    home = CatalogPage(cart)

    # 사전 조건: 장바구니 내 상품 1건만 존재 (로그아웃 전 담은 상품명 기록)
    expect(cart_page.rows).to_have_count(1)
    product_name = cart_page.product_titles.first.inner_text().strip()

    # 1. 메인 페이지 헤더 유저 이름 클릭
    cart.goto(f"{SITE_URL}/")
    header.header_user_menu.click()

    # 2. [Sign out] → 메인 페이지로 리다이렉팅, 헤더에 [Sign in] 노출
    header.header_sign_out.click()
    expect(cart).to_have_url(f"{SITE_URL}/")
    expect(header.header_sign_in).to_be_visible()

    # 3. 헤더 장바구니 아이콘 배지에 "1" 노출
    expect(home.cart_badge).to_have_text("1")

    # 4. 헤더 장바구니 아이콘 클릭 → 로그아웃 전 담은 상품 노출
    home.open_cart_loaded()
    expect(cart_page.row(product_name)).to_have_count(1)


@pytest.mark.tc("UI_96")
@pytest.mark.live_ui
def test_cart_continue_shopping_and_proceed_texts(guest_cart):
    cart_page = CartPage(guest_cart)
    payment = PaymentPage(guest_cart)

    # 1. 장바구니 페이지 정상 이동
    expect(guest_cart).to_have_url(CartPage.URL)
    expect(cart_page.rows).not_to_have_count(0)

    # 2-1. [Continue Shopping] 버튼 노출
    expect(cart_page.continue_shopping).to_be_visible()
    expect(cart_page.continue_shopping).to_have_text("Continue Shopping")
    # 2-2. [Proceed to checkout] 버튼 노출
    expect(payment.proceed_from_cart).to_be_visible()
    expect(payment.proceed_from_cart).to_have_text("Proceed to checkout")
