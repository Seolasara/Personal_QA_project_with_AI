import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import ProductDetailPage
from pages.category_page import CategoryPage, RentalsPage

NOT_BLANK = re.compile(r"\S")
PRICE_TEXT = re.compile(r"^\s*\$\d+(\.\d{2})?\s*$")


@pytest.mark.tc("UI_42")
def test_main_grid_card_contents(guest_catalog):
    catalog = guest_catalog
    cards = catalog.listed_links
    expect(cards).not_to_have_count(0)

    # 1. 모든 상품 카드에 상품 이미지, 상품명, 가격 노출
    for index, card in enumerate(cards.all()):
        image = catalog.card_image(card)
        expect(image).to_be_visible()
        assert catalog.image_natural_width(image) > 0, f"{index + 1}번째 카드 이미지가 로드되지 않음"
        expect(catalog.card_name(card)).to_have_text(NOT_BLANK)
        expect(catalog.card_price(card)).to_have_text(PRICE_TEXT)


@pytest.mark.tc("UI_43")
def test_pagination_page_number(guest_catalog):
    catalog = guest_catalog

    # 1. 상품 그리드 하단에 페이지 이동 버튼 노출
    expect(catalog.pagination).to_be_visible()
    expect(catalog.page_number_button(2)).to_be_visible()

    # 2. 1페이지 상품 리스트 노출
    first_page = catalog.listed_product_names()
    assert first_page, "1페이지 상품 리스트가 비어 있음"

    catalog.go_to_page(2)
    # 4. 1페이지와 다른 상품 리스트 노출
    second_page = catalog.listed_product_names()
    assert second_page, "2페이지 상품 리스트가 비어 있음"
    overlap = set(first_page) & set(second_page)
    assert not overlap, f"2페이지에 1페이지 상품이 다시 노출됨: {sorted(overlap)}"


@pytest.mark.tc("UI_49")
def test_category_menu_page_title(guest_catalog):
    category = CategoryPage(guest_catalog.page)
    # 카드에는 카테고리가 없어, 목록 상품을 별도 탭의 상세 페이지 카테고리 배지로 확인한다
    detail = ProductDetailPage(category.page.context.new_page())

    category.open_categories_menu()
    # 1. 카테고리 메뉴 항목 노출
    expect(category.nav_category_items).to_have_text(
        ["Hand Tools", "Power Tools", "Other", "Special Tools", "Rentals"]
    )

    category.select_category("Hand Tools")
    # 2. "Category: Hand Tools" 페이지 제목 노출
    expect(category.page_title).to_have_text("Category: Hand Tools")

    # 3. 선택한 카테고리 상품 리스트 노출: 각 상품의 카테고리가 Hand Tools 또는 그 하위 카테고리
    allowed = set(category.category_filter_names())
    assert "Hand Tools" in allowed, f"카테고리 필터에 Hand Tools 가 없음: {sorted(allowed)}"
    urls = category.listed_product_urls()
    assert urls, "Hand Tools 카테고리 상품 리스트가 비어 있음"
    for url in urls:
        detail.open(url)
        expect(detail.category_badge).to_be_visible()
        badge = detail.category_badge.inner_text().strip()
        assert badge in allowed, f"Hand Tools 범위 밖 카테고리 상품 노출: {url} ({badge})"


@pytest.mark.tc("UI_50")
@pytest.mark.issue("QA-15")  # 백로그 #29: 카테고리 페이지 Price Range 없음. 고쳐질 때까지 실패로 집계
def test_category_page_filters(guest_catalog):
    category = CategoryPage(guest_catalog.page)
    category.open_categories_menu()
    category.select_category("Hand Tools")

    # 1. 카테고리 페이지 정상 노출
    expect(category.page_title).to_have_text("Category: Hand Tools")
    expect(category.listed_names).not_to_have_count(0)

    # 2. 하위 카테고리 체크박스, 브랜드 체크박스, 정렬 드롭다운, 페이지 이동 버튼, 가격 슬라이더 노출
    subcategories = [name for name in category.category_filter_names() if name != "Hand Tools"]
    assert subcategories, "Hand Tools 하위 카테고리 체크박스가 없음"
    expect(category.category_filters.first).to_be_visible()
    expect(category.brand_filters).not_to_have_count(0)
    expect(category.brand_filters.first).to_be_visible()
    expect(category.sort_select).to_be_visible()
    expect(category.pagination).to_be_visible()
    expect(category.price_slider).to_be_visible()


@pytest.mark.tc("UI_53")
def test_out_of_stock_card_label(guest_catalog):
    catalog = guest_catalog

    card = catalog.find_first_out_of_stock_card()
    assert card is not None, "사전 조건 불충족: 상품 리스트 전체에 품절 상품이 없음"
    # 1. 품절 상품 카드에 "Out of stock" 문구 노출
    expect(catalog.card_out_of_stock(card)).to_be_visible()
    expect(catalog.card_out_of_stock(card)).to_have_text("Out of stock")


@pytest.mark.tc("UI_62")
def test_rentals_page_list(guest_catalog):
    category = CategoryPage(guest_catalog.page)
    rentals = RentalsPage(guest_catalog.page)

    category.open_categories_menu()
    category.nav_category_item("Rentals").click()
    # 1. "Rentals" 제목의 렌탈 페이지 정상 노출
    expect(rentals.page_title).to_have_text("Rentals")

    # 2-1. 렌탈 상품 1건 이상 노출
    expect(rentals.items.first).to_be_visible()

    # 2-2. 각 렌탈 상품의 이미지, 이름, 설명 노출
    for index, item in enumerate(rentals.items.all()):
        image = rentals.item_image(item)
        expect(image).to_be_visible()
        assert rentals.image_natural_width(image) > 0, f"{index + 1}번째 렌탈 상품 이미지가 로드되지 않음"
        expect(rentals.item_name(item)).to_have_text(NOT_BLANK)
        expect(rentals.item_description(item)).to_have_text(NOT_BLANK)
