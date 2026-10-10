import pytest

from clients.logout_client import LogoutClient
from schemas.logout import LogoutErrorResponse, LogoutResponse

INVALID_TOKEN = "invalid.token.value"


@pytest.mark.tc("API_11")
def test_logout(authed_client):
    response = LogoutClient(authed_client).logout()

    assert response.status_code == 200
    assert LogoutResponse.model_validate(response.json()).message == "Successfully logged out"


@pytest.mark.tc("API_12")
def test_logout_without_token(api_client):
    response = LogoutClient(api_client).logout()

    assert response.status_code == 401
    assert LogoutErrorResponse.model_validate(response.json()).message == "Unauthorized"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_13")
def test_logout_with_malformed_token(api_client):
    response = LogoutClient(api_client).logout_with_token(INVALID_TOKEN)

    assert response.status_code == 401
    assert LogoutErrorResponse.model_validate(response.json()).message == "Unauthorized"


@pytest.mark.spec_undefined
@pytest.mark.tc("API_14")
def test_logout_again_with_logged_out_token(authed_client):
    logout_client = LogoutClient(authed_client)
    first = logout_client.logout()
    assert first.status_code == 200

    response = logout_client.logout()

    assert response.status_code == 401
    assert LogoutErrorResponse.model_validate(response.json()).message == "Unauthorized"
