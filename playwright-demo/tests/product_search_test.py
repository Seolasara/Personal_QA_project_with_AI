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


@pytest.mark.tc("UI_10")
def test_product_filter_category_and_brand(guest_catalog):
    catalog = guest_catalog
    # 카드에는 카테고리와 브랜드가 없어, 목록 상품을 별도 탭의 상세 페이지 배지로 확인한다
    detail = ProductDetailPage(catalog.page.context.new_page())

    # 1. 전체 상품 리스트 정상 노출
    expect(catalog.listed_names).not_to_have_count(0)

    catalog.check_category("Hammer")
    # 2-1. "Hammer" 체크박스에 체크 선택 상태로 노출
    expect(catalog.category_checkbox("Hammer")).to_be_checked()
    # 2-2. "Hammer" 해당 상품 리스트 노출
    hammer_urls = catalog.listed_product_urls()
    assert hammer_urls, "Hammer 카테고리 선택 후 상품 리스트가 비어 있음"
    for url in hammer_urls:
        detail.open(url)
        expect(detail.category_badge).to_have_text("Hammer")

    brand = catalog.first_brand_name()
    catalog.check_brand(brand)
    # 3-1. 선택한 브랜드 체크박스에 체크 선택 상태로 노출
    expect(catalog.brand_checkbox(brand)).to_be_checked()
    # 3-2. "Hammer" 카테고리와 선택한 브랜드를 모두 만족하는 상품만 리스트에 노출
    both_urls = catalog.listed_product_urls()
    assert both_urls, f"Hammer + {brand} 선택 후 상품 리스트가 비어 있음"
    assert set(both_urls) <= set(hammer_urls), "브랜드 추가 선택 후 Hammer 목록에 없던 상품이 노출됨"
    for url in both_urls:
        detail.open(url)
        expect(detail.category_badge).to_have_text("Hammer")
        expect(detail.brand_badge).to_have_text(brand)


@pytest.mark.tc("UI_11")
def test_product_price_slider_max(guest_catalog):
    catalog = guest_catalog

    # 1. 가격 슬라이더 기본 범위 1~100 노출 (라벨은 통화 기호 없이 숫자만 표시됨, 2026-10-10 확인)
    expect(catalog.price_min_label).to_have_text("1")
    expect(catalog.price_max_label).to_have_text("100")

    catalog.lower_max_price(presses=2)
    # 2. 가격 슬라이더 최대값이 이동한 값으로 노출
    moved_max = catalog.price_max_handle.get_attribute("aria-valuenow")
    assert int(moved_max) < 100, f"최대값 핸들이 기본값보다 낮아지지 않음: {moved_max}"
    expect(catalog.price_max_label).to_have_text(moved_max)

    # 3. 상품 리스트의 모든 상품 가격이 화면에 표시된 범위 내 금액으로 노출
    low = float(catalog.price_min_label.inner_text())
    high = float(catalog.price_max_label.inner_text())
    prices = catalog.listed_product_prices()
    assert prices, "가격 범위 조정 후 상품 리스트가 비어 있음"
    out_of_range = [price for price in prices if not low <= price <= high]
    assert not out_of_range, f"범위 {low}~{high} 밖 가격 노출: {out_of_range}"


@pytest.mark.tc("UI_12")
def test_product_sort_options(guest_catalog):
    catalog = guest_catalog

    catalog.sort_by("Name (A - Z)")
    # 2. 첫 페이지 상품 리스트가 이름 오름차순으로 노출
    names = [name.casefold() for name in catalog.listed_product_names()]
    assert len(names) >= 2, "정렬을 확인할 상품이 2건 미만"
    assert names == sorted(names), f"이름 오름차순 아님: {names}"

    catalog.sort_by("Name (Z - A)")
    # 3. 첫 페이지 상품 리스트가 이름 내림차순으로 노출
    names = [name.casefold() for name in catalog.listed_product_names()]
    assert len(names) >= 2, "정렬을 확인할 상품이 2건 미만"
    assert names == sorted(names, reverse=True), f"이름 내림차순 아님: {names}"

    catalog.sort_by("Price (Low - High)")
    # 4. 첫 페이지 상품 리스트가 가격 오름차순으로 노출
    prices = catalog.listed_product_prices()
    assert len(prices) >= 2, "정렬을 확인할 상품이 2건 미만"
    assert prices == sorted(prices), f"가격 오름차순 아님: {prices}"

    catalog.sort_by("Price (High - Low)")
    # 5. 첫 페이지 상품 리스트가 가격 내림차순으로 노출
    prices = catalog.listed_product_prices()
    assert len(prices) >= 2, "정렬을 확인할 상품이 2건 미만"
    assert prices == sorted(prices, reverse=True), f"가격 내림차순 아님: {prices}"


