"""상품 카탈로그 관련 Page Object.

- CatalogPage: 메인/상품 목록 + 카테고리 필터 + 헤더 장바구니 네비
- ProductDetailPage: 상품 상세 페이지
- CartPage: 체크아웃 1단계(장바구니) 목록
"""
from playwright.sync_api import Page, Response, expect

HOME_URL = "https://practicesoftwaretesting.com"


class CatalogPage:
    def __init__(self, page: Page):
        self.page = page

        # 상품 목록 (로딩 완료 상태 컨테이너)
        self.product_grid = page.locator('[data-test="filter_completed"]')
        self.product_cards = self.product_grid.locator('[data-test^="product-"]')

        # 헤더
        self.nav_cart = page.locator('[data-test="nav-cart"]')

    def open(self) -> None:
        self.page.goto(HOME_URL)

    def category_checkbox(self, name: str):
        # 카테고리 체크박스는 data-test 가 category-<id> 라 이름 기반이 안정적
        return self.page.get_by_role("checkbox", name=name)

    def filter_by_category(self, name: str) -> None:
        self.category_checkbox(name).check()

    def open_first_product(self) -> None:
        self.product_cards.first.click()

    def open_cart(self) -> None:
        self.nav_cart.click()

    # --- 상품 조회 필터·정렬·검색 (UI_10, UI_11, UI_12, UI_15) ---
    # 아래 메서드는 상품 목록 API 응답을 기다린 뒤, 그리드의 상품명이 그 응답과 같아질 때까지
    # 대기한다. 첫 로드에는 filter_completed 표시가 없고, 슬라이더 이동 후에는 이전 정렬의
    # sorting_completed 가 남아 있어 완료 표시만으로는 갱신 시점을 알 수 없다(2026-10-10 확인).

    @property
    def listed_names(self):
        return self.page.locator('[data-test="product-name"]')

    @property
    def listed_prices(self):
        return self.page.locator('[data-test="product-price"]')

    @property
    def listed_links(self):
        return self.page.locator('a[data-test^="product-"]')

    @property
    def brand_labels(self):
        return self.page.locator("label").filter(
            has=self.page.locator('input[name="brand_id"]')
        )

    @property
    def sort_select(self):
        return self.page.locator('[data-test="sort"]')

    @property
    def price_min_handle(self):
        return self.page.get_by_role("slider", name="ngx-slider", exact=True)

    @property
    def price_max_handle(self):
        return self.page.get_by_role("slider", name="ngx-slider-max", exact=True)

    @property
    def price_min_label(self):
        # ngx-slider 값 라벨은 data-test 가 없어 라이브러리 클래스 셀렉터 사용
        return self.page.locator("ngx-slider .ngx-slider-model-value")

    @property
    def price_max_label(self):
        return self.page.locator("ngx-slider .ngx-slider-model-high")

    @property
    def search_query(self):
        return self.page.locator('[data-test="search-query"]')

    @property
    def search_submit(self):
        return self.page.locator('[data-test="search-submit"]')

    def brand_checkbox(self, name: str):
        return self.page.get_by_role("checkbox", name=name)

    @staticmethod
    def _is_product_list_response(response: Response) -> bool:
        url = response.url.split("?")[0]
        return url.endswith(("/products", "/products/search")) and response.request.method in (
            "GET",
            "QUERY",
        )

    def _apply_and_wait(self, action) -> None:
        """action 이 일으킨 상품 목록 응답을 기다리고, 그리드가 그 응답대로 그려질 때까지 대기한다."""
        with self.page.expect_response(self._is_product_list_response) as info:
            action()
        names = [item["name"] for item in info.value.json()["data"]]
        expect(self.listed_names).to_have_text(names)

    def open_loaded(self) -> None:
        self._apply_and_wait(self.open)

    def check_category(self, name: str) -> None:
        self._apply_and_wait(lambda: self.category_checkbox(name).check())

    def first_brand_name(self) -> str:
        return self.brand_labels.first.inner_text().strip()

    def check_brand(self, name: str) -> None:
        self._apply_and_wait(lambda: self.brand_checkbox(name).check())

    def sort_by(self, label: str) -> None:
        self._apply_and_wait(lambda: self.sort_select.select_option(label=label))

    def lower_max_price(self, presses: int) -> None:
        """가격 슬라이더 최대값 핸들을 키보드(PageDown)로 presses 번 내린다. 한 번에 한 응답씩 기다린다."""
        self.price_max_handle.focus()
        for _ in range(presses):
            self._apply_and_wait(lambda: self.price_max_handle.press("PageDown"))

    def fill_search(self, term: str) -> None:
        self.search_query.fill(term)

    def submit_search(self) -> None:
        self._apply_and_wait(self.search_submit.click)

    def listed_product_names(self) -> list[str]:
        return [name.strip() for name in self.listed_names.all_inner_texts()]

    def listed_product_prices(self) -> list[float]:
        return [to_amount(price) for price in self.listed_prices.all_inner_texts()]

    def listed_product_urls(self) -> list[str]:
        return [HOME_URL + href for href in self.listed_links.evaluate_all(
            "els => els.map(e => e.getAttribute('href'))"
        )]

    # --- 품절 상품 찾기 (UI_23) ---
    # 목록 카드의 품절 표시는 상세와 같은 data-test="out-of-stock" (2026-10-10 확인)

    @property
    def out_of_stock_cards(self):
        return self.listed_links.filter(has=self.page.locator('[data-test="out-of-stock"]'))

    @property
    def pagination_next(self):
        return self.page.locator('[data-test="pagination-next"]')

    def _is_last_page(self) -> bool:
        # 마지막 페이지에서는 버튼이 아니라 감싼 li 에만 disabled 클래스가 붙는다 (2026-10-10 확인)
        next_item = self.page.locator("li.page-item").filter(has=self.pagination_next)
        return "disabled" in (next_item.get_attribute("class") or "")

    def collect_all_product_names(self) -> list[str]:
        """현재 목록부터 마지막 페이지까지 넘기며 상품명을 모은다. 페이지가 하나면 페이지네이션이 없다."""
        names = self.listed_product_names()
        while self.pagination_next.count() and not self._is_last_page():
            self._apply_and_wait(self.pagination_next.click)
            names += self.listed_product_names()
        return names

    def open_first_out_of_stock_product(self) -> bool:
        """현재 목록부터 다음 페이지로 넘기며 첫 품절 상품 카드를 찾아 상세로 이동한다.

        반환값: 품절 상품을 찾아 이동했으면 True, 마지막 페이지까지 없으면 False.
        """
        while not self.out_of_stock_cards.count():
            if self._is_last_page():
                return False
            self._apply_and_wait(self.pagination_next.click)
        self.out_of_stock_cards.first.click()
        return True


