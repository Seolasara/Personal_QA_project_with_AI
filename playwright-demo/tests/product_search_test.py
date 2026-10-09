import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import ProductDetailPage


@pytest.mark.tc("UI_09")
def test_product_checkbox(catalog):
    # 체크박스 선택
    catalog.filter_by_category("Hammer")
    # 체크박스 선택 확인
    expect(catalog.category_checkbox("Hammer")).to_be_checked()


@pytest.mark.tc("UI_17")
def test_product_get(catalog):
    catalog.filter_by_category("Hammer")

    # 리스트 개수가 0이 아님을 확인
    expect(catalog.product_cards).not_to_have_count(0)
    # 상품명에 "hammer" 텍스트 포함 확인 (대소문자 구분 없음)
    expect(catalog.product_grid).to_contain_text(re.compile("hammer", re.IGNORECASE))

    catalog.open_first_product()
    detail = ProductDetailPage(catalog.page)

    # 상품 상세 페이지 url 확인
    expect(catalog.page).to_have_url(re.compile(r"/product/"))
    # 상품명 "hammer" 포함 확인
    expect(detail.name).to_contain_text(re.compile("hammer", re.IGNORECASE))
    # 상품 설명 / 단가 / 수량 박스 / 장바구니 버튼 표시 확인
    expect(detail.description).to_be_visible()
    expect(detail.unit_price).to_be_visible()
    expect(detail.quantity).to_be_visible()
    expect(detail.add_to_cart).to_be_visible()


@pytest.mark.tc("UI_18")
def test_product_quantity_plus_minus(product_detail):
    detail = product_detail

    # 2. 수량 "1" 노출
    expect(detail.quantity).to_have_value("1")

    detail.increase()
    # 3. 수량 "2" 노출
    expect(detail.quantity).to_have_value("2")

    detail.decrease()
    # 4. 수량 "1" 노출
    expect(detail.quantity).to_have_value("1")


@pytest.mark.tc("UI_19")
def test_product_quantity_minus_at_one_stays_one(product_detail):
    detail = product_detail

    # 2. 수량 "1" 노출
    expect(detail.quantity).to_have_value("1")

    detail.decrease()
    # 3. 수량 "1" 유지 상태로 노출
    expect(detail.quantity).to_have_value("1")


@pytest.mark.tc("UI_20")
def test_product_quantity_zero_or_negative_corrected_to_one(product_detail):
    detail = product_detail

    detail.set_quantity("0")
    # 2. 수량 "1"로 보정되어 노출
    expect(detail.quantity).to_have_value("1")

    detail.set_quantity("-1")
    # 3. 수량 "1"로 보정되어 노출
    expect(detail.quantity).to_have_value("1")


@pytest.mark.tc("UI_21")
def test_product_quantity_cleared_corrected_to_one(product_detail):
    detail = product_detail

    detail.set_quantity("")
    # 2. 수량 "1"로 보정되어 노출
    expect(detail.quantity).to_have_value("1")


@pytest.mark.tc("UI_22")
@pytest.mark.xfail(
    strict=True,
    reason="백로그 #16: 수량 상한이 스펙(999999999)과 다름. 실제 상한 99라 100이 99로 보정됨",
)
def test_product_quantity_upper_bound(product_detail):
    detail = product_detail

    detail.set_quantity("100")
    # 2. 수량 "100" 유지 상태로 노출
    expect(detail.quantity).to_have_value("100")
