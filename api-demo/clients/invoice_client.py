import httpx

class InvoiceClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def create_invoice(self, address, payment_method, payment_details, cart_id, omit=(), **overrides):
        payload = {
            "billing_street": address["street"],
            "billing_city": address["city"],
            "billing_state": address["state"],
            "billing_country": address["country"],
            "billing_postal_code": address["postcode"],
            "payment_method": payment_method,
            "payment_details": payment_details,
            "cart_id": cart_id,
        }
        payload.update(overrides)
        for key in omit:
            payload.pop(key, None)
        response = self.client.post("/invoices", json=payload)
        return response

    def get_invoice(self, invoice_id):
        response = self.client.get(f"/invoices/{invoice_id}")
        return response

    def get_invoice_with_token(self, invoice_id, token):
        response = self.client.get(
            f"/invoices/{invoice_id}", headers={"Authorization": f"Bearer {token}"})
        return response

    def list_invoices(self):
        response = self.client.get("/invoices")
        return response
