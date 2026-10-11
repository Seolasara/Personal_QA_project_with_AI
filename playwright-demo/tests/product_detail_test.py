import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import ProductDetailPage


@pytest.mark.tc("UI_54")
def test_product_detail_shows_image_price_and_badges(guest_product_detail):
    detail = guest_product_detail

    # 1. 상품 상세 페이지 정상 노출
    expect(detail.page).to_have_url(re.compile(r"/product/"))
    expect(detail.name).to_be_visible()
    expect(detail.name).not_to_be_empty()

    # 2-1. 상품 이미지 노출
    expect(detail.product_image).to_be_visible()
    # 2-2. 상품 가격 노출
    expect(detail.unit_price).to_be_visible()
    expect(detail.unit_price).to_have_text(re.compile(r"^\s*\$?\d+(\.\d{2})?\s*$"))

    # 3-1. 카테고리 배지 노출
    expect(detail.category_badge).to_be_visible()
    expect(detail.category_badge).not_to_be_empty()
    # 3-2. 브랜드 배지 노출
    expect(detail.brand_badge).to_be_visible()
    expect(detail.brand_badge).not_to_be_empty()


@pytest.mark.tc("UI_55")
@pytest.mark.spec_undefined
def test_product_detail_shows_specifications_table(guest_product_detail):
    detail = guest_product_detail

    # 1. 상품 상세 페이지 정상 노출
    expect(detail.page).to_have_url(re.compile(r"/product/"))
    expect(detail.name).to_be_visible()

    # 2. "Specifications" 표 노출
    expect(detail.specs_title).to_have_text("Specifications")
    expect(detail.specs_table).to_be_visible()
    expect(detail.spec_rows).not_to_have_count(0)


@pytest.mark.tc("UI_56")
def test_product_detail_shows_related_products(guest_product_detail):
    detail = guest_product_detail

    # 1. 상품 상세 페이지 정상 노출
    expect(detail.page).to_have_url(re.compile(r"/product/"))
    expect(detail.name).to_be_visible()

    # 2. 상품 정보 아래에 "Related products" 영역 노출
    expect(detail.related_products_heading).to_be_visible()
    expect(detail.related_product_titles).not_to_have_count(0)
    heading_top = detail.related_products_heading.bounding_box()["y"]
    main_info_bottom = detail.add_to_cart.bounding_box()["y"]
    assert heading_top > main_info_bottom, (
        f"Related products 영역(y={heading_top})이 상품 정보(y={main_info_bottom})보다 위에 노출됨"
    )


@pytest.mark.tc("UI_57")
def test_product_quantity_buttons_from_typed_value(guest_product_detail):
    detail = guest_product_detail

    detail.set_quantity("5")
    # 2. 수량 "5" 노출
    expect(detail.quantity).to_have_value("5")

    detail.increase()
    # 3. 수량 "6" 노출
    expect(detail.quantity).to_have_value("6")

    detail.decrease()
    # 4. 수량 "5" 노출
    expect(detail.quantity).to_have_value("5")


@pytest.mark.tc("UI_58")
@pytest.mark.spec_undefined
def test_product_quantity_rejects_letters(guest_product_detail):
    detail = guest_product_detail

    detail.type_quantity("abc")
    # 2. 수량 입력란에 입력한 문자 미노출
    expect(detail.quantity).not_to_have_value(re.compile("[a-zA-Z]"))


@pytest.mark.tc("UI_59")
@pytest.mark.spec_undefined
def test_out_of_stock_product_quantity_controls_disabled(guest_catalog):
    catalog = guest_catalog

    # 1. 메인 > 품절 상품 상세 페이지 (품절 상품은 고정 id 없이 목록에서 찾는다)
    found = catalog.open_first_out_of_stock_product()
    assert found, "사전 조건 미충족(env): 상품 목록 전체에 품절 상품이 없음"
    detail = ProductDetailPage(catalog.page)
    expect(detail.out_of_stock_label).to_be_visible()

    # 2-1. 비활성 상태의 수량 [-] 버튼 노출
    expect(detail.decrease_quantity).to_be_visible()
    expect(detail.decrease_quantity).to_be_disabled()
    # 2-2. 비활성 상태의 수량 입력란 노출
    expect(detail.quantity).to_be_visible()
    expect(detail.quantity).to_be_disabled()
    # 2-3. 비활성 상태의 수량 [+] 버튼 노출
    expect(detail.increase_quantity).to_be_visible()
    expect(detail.increase_quantity).to_be_disabled()


@pytest.mark.tc("UI_60")
def test_add_to_favorites_requires_login(guest_product_detail):
    detail = guest_product_detail

    detail.add_favorite()
    # 2. "Unauthorized, can not add product to your favorite list." 알림 노출
    expect(detail.toast_message).to_be_visible()
    expect(detail.toast_message).to_have_text("Unauthorized, can not add product to your favorite list.")
