"""헤더 [Categories] 메뉴로 들어가는 페이지의 Page Object.

- CategoryPage: 카테고리 페이지(/category/<slug>). 상품 목록 요소는 메인과 같아 CatalogPage 를 상속한다.
- RentalsPage: 렌탈 페이지(/rentals)
"""
from playwright.sync_api import Page, expect

from pages.catalog_page import CatalogPage


class CategoryPage(CatalogPage):
    """카테고리 페이지. 제목 "Category: <카테고리명>", 하위 카테고리·브랜드 필터, 정렬, 페이지 이동 (2026-10-11 확인)."""

    @property
    def nav_categories(self):
        return self.page.locator('[data-test="nav-categories"]')

    @property
    def nav_category_items(self):
        # 헤더 [Categories] 드롭다운 항목(Hand Tools, Power Tools, Other, Special Tools, Rentals)
        return self.page.get_by_label("nav-categories").get_by_role("link")

    def nav_category_item(self, name: str):
        return self.page.get_by_label("nav-categories").get_by_role("link", name=name, exact=True)

    @property
    def page_title(self):
        return self.page.locator('[data-test="page-title"]')

    @property
    def category_filters(self):
        # 카테고리 필터 체크박스. 상위 카테고리(ex: Hand Tools)와 하위 카테고리가 함께 나온다
        return self.page.locator('input[name="category_id"]')

    @property
    def category_filter_labels(self):
        return self.page.locator("label").filter(has=self.category_filters)

    @property
    def brand_filters(self):
        return self.page.locator('input[name="brand_id"]')

    @property
    def price_slider(self):
        # 메인의 Price Range 슬라이더(ngx-slider)
        return self.page.locator("ngx-slider")

    def open_categories_menu(self) -> None:
        self.nav_categories.click()

    def select_category(self, name: str) -> None:
        """열린 [Categories] 메뉴에서 카테고리를 고르고 상품 목록이 그려질 때까지 기다린다."""
        self._apply_and_wait(lambda: self.nav_category_item(name).click())

    def category_filter_names(self) -> list[str]:
        """카테고리 필터 라벨 이름. 필터는 상품 목록과 별도 응답(categories/tree)으로 그려져
        상품 목록 대기 뒤에도 비어 있을 수 있어, 첫 라벨이 보일 때까지 기다린 뒤 읽는다(2026-10-14 trace 확인)."""
        expect(self.category_filter_labels.first).to_be_visible()
        return [label.strip() for label in self.category_filter_labels.all_inner_texts()]


class RentalsPage:
    """렌탈 페이지. 제목 "Rentals"와 렌탈 상품 행(이미지, 이름, 설명) (2026-10-11 확인)."""

    def __init__(self, page: Page):
        self.page = page

        self.page_title = page.locator('[data-test="page-title"]')
        self.items = page.locator('[data-test^="product-"]')

    # 렌탈 상품 행의 이미지, 이름, 설명은 data-test 가 없어 태그와 Bootstrap 클래스 셀렉터 사용
    @staticmethod
    def item_image(item):
        return item.locator("img")

    @staticmethod
    def item_name(item):
        return item.locator(".card-title")

    @staticmethod
    def item_description(item):
        return item.locator(".card-text")

    image_natural_width = staticmethod(CatalogPage.image_natural_width)
