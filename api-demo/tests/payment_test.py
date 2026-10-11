from schemas.payment import PaymentResponse, PaymentValidationError
from clients.payment_client import PaymentClient
import pytest

SPEC_SUCCESS_MESSAGE = "Success status"  # 스펙 예시값


@pytest.mark.tc("API_93")
@pytest.mark.issue("QA-8")  # 백로그 #2: 결제 성공 메시지가 스펙 예시와 다름. 고쳐질 때까지 실패로 집계
def test_cash_payment(api_client):
    payment_client = PaymentClient(api_client)
    response = payment_client.payment_methods("cash-on-delivery")
    body = response.json()

    assert response.status_code == 200
    result = PaymentResponse.model_validate(body)
    # 스펙 예시값 (QA-8)
    assert result.message == SPEC_SUCCESS_MESSAGE


@pytest.mark.tc("API_94")
@pytest.mark.issue("QA-8")  # 백로그 #2: 결제 성공 메시지가 스펙 예시와 다름. 고쳐질 때까지 실패로 집계
def test_credit_card_payment(api_client):
    payment_client = PaymentClient(api_client)
    response = payment_client.payment_methods("credit-card", {"credit_card_number":"1111-1111-1111-1111", "expiration_date":"12/2030", "cvv":"123", "card_holder_name": "John Doe"})
    body = response.json()

    assert response.status_code == 200
    result = PaymentResponse.model_validate(body)
    # 스펙 예시값 (QA-8)
    assert result.message == SPEC_SUCCESS_MESSAGE


@pytest.mark.tc("API_95")
@pytest.mark.issue("QA-8")  # 백로그 #2: 결제 성공 메시지가 스펙 예시와 다름. 고쳐질 때까지 실패로 집계
def test_transfer_payment(api_client):
    payment_client = PaymentClient(api_client)
    response = payment_client.payment_methods("bank-transfer", {"bank_name":"Test Bank", "account_name":"John Doe", "account_number":"123456789"})
    body = response.json()

    assert response.status_code == 200
    result = PaymentResponse.model_validate(body)
    # 스펙 예시값 (QA-8)
    assert result.message == SPEC_SUCCESS_MESSAGE


@pytest.mark.spec_undefined
@pytest.mark.tc("API_96")
def test_payment_method_missing(api_client):
    payment_client = PaymentClient(api_client)
    response = payment_client.payment_methods(payment_details={})
    body = response.json()

    assert response.status_code == 200
    result = PaymentResponse.model_validate(body)
    # 스펙 예시값과 다른 부분만 xfail (백로그 #2)
    if result.message != SPEC_SUCCESS_MESSAGE:
        pytest.xfail(f"백로그 #2: 결제 메시지가 스펙(\"{SPEC_SUCCESS_MESSAGE}\")과 다름. 실제 \"{result.message}\"")


@pytest.mark.spec_undefined
@pytest.mark.tc("API_97")
def test_payment_method_not_in_enum(api_client):
    payment_client = PaymentClient(api_client)
    response = payment_client.payment_methods("bitcoin", {})
    body = response.json()

    assert response.status_code == 200
    result = PaymentResponse.model_validate(body)
    # 스펙 예시값과 다른 부분만 xfail (백로그 #2)
    if result.message != SPEC_SUCCESS_MESSAGE:
        pytest.xfail(f"백로그 #2: 결제 메시지가 스펙(\"{SPEC_SUCCESS_MESSAGE}\")과 다름. 실제 \"{result.message}\"")


@pytest.mark.spec_undefined
@pytest.mark.tc("API_98")
def test_credit_card_number_missing(api_client):
    payment_client = PaymentClient(api_client)
    response = payment_client.payment_methods("credit-card", {"expiration_date":"12/2030", "cvv":"123", "card_holder_name": "John Doe"})
    body = response.json()

    assert response.status_code == 422
    result = PaymentValidationError.model_validate(body)
    msg = "The payment details.credit card number field is required."
    assert result.message == msg
    assert result.errors == {"payment_details.credit_card_number": [msg]}
