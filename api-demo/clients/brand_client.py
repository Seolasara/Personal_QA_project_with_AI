import httpx

class BrandClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_all(self):
        response = self.client.get("/brands")
        return response

    def get_by_id(self, brand_id: str):
        return self.client.get(f"/brands/{brand_id}")

    def search(self, q: str | None = None):
        params = {} if q is None else {"q": q}
        return self.client.get("/brands/search", params=params)
