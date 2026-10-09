import pytest
from schemas.postcode import PostcodeResponse, PostcodeValidationError
from clients.postcode_client import PostcodeClient

COUNTRY = "GERMANY"
POSTCODE = "10115"


@pytest.mark.tc("API_86")
def test_find_postcode(api_client):
    postcode_client = PostcodeClient(api_client)
    response = postcode_client.get_postcode(COUNTRY, POSTCODE)

    assert response.status_code == 200
    result = PostcodeResponse.model_validate(response.json())
    assert result.country == COUNTRY
    assert result.postcode == POSTCODE


@pytest.mark.tc("API_87")
def test_find_postcode_with_house_number(api_client):
    postcode_client = PostcodeClient(api_client)
    response = postcode_client.get_postcode(COUNTRY, POSTCODE, "5")

    assert response.status_code == 200
    result = PostcodeResponse.model_validate(response.json())
    assert result.house_number == "5"
    assert result.country == COUNTRY
    assert result.postcode == POSTCODE


@pytest.mark.tc("API_88")
def test_postcode_response_field_types(api_client):
    postcode_client = PostcodeClient(api_client)
    response = postcode_client.get_postcode(COUNTRY, POSTCODE)

    assert response.status_code == 200
    body = response.json()
    PostcodeResponse.model_validate(body, strict=True)


@pytest.mark.tc("API_89")
def test_postcode_without_country(api_client):
    postcode_client = PostcodeClient(api_client)
    response = postcode_client.get_postcode(postcode=POSTCODE)

    assert response.status_code == 422
    assert response.json() == {"message": "Resource not found"}


@pytest.mark.tc("API_90")
def test_postcode_without_postcode(api_client):
    postcode_client = PostcodeClient(api_client)
    response = postcode_client.get_postcode(country=COUNTRY)

    assert response.status_code == 422
    result = PostcodeValidationError.model_validate(response.json())
    msg = "The postcode field is required."
    assert result.message == msg
    assert result.errors == {"postcode": [msg]}


@pytest.mark.tc("API_91")
def test_postcode_country_too_long(api_client):
    postcode_client = PostcodeClient(api_client)
    response = postcode_client.get_postcode("a" * 41, POSTCODE)

    assert response.status_code == 422
    result = PostcodeValidationError.model_validate(response.json())
    msg = "The country field must not be greater than 40 characters."
    assert result.message == msg
    assert result.errors == {"country": [msg]}


@pytest.mark.tc("API_92")
def test_postcode_postcode_too_long(api_client):
    postcode_client = PostcodeClient(api_client)
    response = postcode_client.get_postcode(COUNTRY, "1" * 11)

    assert response.status_code == 422
    result = PostcodeValidationError.model_validate(response.json())
    msg = "The postcode field must not be greater than 10 characters."
    assert result.message == msg
    assert result.errors == {"postcode": [msg]}
