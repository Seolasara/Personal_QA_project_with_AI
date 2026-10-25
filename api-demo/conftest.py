import pytest

from account_lock import UNLOCKS, login_or_unlock, unlock_if_locked
from config import ADMIN_EMAIL, ADMIN_PASSWORD, API_EMAIL, API_EMAIL2, API_PASSWORD, API_PASSWORD2
from clients.base_client import get_client
from clients.cart_client import CartClient
from clients.login_client import LoginClient
from clients.postcode_client import PostcodeClient
from clients.product_client import ProductClient


# 실행 전 점검: 테스트 계정이 잠겨 있으면 관리자 계정으로 풀고 시작한다(백로그 #8). 해제 기록은 report.json과 Slack 요약에 남는다
def pytest_sessionstart(session):
    for email, account in ((API_EMAIL, "API_EMAIL"), (API_EMAIL2, "API_EMAIL2")):
        if email:
            unlock_if_locked(email, account, "실행 전 점검")


def pytest_json_modifyreport(json_report):
    json_report["account_unlocks"] = UNLOCKS


def pytest_terminal_summary(terminalreporter):
    if UNLOCKS:
        terminalreporter.write_line(f"계정 잠금 해제 {len(UNLOCKS)}회: " + ", ".join(
            f"{u['account']}({u['stage']}{' ' + u['where'] if u['where'] else ''})" for u in UNLOCKS))


@pytest.fixture
def api_client():
    client = get_client()
    yield client
    client.close()


@pytest.fixture
def auth_token(api_client, request):
    login = login_or_unlock(api_client, API_EMAIL, API_PASSWORD, "API_EMAIL", request.node.nodeid)
    token = login.json()["access_token"]
    return token


@pytest.fixture
def authed_client(api_client, auth_token):
    api_client.headers["Authorization"] = f"Bearer {auth_token}"
    return api_client


@pytest.fixture
def other_user_client(request):
    """두 번째 고객 계정 클라이언트. 다른 사용자 데이터에 접근하는지 검증할 때 쓴다."""
    if not (API_EMAIL2 and API_PASSWORD2):
        raise RuntimeError("API_EMAIL2/API_PASSWORD2가 없습니다. api-demo/.env에 값을 채우세요.")
    client = get_client()
    token = login_or_unlock(client, API_EMAIL2, API_PASSWORD2, "API_EMAIL2", request.node.nodeid).json()["access_token"]
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
