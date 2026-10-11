import pytest

from schemas.cart import CartCreatedResponse
from schemas.cart import CartMessageResponse
from schemas.cart import CartResponse
from schemas.cart import CartItemAddedResponse
from schemas.cart import UpdatedResponse
from schemas.cart import CartValidationError
from clients.cart_client import CartClient


@pytest.mark.tc("API_59")
def test_create_empty_cart(api_client, cart_cleanup):
    response = CartClient(api_client).create_cart({})
    body = response.json()
    cart_cleanup.append(body["id"])
    assert response.status_code == 201
    CartCreatedResponse.model_validate(body)


@pytest.mark.spec_undefined
@pytest.mark.tc("API_60")
def test_create_cart_without_body(api_client, cart_cleanup):
    response = CartClient(api_client).create_cart()
    body = response.json()
    cart_cleanup.append(body["id"])
    assert response.status_code == 201
    CartCreatedResponse.model_validate(body)


@pytest.mark.tc("API_61")
def test_create_cart_id_field_type(api_client, cart_cleanup):
    response = CartClient(api_client).create_cart({})
    body = response.json()
    cart_cleanup.append(body["id"])
    assert response.status_code == 201
    CartCreatedResponse.model_validate(body, strict=True)


@pytest.mark.tc("API_62")
def test_get_created_cart(api_client, cart_id):
    response = CartClient(api_client).get_cart(cart_id)
    body = CartResponse.model_validate(response.json())
    assert response.status_code == 200
    assert body.id == cart_id
    assert body.additional_discount_percentage is None
    assert body.lat is None
    assert body.lng is None
    assert body.cart_items == []


@pytest.mark.spec_undefined
@pytest.mark.tc("API_63")
def test_get_cart_after_add_item(api_client, cart_id, product_id):
    cart_client = CartClient(api_client)
    add = cart_client.add_item(cart_id, product_id, 1)
    assert add.status_code == 200

    response = cart_client.get_cart(cart_id)
    body = CartResponse.model_validate(response.json())
    assert response.status_code == 200
    assert body.id == cart_id
    assert body.additional_discount_percentage is None
    assert body.lat is None
    assert body.lng is None
    assert len(body.cart_items) == 1
    item = body.cart_items[0]
    assert item.quantity == 1
    assert item.discount_percentage is None
    assert item.cart_id == cart_id
    assert item.product_id == product_id


@pytest.mark.spec_undefined
@pytest.mark.tc("API_64")
def test_get_deleted_cart(api_client, cart_id):
    cart_client = CartClient(api_client)
    delete = cart_client.delete_cart(cart_id)
    assert delete.status_code == 204

    response = cart_client.get_cart(cart_id)
    body = CartMessageResponse.model_validate(response.json())
    assert response.status_code == 404
    assert body.message == "Requested item not found"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_65")
def test_get_cart_after_update_quantity(api_client, cart_id, product_id):
    cart_client = CartClient(api_client)
    add = cart_client.add_item(cart_id, product_id, 1)
    assert add.status_code == 200
    update = cart_client.update_quantity(cart_id, product_id, 3)
    assert update.status_code == 200

    response = cart_client.get_cart(cart_id)
    body = CartResponse.model_validate(response.json())
    assert response.status_code == 200
    assert body.id == cart_id
    assert len(body.cart_items) == 1
    assert body.cart_items[0].quantity == 3
    assert body.cart_items[0].product_id == product_id


@pytest.mark.tc("API_66")
def test_add_item(api_client, cart_id, product_id):
    response = CartClient(api_client).add_item(cart_id, product_id, 1)
    body = CartItemAddedResponse.model_validate(response.json())
    assert response.status_code == 200
    assert body.result == "item added or updated"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_67")
def test_add_same_item_twice(api_client, cart_id, product_id):
    cart_client = CartClient(api_client)
    first = cart_client.add_item(cart_id, product_id, 1)
    second = cart_client.add_item(cart_id, product_id, 1)
    assert first.status_code == 200
    assert second.status_code == 200
    assert CartItemAddedResponse.model_validate(first.json()).result == "item added or updated"
    assert CartItemAddedResponse.model_validate(second.json()).result == "item added or updated"

    cart = CartResponse.model_validate(cart_client.get_cart(cart_id).json())
    items = [i for i in cart.cart_items if i.product_id == product_id]
    assert len(items) == 1
    assert items[0].quantity == 2


@pytest.mark.tc("API_68")
def test_update_quantity(api_client, cart_id, product_id):
    response = CartClient(api_client).update_quantity(cart_id, product_id, 2)
    body = UpdatedResponse.model_validate(response.json())
    assert response.status_code == 200
    assert body.result == "item added or updated"


@pytest.mark.tc("API_69")
def test_update_quantity_invalid_product(api_client, cart_id):
    response = CartClient(api_client).update_quantity(cart_id, "notfound", 2)
    body = CartValidationError.model_validate(response.json())
    assert response.status_code == 422
    assert body.message == "The selected product id is invalid."
    assert body.errors == {"product_id": ["The selected product id is invalid."]}


@pytest.mark.tc("API_70")
def test_update_quantity_without_quantity(api_client, cart_id, product_id):
    response = CartClient(api_client).update_quantity_raw(cart_id, {"product_id": product_id})
    body = CartValidationError.model_validate(response.json())
    assert response.status_code == 422
    assert body.message == "The quantity field is required."
    assert body.errors == {"quantity": ["The quantity field is required."]}


