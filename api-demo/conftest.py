import pytest

from config import ADMIN_EMAIL, ADMIN_PASSWORD, API_EMAIL, API_EMAIL2, API_PASSWORD, API_PASSWORD2
from clients.base_client import get_client
from clients.cart_client import CartClient
from clients.login_client import LoginClient
from clients.postcode_client import PostcodeClient
from clients.product_client import ProductClient


@pytest.fixture
def api_client():
    client = get_client()
    yield client
    client.close()


@pytest.fixture
def auth_token(api_client):
    login_client = LoginClient(api_client)
    login = login_client.login(API_EMAIL, API_PASSWORD)
    token = login.json()["access_token"]
    return token


@pytest.fixture
def authed_client(api_client, auth_token):
    api_client.headers["Authorization"] = f"Bearer {auth_token}"
    return api_client


@pytest.fixture
def other_user_client():
    """두 번째 고객 계정 클라이언트. 다른 사용자 데이터에 접근하는지 검증할 때 쓴다."""
    if not (API_EMAIL2 and API_PASSWORD2):
        raise RuntimeError("API_EMAIL2/API_PASSWORD2가 없습니다. api-demo/.env에 값을 채우세요.")
    client = get_client()
    token = LoginClient(client).login(API_EMAIL2, API_PASSWORD2).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
    client.close()


@pytest.fixture
def admin_client():
    """관리자 작업(계정 잠금 해제 등)용 클라이언트. api_client와 헤더를 섞지 않도록 따로 만든다."""
    if not (ADMIN_EMAIL and ADMIN_PASSWORD):
        raise RuntimeError("ADMIN_EMAIL/ADMIN_PASSWORD가 없습니다. api-demo/.env에 값을 채우세요.")
    client = get_client()
    token = LoginClient(client).login(ADMIN_EMAIL, ADMIN_PASSWORD).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
    client.close()


# cart id 픽스처: 테스트가 끝나면 장바구니를 지운다 (테스트가 이미 지웠으면 404라 무시)
@pytest.fixture
def cart_id(api_client):
    cart_client = CartClient(api_client)
    response = cart_client.create_cart()
    cartId = response.json()["id"]
    yield cartId
    cart_client.delete_cart(cartId)


@pytest.fixture
def cart_cleanup(api_client):
    """테스트 안에서 직접 만든 장바구니 id를 append하면 끝날 때 지운다."""
    created = []
    yield created
    cart_client = CartClient(api_client)
    for cart in created:
        cart_client.delete_cart(cart)


# product id 픽스처
@pytest.fixture
def product_id(api_client):
    product_client = ProductClient(api_client)
    product_res = product_client.get_all()
    productId = product_res.json()["data"][0]["id"]
    return productId


@pytest.fixture
def address_info(api_client):
    postcode_client = PostcodeClient(api_client)
    postal_code = postcode_client.get_postcode("korea", "12345")
    response = postal_code.json()
    return response
