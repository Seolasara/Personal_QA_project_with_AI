"""상품 카탈로그 관련 Page Object.

- CatalogPage: 메인/상품 목록 + 카테고리 필터 + 헤더 장바구니 네비
- ProductDetailPage: 상품 상세 페이지
- CartPage: 체크아웃 1단계(장바구니) 목록
"""
from playwright.sync_api import Page

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
