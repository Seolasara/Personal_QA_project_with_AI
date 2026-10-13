"""상품 카탈로그 관련 Page Object.

- CatalogPage: 메인/상품 목록 + 카테고리 필터 + 헤더 장바구니 네비
- ProductDetailPage: 상품 상세 페이지
- CartPage: 체크아웃 1단계(장바구니) 목록
"""
from urllib.parse import urlparse

from playwright.sync_api import Page, Response, expect

HOME_URL = "https://practicesoftwaretesting.com"


def is_cart_fetch(response: Response) -> bool:
    """장바구니 조회 응답(GET /carts/{id})인지 본다."""
    parts = urlparse(response.url).path.strip("/").split("/")
    return response.request.method == "GET" and len(parts) == 2 and parts[0] == "carts"


def open_cart_and_wait_fetch(page: Page, nav_cart) -> None:
    """헤더 [cart]를 누르고 장바구니 조회 응답(GET /carts/{id})까지 기다린다.

    /checkout 은 지연 로드 모듈이라 모듈을 받은 뒤에야 장바구니를 조회해 행을 그린다. 사이트가 느리면
    클릭 뒤 5초 안에 조회가 시작되지 않아 행 대기가 먼저 끝난다(2026-10-13 trace 확인).
    담긴 상품이 있으면 비로그인, 상세·메인에서 이동, 로그아웃·재로그인 뒤 모두 조회가 나간다(2026-10-13 확인).
    빈 장바구니는 헤더 [cart]가 없어 이 함수를 쓰지 않는다.
    """
    with page.expect_response(is_cart_fetch):
        nav_cart.click()


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

    # --- 헤더 장바구니 배지 (UI_65, UI_66, UI_70). 장바구니가 비면 아이콘째 사라진다 (2026-10-11 확인) ---
    @property
    def cart_badge(self):
        return self.nav_cart.locator('[data-test="cart-quantity"]')

    def category_checkbox(self, name: str):
        # 카테고리 체크박스는 data-test 가 category-<id> 라 이름 기반이 안정적
        return self.page.get_by_role("checkbox", name=name)

    def filter_by_category(self, name: str) -> None:
        self.category_checkbox(name).check()

    def open_first_product(self) -> None:
        self.product_cards.first.click()

    def open_cart(self) -> None:
        self.nav_cart.click()

    def open_cart_loaded(self) -> None:
        """헤더 [cart]를 누르고 장바구니 조회 응답까지 기다린다. 빈 장바구니에는 쓰지 않는다."""
        open_cart_and_wait_fetch(self.page, self.nav_cart)

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

    # --- 상품 카드 구성, 페이지 번호 이동, 목록의 품절 카드 (UI_42, UI_43, UI_53) ---
    # 카드 이미지는 data-test 가 없어 카드 안의 img 태그를 쓴다 (2026-10-11 확인)

    @staticmethod
    def card_image(card):
        return card.locator("img")

    @staticmethod
    def card_name(card):
        return card.locator('[data-test="product-name"]')

    @staticmethod
    def card_price(card):
        return card.locator('[data-test="product-price"]')

    @staticmethod
    def card_out_of_stock(card):
        return card.locator('[data-test="out-of-stock"]')

    @staticmethod
    def image_natural_width(image) -> int:
        """이미지가 로드되면 원본 너비를 돌려준다. 로드 실패면 0. 카드 이미지는 lazy 로딩이라 먼저 화면으로 스크롤한다."""
        image.scroll_into_view_if_needed()
        return image.evaluate(
            """img => img.complete ? img.naturalWidth : new Promise(resolve => {
                img.addEventListener('load', () => resolve(img.naturalWidth), {once: true});
                img.addEventListener('error', () => resolve(0), {once: true});
            })"""
        )

    @property
    def pagination(self):
        return self.page.locator("ul.pagination")

    def page_number_button(self, number: int):
        # 페이지 번호 버튼은 data-test 가 없고 aria-label 이 "Page-<번호>" (2026-10-11 확인)
        return self.page.get_by_role("button", name=f"Page-{number}", exact=True)

    def go_to_page(self, number: int) -> None:
        self._apply_and_wait(self.page_number_button(number).click)

    def find_first_out_of_stock_card(self):
        """현재 목록부터 다음 페이지로 넘기며 첫 품절 상품 카드를 찾는다. 마지막 페이지까지 없으면 None."""
        while not self.out_of_stock_cards.count():
            if self._is_last_page():
                return None
            self._apply_and_wait(self.pagination_next.click)
        return self.out_of_stock_cards.first

    # --- 첫 상품 이미지 클릭, 검색 초기화·결과 없음, CO₂ 정렬, Eco-friendly, 가격 슬라이더 (UI_17, UI_44~UI_52) ---
    # 2026-10-11 확인: 2자 검색은 상품 목록 요청을 보내지 않고, [X]와 슬라이더 이동은 요청을 보낸다.

    def open_first_product_image(self) -> None:
        self.card_image(self.listed_links.first).click()

    @property
    def search_reset(self):
        return self.page.locator('[data-test="search-reset"]')

    @property
    def search_caption(self):
        return self.page.locator('[data-test="search-caption"]')

    @property
    def no_results(self):
        return self.page.locator('[data-test="no-results"]')

    def reset_search(self) -> None:
        self._apply_and_wait(self.search_reset.click)

    def record_product_list_requests(self) -> list[str]:
        """지금부터 나가는 상품 목록 요청 URL을 모으는 목록을 돌려준다 (검색 미실행 확인용)."""
        sent: list[str] = []

        def _record(request) -> None:
            if request.url.split("?")[0].endswith(("/products", "/products/search")):
                sent.append(request.url)

        self.page.on("request", _record)
        return sent

    def click_search(self) -> None:
        """응답을 기다리지 않고 [Search]만 누른다. 검색이 실행되지 않는 입력(2자)용."""
        self.search_submit.click()

    def selected_sort_label(self) -> str:
        return self.sort_select.evaluate("e => e.options[e.selectedIndex].text").strip()

    @property
    def co2_active_letters(self):
        # 카드 CO₂ 배지는 A~E 글자를 모두 그리고 해당 등급에만 active 클래스가 붙는다 (data-test 없음)
        return self.page.locator('[data-test="co2-rating-badge"] .co2-letter.active')

    def listed_co2_ratings(self) -> list[str]:
        return [letter.strip() for letter in self.co2_active_letters.all_inner_texts()]

    @property
    def eco_filter(self):
        return self.page.locator('[data-test="eco-friendly-filter"]')

    @property
    def eco_badges(self):
        return self.listed_links.locator('[data-test="eco-badge"]')

    @property
    def cards_without_eco_badge(self):
        return self.listed_links.filter(has_not=self.page.locator('[data-test="eco-badge"]'))

    def check_eco_friendly(self) -> None:
        self._apply_and_wait(self.eco_filter.check)

    def raise_min_price(self, presses: int) -> None:
        """가격 슬라이더 최소값 핸들을 키보드(PageUp)로 presses 번 올린다. 한 번에 한 응답씩 기다린다."""
        self.price_min_handle.focus()
        for _ in range(presses):
            self._apply_and_wait(lambda: self.price_min_handle.press("PageUp"))

    def move_max_price_to_end(self) -> None:
        """가격 슬라이더 최대값 핸들을 키보드(End)로 오른쪽 끝까지 옮긴다."""
        self.price_max_handle.focus()
        self._apply_and_wait(lambda: self.price_max_handle.press("End"))


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

    def open_cart_loaded(self) -> None:
        """헤더 [cart]를 누르고 장바구니 조회 응답까지 기다린다 (UI_25). 빈 장바구니에는 쓰지 않는다."""
        open_cart_and_wait_fetch(self.page, self.nav_cart)

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

    # --- 상세 이미지, Specifications, Related products, 즐겨찾기 (UI_54~UI_60, 2026-10-11 확인) ---
    @property
    def product_image(self):
        # 상세 이미지는 data-test 가 없고 alt 가 상품명이다
        return self.page.get_by_role("img", name=self.name.inner_text().strip(), exact=True)

    @property
    def specs_title(self):
        return self.page.locator('[data-test="specs-title"]')

    @property
    def specs_table(self):
        return self.page.locator('[data-test="product-specs"]')

    @property
    def spec_rows(self):
        return self.page.locator('[data-test="spec-row"]')

    @property
    def related_products_heading(self):
        return self.page.get_by_role("heading", name="Related products", exact=True)

    @property
    def related_product_titles(self):
        # 관련 상품 카드 제목은 data-test 가 없는 h5 이고, 상세 화면에서 h5 는 관련 상품 카드에만 있다
        return self.page.get_by_role("heading", level=5)

    @property
    def add_to_favorites(self):
        return self.page.locator('[data-test="add-to-favorites"]')

    @property
    def toast_message(self):
        return self.page.get_by_role("alert")

    def add_favorite(self) -> None:
        self.add_to_favorites.click()

    def type_quantity(self, text: str) -> None:
        """수량 입력란에 키보드로 한 글자씩 입력한다. 숫자 입력란이라 fill 은 문자를 거부한다."""
        self.quantity.press_sequentially(text)


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

    def open(self) -> None:
        """URL(/checkout)로 직접 진입하고 장바구니 조회 요청이 끝날 때까지 기다린다 (UI_37).

        빈 장바구니는 본문에 표시할 요소가 없어(2026-10-10 확인) 요소 대기 대신 네트워크 안정 시점을 쓴다.
        """
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

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

    # --- 표 컬럼, 행 [X], [Continue Shopping], 삭제 토스트 (UI_67, UI_68, UI_69) ---
    def column_header(self, name: str):
        # 표 머리글은 data-test 가 없어 역할 기반 (2026-10-11 확인)
        return self.page.get_by_role("columnheader", name=name, exact=True)

    def row_remove_button(self, title: str):
        return self.row(title).locator("a.btn.btn-danger")

    @property
    def continue_shopping(self):
        return self.page.locator('[data-test="continue-shopping"]')

    @property
    def deleted_toast(self):
        return self.page.get_by_label("Product deleted.")
