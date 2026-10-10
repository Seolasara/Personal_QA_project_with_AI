import pytest

from clients.brand_client import BrandClient
from clients.product_client import ProductClient
from schemas.product import (
    PaginatedProductResponse,
    PaginatedSearchProductResponse,
    ProductDetailResponse,
    ProductNotFoundResponse,
    ProductResponse,
    RelatedProductResponse,
)


@pytest.fixture
def category_id2(api_client):
    """{{category_id2}}: GET /products 첫 상품의 카테고리 id."""
    return ProductClient(api_client).get_all().json()["data"][0]["category"]["id"]


@pytest.mark.tc("API_40")
def test_get_products(api_client):
    response = ProductClient(api_client).get_all()
    body = response.json()

    assert response.status_code == 200
    products = PaginatedProductResponse.model_validate(body)
    assert products.current_page == 1
    assert products.from_ == 1
    assert products.per_page == 9
    assert products.to == 9


@pytest.mark.tc("API_41")
def test_get_products_by_category(api_client, category_id2):
    response = ProductClient(api_client).get_by_category(category_id2)
    body = response.json()

    assert response.status_code == 200
    products = PaginatedProductResponse.model_validate(body)
    assert products.current_page == 1
    assert {p.category.id for p in products.data} == {category_id2}


@pytest.mark.tc("API_42")
def test_products_page_info_field_types(api_client):
    response = ProductClient(api_client).get_all()
    body = response.json()

    assert response.status_code == 200
    PaginatedProductResponse.model_validate(body, strict=True)


@pytest.mark.tc("API_43")
def test_get_products_by_brand(api_client):
    brand_id = BrandClient(api_client).get_all().json()[0]["id"]

    response = ProductClient(api_client).get_by_brand(brand_id)
    body = response.json()

    assert response.status_code == 200
    products = PaginatedProductResponse.model_validate(body)
    assert products.current_page == 1
    assert products.data
    assert {p.brand.id for p in products.data} == {brand_id}


@pytest.mark.tc("API_44")
def test_get_products_page_2(api_client):
    response = ProductClient(api_client).get_page(2)
    body = response.json()

    assert response.status_code == 200
    products = PaginatedProductResponse.model_validate(body)
    assert products.current_page == 2


@pytest.mark.tc("API_45")
def test_get_products_sorted_by_price_asc(api_client):
    response = ProductClient(api_client).get_sorted("price,asc")
    body = response.json()

    assert response.status_code == 200
    products = PaginatedProductResponse.model_validate(body)
    prices = [p.price for p in products.data]
    assert products.current_page == 1
    assert prices == sorted(prices)


@pytest.mark.spec_undefined
@pytest.mark.tc("API_46")
def test_get_products_between_price(api_client):
    response = ProductClient(api_client).get_between("price,10,30")
    body = response.json()

    assert response.status_code == 200
    products = PaginatedProductResponse.model_validate(body)
    assert products.current_page == 1
    assert products.data
    assert all(10 <= p.price <= 30 for p in products.data)


@pytest.mark.tc("API_47")
def test_get_product_by_id(api_client, product_id):
    response = ProductClient(api_client).get_by_id(product_id)
    body = response.json()

    assert response.status_code == 200
    product = ProductDetailResponse.model_validate(body)
    assert product.id == product_id


@pytest.mark.tc("API_48")
def test_get_product_by_unknown_id(api_client):
    response = ProductClient(api_client).get_by_id("nonexistent-product-id")
    body = response.json()

    assert response.status_code == 404
    error = ProductNotFoundResponse.model_validate(body)
    assert error.message == "Requested item not found"


@pytest.mark.tc("API_49")
def test_product_nested_brand_and_category(api_client, product_id):
    response = ProductClient(api_client).get_by_id(product_id)
    body = response.json()

    assert response.status_code == 200
    product = ProductDetailResponse.model_validate(body)
    assert product.id == product_id
    assert set(body["brand"]) == {"id", "name"}
    assert set(body["category"]) == {"id", "name", "slug", "parent_id"}


@pytest.mark.tc("API_50")
def test_product_field_types(api_client, product_id):
    response = ProductClient(api_client).get_by_id(product_id)
    body = response.json()

    assert response.status_code == 200
    ProductDetailResponse.model_validate(body, strict=True)


@pytest.mark.tc("API_51")
def test_product_matches_list_item(api_client, product_id):
    list_item = ProductClient(api_client).get_all().json()["data"][0]

    response = ProductClient(api_client).get_by_id(product_id)
    body = response.json()

    assert response.status_code == 200
    product = ProductDetailResponse.model_validate(body)
    assert product.id == product_id
    assert (product.id, product.name, product.price) == (
        list_item["id"],
        list_item["name"],
        list_item["price"],
    )


@pytest.mark.tc("API_52")
def test_get_related_products(api_client, product_id):
    response = ProductClient(api_client).get_related(product_id)
    body = response.json()

    assert response.status_code == 200
    related = [RelatedProductResponse.model_validate(item) for item in body]
    assert related


@pytest.mark.tc("API_53")
@pytest.mark.xfail(
    strict=True,
    reason="백로그 #13: 존재하지 않는 상품의 연관 상품 조회가 스펙(404) 대신 500 Server Error",
)
def test_get_related_products_unknown_id(api_client):
    response = ProductClient(api_client).get_related("nonexistent-product-id")
    body = response.json()

    assert response.status_code == 404
    error = ProductNotFoundResponse.model_validate(body)
    assert error.message == "Requested item not found"


@pytest.mark.tc("API_54")
@pytest.mark.xfail(
    strict=True,
    reason="백로그 #18: 연관 상품 항목에 co2_rating이 없고 category에 slug가 없어 상품(ProductResponse) 구조와 다름",
)
def test_related_product_item_structure(api_client, product_id):
    response = ProductClient(api_client).get_related(product_id)
    body = response.json()

    assert response.status_code == 200
    assert body
    for item in body:
        ProductResponse.model_validate(item)


@pytest.mark.tc("API_55")
def test_search_products(api_client):
    response = ProductClient(api_client).search("Hammer")
    body = response.json()

    assert response.status_code == 200
    products = PaginatedSearchProductResponse.model_validate(body)
    assert products.current_page == 1
    assert all("hammer" in p.name.lower() for p in products.data)


@pytest.mark.tc("API_56")
def test_search_products_no_result(api_client):
    response = ProductClient(api_client).search("notfound")
    body = response.json()

    assert response.status_code == 200
    products = PaginatedSearchProductResponse.model_validate(body)
    assert products.current_page == 1
    assert products.data == []
    assert products.total == 0


@pytest.mark.spec_undefined
@pytest.mark.tc("API_57")
def test_search_products_lowercase(api_client):
    response = ProductClient(api_client).search("hammer")
    body = response.json()

    assert response.status_code == 200
    products = PaginatedSearchProductResponse.model_validate(body)
    assert products.current_page == 1
    assert all("hammer" in p.name.lower() for p in products.data)


@pytest.mark.tc("API_58")
def test_search_products_page_info_field_types(api_client):
    response = ProductClient(api_client).search("Hammer")
    body = response.json()

    assert response.status_code == 200
    PaginatedSearchProductResponse.model_validate(body, strict=True)
