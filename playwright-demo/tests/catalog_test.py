import re

import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage, ProductDetailPage
from pages.category_page import CategoryPage, RentalsPage
from pages.login_page import LoginPage

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


CATEGORY_MENU_ITEMS = ["Hand Tools", "Power Tools", "Other", "Special Tools", "Rentals"]


def _expect_category_products(category: CategoryPage, detail: ProductDetailPage, name: str) -> None:
    """선택한 카테고리 상품 리스트 노출: 각 상품의 카테고리가 name 또는 그 하위 카테고리."""
    # 필터는 상품 목록과 별도 응답으로 그려져, 이전 카테고리의 필터가 남아 있지 않게 name 이 보일 때까지 기다린다
    expect(category.category_filter_labels).to_contain_text([name])
    allowed = set(category.category_filter_names())
    urls = category.listed_product_urls()
    assert urls, f"{name} 카테고리 상품 리스트가 비어 있음"
    for url in urls:
        detail.open(url)
        expect(detail.category_badge).to_be_visible()
        badge = detail.category_badge.inner_text().strip()
        assert badge in allowed, f"{name} 범위 밖 카테고리 상품 노출: {url} ({badge})"


@pytest.mark.tc("UI_49")
def test_category_menu_page_title(guest_catalog):
    category = CategoryPage(guest_catalog.page)
    # 카드에는 카테고리가 없어, 목록 상품을 별도 탭의 상세 페이지 카테고리 배지로 확인한다
    detail = ProductDetailPage(category.page.context.new_page())

    # TC 스텝대로 메인 → Hand Tools → Power Tools → Other 를 이어서 이동한다
    for name in ("Hand Tools", "Power Tools", "Other"):
        category.open_categories_menu()
        # 1, 4, 7. 카테고리 메뉴 항목 노출
        expect(category.nav_category_items).to_have_text(CATEGORY_MENU_ITEMS)

        category.select_category(name)
        # 2, 5, 8. "Category: <카테고리명>" 페이지 제목 노출
        expect(category.page_title).to_have_text(f"Category: {name}")

        # 3, 6, 9. 선택한 카테고리 상품 리스트 노출
        _expect_category_products(category, detail, name)


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


@pytest.mark.tc("UI_92")
@pytest.mark.live_ui
def test_main_header_menu_and_sidebar_titles(guest_catalog):
    catalog = CategoryPage(guest_catalog.page)
    header = LoginPage(guest_catalog.page)

    # 1. 헤더에 메뉴 노출: "Home", "Categories", "Contact", "Sign in"
    expect(catalog.nav_home).to_have_text("Home")
    expect(catalog.nav_categories).to_have_text("Categories")
    expect(catalog.nav_contact).to_have_text("Contact")
    expect(header.header_sign_in).to_have_text("Sign in")

    # 2. 좌측 영역 제목 노출: "Sort", "Price Range", "Search", "Filters" (정확 일치, 앞 아이콘 공백은 무시)
    expect(catalog.sidebar_titles).to_have_text(["Sort", "Price Range", "Search", "Filters"])

    # 3. 검색 영역에 [Search] 버튼 노출
    expect(catalog.search_submit).to_be_visible()
    expect(catalog.search_submit).to_have_text("Search")


@pytest.mark.tc("UI_93")
@pytest.mark.live_ui
def test_header_home_returns_to_main(login_page):
    home = CatalogPage(login_page.page)

    # 1. 로그인 페이지 정상 노출
    expect(login_page.page).to_have_url(LoginPage.LOGIN_URL)
    expect(login_page.form).to_be_visible()

    home.nav_home.click()

    # 2. 메인 페이지 이동, 상품 카드 노출
    expect(login_page.page).to_have_url(LoginPage.HOME_URL)
    expect(home.listed_links.first).to_be_visible()
    expect(home.listed_names.first).to_have_text(NOT_BLANK)


@pytest.mark.tc("UI_99")
def test_category_page_sort_name_desc(guest_catalog):
    category = CategoryPage(guest_catalog.page)
    category.open_categories_menu()
    category.select_category("Hand Tools")

    # 1. Hand Tools 카테고리 페이지 정상 노출
    expect(category.page_title).to_have_text("Category: Hand Tools")
    expect(category.listed_names).not_to_have_count(0)

    category.sort_by("Name (Z - A)")
    # 2. 첫 페이지 상품 리스트가 이름 내림차순으로 노출
    names = [name.casefold() for name in category.listed_product_names()]
    assert len(names) >= 2, "정렬을 확인할 상품이 2건 미만"
    assert names == sorted(names, reverse=True), f"이름 내림차순 아님: {names}"