@pytest.mark.tc("UI_13")
@pytest.mark.issue("QA-7")  # 백로그 #26: 4자 이상 검색어 단어 시작 일치. 고쳐질 때까지 실패로 집계
def test_product_search_shows_matching_only(guest_catalog):
    catalog = guest_catalog
    # 일치 기준: 상품명에 검색어 포함(부분 일치, 대소문자 무시). 사용자 결정(2026-10-10), 백로그 #26
    expected = sorted(n for n in catalog.collect_all_product_names() if "hammer" in n.casefold())
    assert expected, "사전 조건 미충족: 상품명에 hammer가 포함된 상품 없음"

    catalog.fill_search("hammer")
    # 2. 검색 입력란에 "hammer" 텍스트 노출 (제출 후에는 입력란이 비워져 제출 전에 확인, 2026-10-10 확인)
    expect(catalog.search_query).to_have_value("hammer")

    catalog.submit_search()
    names = catalog.collect_all_product_names()
    # 3-1. "hammer"가 포함된 상품이 누락 없이 노출
    missing = [name for name in expected if name not in names]
    # 3-2. 상품명에 "hammer"가 포함되지 않은 상품 미노출
    not_matching = [name for name in names if "hammer" not in name.casefold()]
    assert not not_matching, f"hammer가 포함되지 않은 상품 노출: {not_matching}"
    assert not missing, f"hammer가 포함된 상품 누락: {missing}"


@pytest.mark.tc("UI_14")
def test_product_search_query_length_bounds(guest_catalog):
    catalog = guest_catalog

    catalog.fill_search("ham")
    # 2. 검색 입력란에 "ham" 텍스트 노출
    expect(catalog.search_query).to_have_value("ham")

    catalog.submit_search()
    # 3. 상품 그리드에 "ham"과 일치하는 상품만 노출
    names = catalog.listed_product_names()
    assert names, "검색 결과 상품이 노출되지 않음"
    not_matching = [name for name in names if "ham" not in name.casefold()]
    assert not not_matching, f"ham과 일치하지 않는 상품 노출: {not_matching}"

    long_term = "h" * 40
    catalog.fill_search(long_term)
    # 4. 검색 입력란에 입력한 40자 문자열 노출
    expect(catalog.search_query).to_have_value(long_term)

    catalog.submit_search()
    # 5. 입력한 40자 문자열과 일치하는 상품만 노출 (일치하는 상품이 없으면 상품 카드 미노출)
    names = catalog.listed_product_names()
    not_matching = [name for name in names if long_term not in name.casefold()]
    assert not not_matching, f"40자 검색어와 일치하지 않는 상품 노출: {not_matching}"
    expect(catalog.listed_links).to_have_count(len(names))


@pytest.mark.tc("UI_15")
def test_product_search_resets_category_filter(guest_catalog):
    catalog = guest_catalog

    catalog.check_category("Pliers")
    # 2. "Pliers" 체크박스에 체크 선택 상태로 노출
    expect(catalog.category_checkbox("Pliers")).to_be_checked()

    catalog.fill_search("hammer")
    # 3. 검색 입력란에 "hammer" 텍스트 노출
    expect(catalog.search_query).to_have_value("hammer")

    catalog.submit_search()
    # 4-1. 상품 그리드에 "hammer"와 일치하는 상품 노출
    names = catalog.listed_product_names()
    assert names, "검색 결과 상품이 노출되지 않음"
    not_matching = [name for name in names if "hammer" not in name.casefold()]
    assert not not_matching, f"hammer와 일치하지 않는 상품 노출: {not_matching}"
    # 4-2. "Pliers" 체크박스에 체크 해제 상태로 노출
    expect(catalog.category_checkbox("Pliers")).not_to_be_checked()


@pytest.mark.tc("UI_16")
def test_product_search_no_results(guest_catalog):
    catalog = guest_catalog

    catalog.fill_search("zzzzzz")
    # 2. 검색 입력란에 "zzzzzz" 텍스트 노출
    expect(catalog.search_query).to_have_value("zzzzzz")

    catalog.submit_search()
    # 3. 상품 카드 미노출
    expect(catalog.listed_links).to_have_count(0)
    expect(catalog.listed_names).to_have_count(0)


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


@pytest.mark.spec_undefined
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


@pytest.mark.tc("UI_23")
def test_out_of_stock_product_add_to_cart_disabled(guest_catalog):
    catalog = guest_catalog

    # 1. 메인 > 품절 상품 상세 페이지 (품절 상품은 고정 id 없이 목록에서 찾는다)
    found = catalog.open_first_out_of_stock_product()
    assert found, "사전 조건 미충족(env): 상품 목록 전체에 품절 상품이 없음"
    detail = ProductDetailPage(catalog.page)

    # 2-1. 빨간색 "Out of stock" 문구 노출
    expect(detail.out_of_stock_label).to_be_visible()
    expect(detail.out_of_stock_label).to_have_text("Out of stock")
    red, green, blue = detail.out_of_stock_color()
    assert red >= 150 and green <= 100 and blue <= 100, (
        f"품절 문구 색이 빨간색이 아님: rgb({red}, {green}, {blue})"
    )
    # 2-2. 비활성 상태의 [Add to cart] 버튼 노출
    expect(detail.add_to_cart).to_be_visible()
    expect(detail.add_to_cart).to_be_disabled()