@pytest.mark.tc("API_71")
def test_update_quantity_without_product_id(api_client, cart_id):
    response = CartClient(api_client).update_quantity_raw(cart_id, {"quantity": 2})
    body = CartValidationError.model_validate(response.json())
    assert response.status_code == 422
    assert body.message == "The product id field is required."
    assert body.errors == {"product_id": ["The product id field is required."]}


@pytest.mark.tc("API_72")
@pytest.mark.issue("QA-13")  # 백로그 #19: 404 메시지가 스펙과 다름. 고쳐질 때까지 실패로 집계
def test_update_quantity_nonexistent_cart(api_client, product_id):
    response = CartClient(api_client).update_quantity("notfound", product_id, 2)
    body = CartMessageResponse.model_validate(response.json())
    assert response.status_code == 404
    # 스펙 404 메시지 (QA-13)
    assert body.message == "Resource not found"


@pytest.mark.tc("API_73")
def test_delete_item(api_client, cart_id, product_id):
    cart_client = CartClient(api_client)
    add = cart_client.add_item(cart_id, product_id, 1)
    assert add.status_code == 200
    delete = cart_client.remove_item(cart_id, product_id)
    assert delete.status_code == 204
    assert delete.content == b""


@pytest.mark.spec_undefined
@pytest.mark.tc("API_74")
def test_delete_item_not_in_cart(api_client, cart_id, product_id):
    response = CartClient(api_client).remove_item(cart_id, product_id)
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.tc("API_75")
@pytest.mark.issue("QA-13")  # 백로그 #19: 404 메시지가 스펙과 다름. 고쳐질 때까지 실패로 집계
def test_delete_item_nonexistent_cart(api_client, product_id):
    response = CartClient(api_client).remove_item("notfound", product_id)
    body = CartMessageResponse.model_validate(response.json())
    assert response.status_code == 404
    # 스펙 404 메시지 (QA-13)
    assert body.message == "Resource not found"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_76")
def test_get_cart_after_delete_item(api_client, cart_id, product_id):
    cart_client = CartClient(api_client)
    add = cart_client.add_item(cart_id, product_id, 1)
    assert add.status_code == 200
    delete = cart_client.remove_item(cart_id, product_id)
    assert delete.status_code == 204
    assert delete.content == b""

    cart = CartResponse.model_validate(cart_client.get_cart(cart_id).json())
    assert cart.cart_items == []


@pytest.mark.tc("API_77")
def test_add_invalid_item(api_client, cart_id):
    response = CartClient(api_client).add_item(cart_id, "notfound", 1)
    body = CartValidationError.model_validate(response.json())
    assert response.status_code == 422
    assert body.message == "The selected product id is invalid."
    assert body.errors == {"product_id": ["The selected product id is invalid."]}


@pytest.mark.tc("API_78")
def test_add_item_without_product_id(api_client, cart_id):
    response = CartClient(api_client).add_item_raw(cart_id, {"quantity": 1})
    body = CartValidationError.model_validate(response.json())
    assert response.status_code == 422
    assert body.message == "The product id field is required."
    assert body.errors == {"product_id": ["The product id field is required."]}


@pytest.mark.tc("API_79")
def test_add_item_without_quantity(api_client, cart_id, product_id):
    response = CartClient(api_client).add_item_raw(cart_id, {"product_id": product_id})
    body = CartValidationError.model_validate(response.json())
    assert response.status_code == 422
    assert body.message == "The quantity field is required."
    assert body.errors == {"quantity": ["The quantity field is required."]}


@pytest.mark.tc("API_80")
def test_add_item_quantity_string(api_client, cart_id, product_id):
    response = CartClient(api_client).add_item(cart_id, product_id, "abc")
    body = CartValidationError.model_validate(response.json())
    assert response.status_code == 422
    assert body.message == "The quantity field must be an integer."
    assert body.errors == {"quantity": ["The quantity field must be an integer."]}


@pytest.mark.tc("API_81")
def test_delete_cart(api_client, cart_id):
    response = CartClient(api_client).delete_cart(cart_id)
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.tc("API_82")
@pytest.mark.issue("QA-13")  # 백로그 #19: 404 메시지가 스펙과 다름. 고쳐질 때까지 실패로 집계
def test_delete_nonexistent_cart(api_client):
    response = CartClient(api_client).delete_cart("notfound")
    body = CartMessageResponse.model_validate(response.json())
    assert response.status_code == 404
    # 스펙 404 메시지 (QA-13)
    assert body.message == "Resource not found"


@pytest.mark.tc("API_83")
def test_delete_cart_with_item(api_client, cart_id, product_id):
    cart_client = CartClient(api_client)
    add = cart_client.add_item(cart_id, product_id, 1)
    assert add.status_code == 200

    response = cart_client.delete_cart(cart_id)
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.tc("API_84")
def test_get_nonexistent_cart(api_client):
    response = CartClient(api_client).get_cart("notfound")
    body = CartMessageResponse.model_validate(response.json())
    assert response.status_code == 404
    assert body.message == "Requested item not found"


@pytest.mark.tc("API_85")
@pytest.mark.issue("QA-13")  # 백로그 #19: 404 메시지가 스펙과 다름. 고쳐질 때까지 실패로 집계
def test_add_item_nonexistent_cart(api_client, product_id):
    response = CartClient(api_client).add_item("notfound", product_id, 1)
    body = CartMessageResponse.model_validate(response.json())
    assert response.status_code == 404
    # 스펙 404 메시지 (QA-13)
    assert body.message == "Requested item not found"
