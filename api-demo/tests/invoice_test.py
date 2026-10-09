import pytest
from schemas.invoice import InvoiceCreatedResponse
from schemas.invoice import InvoiceResponse
from clients.invoice_client import InvoiceClient
from clients.cart_client import CartClient
from clients.base_client import get_client
from clients.logout_client import LogoutClient
from schemas.invoice import PaginatedInvoiceResponse

INVALID_TOKEN = "invalid.token.value"

CARD_DETAILS = {
    "credit_card_number": "1111-1111-1111-1111",
    "expiration_date": "12/2030",
    "cvv": "123",
    "card_holder_name": "John Doe",
}


@pytest.fixture
def existing_invoice_id(api_client, authed_client, cart_id, product_id, address_info):
    #기존 인보이스가 없는 계정이라 사전 조건용으로 1건 생성
    CartClient(api_client).add_item(cart_id, product_id, 1)
    return InvoiceClient(authed_client).create_invoice(address_info, "cash-on-delivery", {}, cart_id).json()["id"]


def assert_billing_matches(body, address_info):
    assert body["billing_street"] == address_info["street"]
    assert body["billing_city"] == address_info["city"]
    assert body["billing_state"] == address_info["state"]
    assert body["billing_country"] == address_info["country"]
    assert body["billing_postal_code"] == address_info["postcode"]


@pytest.mark.tc("API_99")
def test_create_invoice(api_client, authed_client, cart_id, product_id, address_info):
    #장바구니 생성 > 상품 추가
    CartClient(api_client).add_item(cart_id, product_id, 1)

    #인보이스 생성
    invoice_client = InvoiceClient(authed_client)
    response = invoice_client.create_invoice(address_info, "cash-on-delivery", {}, cart_id)
    body = response.json()

    InvoiceCreatedResponse.model_validate(body)
    assert_billing_matches(body, address_info)
    # 스펙과 다른 성공 코드(201)만 xfail (백로그 #12), 그 밖의 코드는 실패
    if response.status_code == 201:
        pytest.xfail("백로그 #12: 인보이스 생성 성공 코드가 스펙(200)과 다름. 실제 201")
    assert response.status_code == 200


@pytest.mark.tc("API_100")
def test_create_invoice_credit_card(api_client, authed_client, cart_id, product_id, address_info):
    CartClient(api_client).add_item(cart_id, product_id, 1)

    invoice_client = InvoiceClient(authed_client)
    response = invoice_client.create_invoice(address_info, "credit-card", CARD_DETAILS, cart_id)
    body = response.json()

    InvoiceCreatedResponse.model_validate(body)
    assert_billing_matches(body, address_info)
    # 스펙과 다른 성공 코드(201)만 xfail (백로그 #12), 그 밖의 코드는 실패
    if response.status_code == 201:
        pytest.xfail("백로그 #12: 인보이스 생성 성공 코드가 스펙(200)과 다름. 실제 201")
    assert response.status_code == 200


@pytest.mark.tc("API_101")
def test_get_invoice(api_client, authed_client, cart_id, product_id, address_info):
    #장바구니 생성 > 상품 추가
    CartClient(api_client).add_item(cart_id, product_id, 1)

    #인보이스 생성
    invoice_client = InvoiceClient(authed_client)
    invoice_id = invoice_client.create_invoice(address_info, "cash-on-delivery", {}, cart_id).json()["id"]

    #인보이스 조회
    response = invoice_client.get_invoice(invoice_id)
    body = response.json()

    assert response.status_code == 200
    InvoiceResponse.model_validate(body)
    assert body["id"] == invoice_id
    assert body["payment"]["payment_method"] == "cash-on-delivery"
    assert body["payment"]["payment_details"] == []


@pytest.mark.tc("API_102")
def test_get_invoice_matches_created(api_client, authed_client, cart_id, product_id, address_info):
    CartClient(api_client).add_item(cart_id, product_id, 1)

    invoice_client = InvoiceClient(authed_client)
    created = invoice_client.create_invoice(address_info, "cash-on-delivery", {}, cart_id).json()

    response = invoice_client.get_invoice(created["id"])
    body = response.json()

    assert response.status_code == 200
    InvoiceResponse.model_validate(body)
    assert body["id"] == created["id"]
    assert body["invoice_number"] == created["invoice_number"]
    assert body["total"] == created["total"]
    for key in ("billing_street", "billing_city", "billing_state", "billing_country", "billing_postal_code"):
        assert body[key] == created[key]


