import pytest

from clients.login_client import LoginClient
from config import API_EMAIL, API_PASSWORD
from schemas.login import LoginErrorResponse, LoginResponse, UserResponse

# 시트의 요청 바디 값 중 계정 정보는 .env(API_EMAIL)에서 파생한다.
_LOCAL, _, _DOMAIN = API_EMAIL.partition("@")
WRONG_PASSWORD = "pass"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_01")
def test_invalid_email_without_domain(api_client):
    response = LoginClient(api_client).login_with_payload(
        {"email": _LOCAL, "password": API_PASSWORD}
    )

    assert response.status_code == 401
    assert LoginErrorResponse.model_validate(response.json()).error == "Unauthorized"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_02")
def test_invalid_email_with_incomplete_domain(api_client):
    response = LoginClient(api_client).login_with_payload(
        {"email": f"{_LOCAL}@{_DOMAIN.removesuffix('.com')}", "password": API_PASSWORD}
    )

    assert response.status_code == 401
    assert LoginErrorResponse.model_validate(response.json()).error == "Unauthorized"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_03")
def test_invalid_password(api_client):
    response = LoginClient(api_client).login(API_EMAIL, WRONG_PASSWORD)

    assert response.status_code == 401
    assert LoginErrorResponse.model_validate(response.json()).error == "Unauthorized"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_04")
def test_login_without_email(api_client):
    response = LoginClient(api_client).login_with_payload({"password": API_PASSWORD})

    assert response.status_code == 401
    assert LoginErrorResponse.model_validate(response.json()).error == "Invalid login request"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_05")
def test_login_without_password(api_client):
    response = LoginClient(api_client).login_with_payload({"email": API_EMAIL})

    assert response.status_code == 401
    assert LoginErrorResponse.model_validate(response.json()).error == "Invalid login request"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_06")
def test_login_with_empty_body(api_client):
    response = LoginClient(api_client).login_with_payload({})

    assert response.status_code == 401
    assert LoginErrorResponse.model_validate(response.json()).error == "Invalid login request"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_07")
def test_login_with_unregistered_email(api_client):
    response = LoginClient(api_client).login(f"nouser@{_DOMAIN}", API_PASSWORD)

    assert response.status_code == 401
    assert LoginErrorResponse.model_validate(response.json()).error == "Unauthorized"


@pytest.mark.tc("API_08")
@pytest.mark.issue("QA-14")  # 백로그 #20: token_type, expires_in이 스펙 예시와 다름. 고쳐질 때까지 실패로 집계
def test_login(api_client):
    response = LoginClient(api_client).login(API_EMAIL, API_PASSWORD)

    assert response.status_code == 200
    result = LoginResponse.model_validate(response.json())
    # 스펙 예시값 (QA-14)
    assert (result.token_type, result.expires_in) == ("Bearer", 120)


@pytest.mark.tc("API_09")
def test_login_response_field_types(api_client):
    response = LoginClient(api_client).login(API_EMAIL, API_PASSWORD)

    assert response.status_code == 200
    body = response.json()
    LoginResponse.model_validate(body, strict=True)


@pytest.mark.tc("API_10")
def test_get_user(authed_client):
    response = LoginClient(authed_client).get_user()

    assert response.status_code == 200
    user = UserResponse.model_validate(response.json())
    assert user.email == API_EMAIL
