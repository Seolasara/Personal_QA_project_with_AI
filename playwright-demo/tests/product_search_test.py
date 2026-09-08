import re
from playwright.sync_api import expect


def test_product_checkbox(loggedin_home):
    page = loggedin_home

    # page.get_by_label("Hammer").click()
    # 체크박스 선택
    page.get_by_role("checkbox", name="Hammer").check()
#    # 체크박스 선택 확인
    expect(page.get_by_role("checkbox", name="Hammer")).to_be_checked()


def test_product_get(loggedin_home):
    page = loggedin_home

    # 체크박스 선택
    page.get_by_role("checkbox", name="Hammer").check()

    product_list = page.locator('[data-test="filter_completed"]')
    products = product_list.locator('[data-test^="product-"]')

    # 리스트 개수가 0이 아님을 확인
    expect(products).not_to_have_count(0)
    # 상품명에 "hammer" 텍스트 포함 확인 (대소문자 구분 없음)
    expect(product_list).to_contain_text(re.compile("hammer", re.IGNORECASE))

    products.first.click()
    # 상품 상세 페이지 url 확인
    expect(page).to_have_url(re.compile(r"/product/"))
    # 상품명 "hammer" 포함 확인
    expect(page.locator('[data-test="product-name"]')).to_contain_text(re.compile("hammer", re.IGNORECASE))

    # 상품 설명 표시 확인
    expect(page.locator('[data-test="product-description"]')).to_be_visible()
    # 단가 표시 확인
    expect(page.get_by_label("unit-price")).to_be_visible()
    # 수량 박스 확인
    expect(page.locator('[data-test="quantity"]')).to_be_visible()
    # 장바구니 버튼 확인
    expect(page.get_by_role("button", name="Add to cart")).to_be_visible()