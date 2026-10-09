import pytest

from clients.brand_client import BrandClient
from schemas.brand import BrandNotFoundResponse, BrandsResponse

FORGE_NAME = "ForgeFlex Tools"
FORGE_SLUG = "forgeflex-tools"


@pytest.fixture
def forge_brand(api_client):
    """{{brand_id}}: GET /brands 에서 ForgeFlex Tools 항목을 가져온다."""
    brands = BrandClient(api_client).get_all().json()
    return next(b for b in brands if b["name"] == FORGE_NAME)


@pytest.mark.tc("API_15")
def test_get_brands(api_client):
    response = BrandClient(api_client).get_all()
    body = response.json()

    assert response.status_code == 200
    brands = [BrandsResponse.model_validate(b) for b in body]
    assert {b.name: b.slug for b in brands}[FORGE_NAME] == FORGE_SLUG


@pytest.mark.tc("API_16")
def test_brands_item_field_types(api_client):
    response = BrandClient(api_client).get_all()
    body = response.json()

    assert response.status_code == 200
    assert body
    for item in body:
        BrandsResponse.model_validate(item, strict=True)


@pytest.mark.tc("API_17")
def test_get_brand_by_id(api_client, forge_brand):
    response = BrandClient(api_client).get_by_id(forge_brand["id"])
    brand = BrandsResponse.model_validate(response.json())

    assert response.status_code == 200
    assert brand.id == forge_brand["id"]
    assert brand.name == FORGE_NAME
    assert brand.slug == FORGE_SLUG


@pytest.mark.tc("API_18")
def test_get_brand_by_unknown_id(api_client):
    response = BrandClient(api_client).get_by_id("nonexistent-brand-id")
    body = BrandNotFoundResponse.model_validate(response.json())

    assert response.status_code == 404
    assert body.message == "Requested item not found"


@pytest.mark.tc("API_19")
def test_brand_detail_matches_list_item(api_client):
    brand_client = BrandClient(api_client)
    list_item = brand_client.get_all().json()[0]

    response = brand_client.get_by_id(list_item["id"])

    assert response.status_code == 200
    assert response.json() == list_item


@pytest.mark.tc("API_20")
def test_search_brand_by_keyword(api_client, forge_brand):
    response = BrandClient(api_client).search("Forge")
    body = response.json()

    assert response.status_code == 200
    assert [BrandsResponse.model_validate(b).model_dump() for b in body] == [forge_brand]


@pytest.mark.tc("API_21")
def test_search_brand_no_result(api_client):
    response = BrandClient(api_client).search("not found")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.tc("API_22")
def test_search_brand_without_q(api_client):
    response = BrandClient(api_client).search()
    body = response.json()

    assert response.status_code == 200
    assert body
    for item in body:
        BrandsResponse.model_validate(item)


@pytest.mark.tc("API_23")
def test_search_brand_lowercase_keyword(api_client, forge_brand):
    response = BrandClient(api_client).search("forge")
    body = response.json()

    assert response.status_code == 200
    assert [BrandsResponse.model_validate(b).model_dump() for b in body] == [forge_brand]