@pytest.mark.tc("API_103")
def test_invoice_lines_match_cart(api_client, authed_client, cart_id, product_id, address_info):
    CartClient(api_client).add_item(cart_id, product_id, 1)

    invoice_client = InvoiceClient(authed_client)
    invoice_id = invoice_client.create_invoice(address_info, "cash-on-delivery", {}, cart_id).json()["id"]

    response = invoice_client.get_invoice(invoice_id)
    body = response.json()

    assert response.status_code == 200
    InvoiceResponse.model_validate(body)
    lines = body["invoicelines"]
    assert len(lines) == 1
    assert lines[0]["invoice_id"] == invoice_id
    assert lines[0]["product_id"] == product_id
    assert lines[0]["quantity"] == 1


@pytest.mark.tc("API_104")
def test_create_invoice_without_auth(api_client, cart_id, product_id, address_info):
    CartClient(api_client).add_item(cart_id, product_id, 1)

    response = InvoiceClient(api_client).create_invoice(address_info, "cash-on-delivery", {}, cart_id)

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


@pytest.mark.tc("API_105")
def test_create_invoice_without_billing_street(api_client, authed_client, cart_id, product_id, address_info):
    CartClient(api_client).add_item(cart_id, product_id, 1)

    response = InvoiceClient(authed_client).create_invoice(
        address_info, "cash-on-delivery", {}, cart_id, omit=("billing_street",))

    assert response.status_code == 422
    assert response.json() == {"billing_street": ["The billing street field is required."]}


@pytest.mark.tc("API_106")
def test_create_invoice_without_cart_id(authed_client, address_info):
    response = InvoiceClient(authed_client).create_invoice(
        address_info, "cash-on-delivery", {}, None, omit=("cart_id",))

    assert response.status_code == 422
    assert response.json() == {"cart_id": ["The cart id field is required."]}


@pytest.mark.tc("API_107")
def test_create_invoice_invalid_payment_method(api_client, authed_client, cart_id, product_id, address_info):
    CartClient(api_client).add_item(cart_id, product_id, 1)

    response = InvoiceClient(authed_client).create_invoice(address_info, "bitcoin", {}, cart_id)

    assert response.status_code == 422
    assert response.json() == {"payment_method": ["The selected payment method is invalid."]}


@pytest.mark.tc("API_108")
def test_create_invoice_mismatched_city(api_client, authed_client, cart_id, product_id, address_info):
    CartClient(api_client).add_item(cart_id, product_id, 1)

    response = InvoiceClient(authed_client).create_invoice(
        address_info, "cash-on-delivery", {}, cart_id, billing_city="OtherCity")

    assert response.status_code == 422
    assert response.json() == {"billing_country": [
        "The billing_country does not match the entered address. The city does not belong to the selected country."]}


@pytest.mark.tc("API_109")
def test_get_invoice_without_auth(existing_invoice_id):
    response = InvoiceClient(get_client()).get_invoice(existing_invoice_id)

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


@pytest.mark.tc("API_110")
def test_get_invoice_with_malformed_token(authed_client, existing_invoice_id):
    response = InvoiceClient(authed_client).get_invoice_with_token(existing_invoice_id, INVALID_TOKEN)

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


@pytest.mark.tc("API_111")
def test_get_invoice_not_found(authed_client):
    response = InvoiceClient(authed_client).get_invoice("notfound")

    assert response.status_code == 404
    assert response.json() == {"message": "Requested item not found"}


@pytest.mark.tc("API_112")
def test_get_other_users_invoice(other_user_client, existing_invoice_id):
    # existing_invoice_id는 API 계정(customer3)이 만든 인보이스, 조회는 두 번째 계정으로 한다
    response = InvoiceClient(other_user_client).get_invoice(existing_invoice_id)

    assert response.status_code == 404
    assert response.json() == {"message": "Requested item not found"}


@pytest.mark.tc("API_113")
def test_list_invoices(authed_client, existing_invoice_id):
    response = InvoiceClient(authed_client).list_invoices()
    body = response.json()

    assert response.status_code == 200
    PaginatedInvoiceResponse.model_validate(body)
    assert body["current_page"] == 1


@pytest.mark.tc("API_114")
def test_list_invoices_page_field_types(authed_client, existing_invoice_id):
    response = InvoiceClient(authed_client).list_invoices()
    body = response.json()

    assert response.status_code == 200
    PaginatedInvoiceResponse.model_validate(body, strict=True)


@pytest.mark.tc("API_115")
def test_list_invoices_without_auth(api_client):
    response = InvoiceClient(api_client).list_invoices()

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


@pytest.mark.tc("API_116")
def test_list_invoices_with_logged_out_token(api_client, auth_token):
    api_client.headers["Authorization"] = f"Bearer {auth_token}"
    LogoutClient(api_client).logout()

    response = InvoiceClient(api_client).list_invoices()

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}
