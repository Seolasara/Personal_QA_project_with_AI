import pytest

from clients.category_client import CategoryClient
from schemas.category import (
    CategoryNotFoundResponse,
    CategoryResponse,
    CategoryTreeResponse,
)

POWER_TOOLS_NAME = "Power Tools"


@pytest.fixture
def power_tools(api_client):
    """{{slug_id}}, {{categories_id}}: GET /categories/tree 에서 Power Tools 항목을 가져온다."""
    tree = CategoryClient(api_client).get_tree().json()
    return next(c for c in tree if c["name"] == POWER_TOOLS_NAME)


@pytest.fixture
def sub_category(api_client, power_tools):
    """{{category_id}}: Power Tools 필터 조회(API_28)의 하위 카테고리 첫 항목."""
    response = CategoryClient(api_client).get_tree(power_tools["slug"])
    return response.json()[0]["sub_categories"][0]


@pytest.mark.tc("API_24")
def test_get_categories(api_client):
    response = CategoryClient(api_client).get_all()
    body = response.json()

    assert response.status_code == 200
    assert body
    for item in body:
        CategoryResponse.model_validate(item)


@pytest.mark.tc("API_25")
def test_categories_item_field_types(api_client):
    response = CategoryClient(api_client).get_all()
    body = response.json()

    assert response.status_code == 200
    assert body
    for item in body:
        CategoryResponse.model_validate(item, strict=True)


@pytest.mark.tc("API_26")
def test_categories_parent_id_types(api_client):
    response = CategoryClient(api_client).get_all()
    categories = [CategoryResponse.model_validate(c) for c in response.json()]
    by_name = {c.name: c for c in categories}

    assert response.status_code == 200
    assert by_name["Hand Tools"].slug == "hand-tools"
    assert by_name["Hand Tools"].parent_id is None
    assert by_name["Hammer"].slug == "hammer"
    assert by_name["Hammer"].parent_id is not None
    assert any(c.parent_id is None for c in categories)


@pytest.mark.tc("API_27")
def test_get_category_tree(api_client):
    response = CategoryClient(api_client).get_tree()
    body = response.json()
    tree = [CategoryTreeResponse.model_validate(c) for c in body]
    power_tools = next(c for c in tree if c.name == POWER_TOOLS_NAME)

    assert response.status_code == 200
    assert power_tools.parent_id is None


@pytest.mark.tc("API_28")
def test_get_category_tree_by_slug(api_client, power_tools):
    response = CategoryClient(api_client).get_tree(power_tools["slug"])
    body = [CategoryTreeResponse.model_validate(c) for c in response.json()]

    assert response.status_code == 200
    assert len(body) == 1
    top = body[0]
    assert top.id == power_tools["id"]
    assert top.name == POWER_TOOLS_NAME
    assert top.slug == power_tools["slug"]
    assert top.parent_id is None
    assert top.sub_categories
    for sub in top.sub_categories:
        assert sub.parent_id == power_tools["id"]


@pytest.mark.tc("API_29")
def test_category_tree_top_level_structure(api_client):
    response = CategoryClient(api_client).get_tree()
    tree = [CategoryTreeResponse.model_validate(c) for c in response.json()]

    assert response.status_code == 200
    assert [c.name for c in tree[:3]] == ["Hand Tools", POWER_TOOLS_NAME, "Other"]
    assert tree[0].slug == "hand-tools"
    for item in tree:
        assert item.parent_id is None


@pytest.mark.tc("API_30")
def test_get_category_tree_by_example_slug(api_client):
    response = CategoryClient(api_client).get_tree("hand-tools")
    body = [CategoryTreeResponse.model_validate(c) for c in response.json()]

    assert response.status_code == 200
    assert len(body) == 1
    top = body[0]
    assert top.name == "Hand Tools"
    assert top.slug == "hand-tools"
    assert top.parent_id is None
    assert top.sub_categories
    for sub in top.sub_categories:
        assert sub.parent_id == top.id


@pytest.mark.tc("API_31")
def test_get_category_by_id(api_client, power_tools, sub_category):
    response = CategoryClient(api_client).get_tree_by_id(sub_category["id"])
    body = CategoryTreeResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.id == sub_category["id"]
    assert body.name == "Grinder"
    assert body.slug == "grinder"
    assert body.parent_id == power_tools["id"]
    assert body.sub_categories == []


@pytest.mark.tc("API_32")
def test_get_parent_category_with_sub_categories(api_client, power_tools):
    response = CategoryClient(api_client).get_tree_by_id(power_tools["id"])
    body = CategoryTreeResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.id == power_tools["id"]
    assert body.name == POWER_TOOLS_NAME
    assert body.slug == power_tools["slug"]
    assert body.parent_id is None
    assert body.sub_categories
    for sub in body.sub_categories:
        assert sub.parent_id == power_tools["id"]


@pytest.mark.tc("API_33")
def test_get_category_by_unknown_id(api_client):
    response = CategoryClient(api_client).get_tree_by_id("nonexistent-category-id")
    body = CategoryNotFoundResponse.model_validate(response.json())

    assert response.status_code == 404
    assert body.message == "Requested item not found"


@pytest.mark.tc("API_34")
def test_category_matches_tree_item(api_client):
    client = CategoryClient(api_client)
    tree = [CategoryTreeResponse.model_validate(c) for c in client.get_tree().json()]
    hand_tools = next(c for c in tree if c.name == "Hand Tools")

    response = client.get_tree_by_id(hand_tools.id)
    body = CategoryTreeResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.id == hand_tools.id
    assert body.name == "Hand Tools"
    assert body.slug == "hand-tools"
    assert body.parent_id is None
    assert body == hand_tools


@pytest.mark.tc("API_35")
def test_search_categories_by_keyword(api_client):
    response = CategoryClient(api_client).search("Hammer")
    body = [CategoryTreeResponse.model_validate(c) for c in response.json()]

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0].name == "Hammer"
    assert body[0].slug == "hammer"
    assert body[0].parent_id is not None
    assert body[0].sub_categories == []


@pytest.mark.tc("API_36")
def test_search_categories_no_result(api_client):
    response = CategoryClient(api_client).search("notfound")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.spec_undefined
@pytest.mark.tc("API_37")
def test_search_categories_without_q(api_client):
    response = CategoryClient(api_client).search()
    body = [CategoryTreeResponse.model_validate(c) for c in response.json()]

    assert response.status_code == 200
    assert body[0].name == "Hand Tools"
    assert body[0].slug == "hand-tools"
    assert body[0].parent_id is None
    assert body[0].sub_categories


@pytest.mark.spec_undefined
@pytest.mark.tc("API_38")
def test_search_categories_lowercase_keyword(api_client):
    response = CategoryClient(api_client).search("hammer")
    body = [CategoryTreeResponse.model_validate(c) for c in response.json()]

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0].name == "Hammer"
    assert body[0].slug == "hammer"
    assert body[0].parent_id is not None
    assert body[0].sub_categories == []


@pytest.mark.spec_undefined
@pytest.mark.tc("API_39")
def test_search_categories_partial_match(api_client):
    response = CategoryClient(api_client).search("tools")
    body = [CategoryTreeResponse.model_validate(c) for c in response.json()]

    assert response.status_code == 200
    assert [(c.name, c.slug) for c in body] == [
        ("Hand Tools", "hand-tools"),
        ("Power Tools", "power-tools"),
    ]
    for item in body:
        assert item.parent_id is None
        assert item.sub_categories