class ProductDetailPage:
    def __init__(self, page: Page):
        self.page = page

        self.name = page.locator('[data-test="product-name"]')
        self.description = page.locator('[data-test="product-description"]')
        self.unit_price = page.locator('[data-test="unit-price"]')
        self.quantity = page.locator('[data-test="quantity"]')
        self.increase_quantity = page.locator('[data-test="increase-quantity"]')
        self.decrease_quantity = page.locator('[data-test="decrease-quantity"]')
        self.add_to_cart = page.locator('[data-test="add-to-cart"]')
        self.added_toast = page.get_by_label("Product added to shopping cart.")

        self.nav_cart = page.locator('[data-test="nav-cart"]')

    def add(self) -> None:
        self.add_to_cart.click()

    def set_quantity(self, value: str) -> None:
        """수량 입력란에 값을 입력하고 입력란 밖(상품명)을 클릭한다."""
        self.quantity.fill(value)
        self.name.click()

    def increase(self) -> None:
        self.increase_quantity.click()

    def decrease(self) -> None:
        self.decrease_quantity.click()

    def open_cart(self) -> None:
        self.nav_cart.click()

    # --- 상세의 카테고리, 브랜드 배지 (UI_10). data-test 가 없어 aria-label 사용 ---
    @property
    def category_badge(self):
        return self.page.get_by_label("category", exact=True)

    @property
    def brand_badge(self):
        return self.page.get_by_label("brand", exact=True)

    def open(self, url: str) -> None:
        self.page.goto(url)

    # --- 품절 표시 (UI_23) ---
    @property
    def out_of_stock_label(self):
        return self.page.locator('[data-test="out-of-stock"]')

    def out_of_stock_color(self) -> tuple[int, int, int]:
        """품절 문구의 계산된 글자색을 (R, G, B)로 돌려준다."""
        color = self.out_of_stock_label.evaluate("e => getComputedStyle(e).color")
        red, green, blue = (int(part) for part in color[color.index("(") + 1:color.index(")")].split(",")[:3])
        return red, green, blue


def to_amount(text: str) -> float:
    """"$13.41" 형식의 금액 텍스트를 숫자로 바꾼다."""
    return float(text.strip().replace("$", "").replace(",", ""))


class CartPage:
    """체크아웃 위저드 1단계. URL: /checkout"""

    URL = "https://practicesoftwaretesting.com/checkout"

    def __init__(self, page: Page):
        self.page = page

        self.rows = page.locator('tr:has([data-test="product-title"])')
        self.product_titles = page.locator('[data-test="product-title"]')
        self.quantities = page.locator('[data-test="product-quantity"]')
        self.unit_prices = page.locator('[data-test="product-price"]')
        self.line_prices = page.locator('[data-test="line-price"]')
        self.cart_total = page.locator('[data-test="cart-total"]')
        self.quantity_updated_toast = page.get_by_label("Product quantity updated.")
        self.empty_message = page.get_by_text("Your shopping cart is empty")
        # 장바구니 행 삭제 버튼: 앱에 data-test 가 없어 클래스 셀렉터 사용 (기술부채)
        self.remove_buttons = page.locator("a.btn.btn-danger")

    def row(self, title: str):
        """상품명으로 장바구니 행을 찾는다."""
        return self.rows.filter(
            has=self.page.locator('[data-test="product-title"]', has_text=title)
        )

    def row_quantity(self, title: str):
        return self.row(title).locator('[data-test="product-quantity"]')

    def row_unit_price(self, title: str):
        return self.row(title).locator('[data-test="product-price"]')

    def row_line_price(self, title: str):
        return self.row(title).locator('[data-test="line-price"]')

    def set_row_quantity(self, title: str, value: str) -> None:
        """행 수량 입력란에 값을 입력하고 포커스를 옮겨 변경을 반영한다."""
        quantity = self.row_quantity(title)
        quantity.fill(value)
        quantity.press("Tab")

    def remove_item(self, title: str) -> None:
        self.row(title).locator("a.btn.btn-danger").click()

    def remove_first_item(self) -> None:
        if self.remove_buttons.count():
            self.remove_buttons.first.click()
