import httpx

class PaymentClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def payment_methods(self, payment_method=None, payment_details=None):
        """None인 항목은 요청 바디에서 생략한다."""
        body = {}
        if payment_method is not None:
            body["payment_method"] = payment_method
        if payment_details is not None:
            body["payment_details"] = payment_details
        return self.client.post("/payment/check", json=body)
