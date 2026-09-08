import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import ProductDetailPage


@pytest.mark.tc("QA-07")
def test_product_checkbox(catalog):
    # 체크박스 선택
    catalog.filter_by_category("Hammer")
    # 체크박스 선택 확인
    expect(catalog.category_checkbox("Hammer")).to_be_checked()


@pytest.mark.tc("QA-08")
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
