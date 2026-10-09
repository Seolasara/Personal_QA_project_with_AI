import httpx

class ProductClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_all(self, params: dict | None = None):
        response = self.client.get("/products", params=params)
        return response

    def get_by_category(self, category_id: str):
        return self.get_all({"by_category": category_id})

    def get_by_brand(self, brand_id: str):
        return self.get_all({"by_brand": brand_id})

    def get_page(self, page: int):
        return self.get_all({"page": page})

    def get_sorted(self, sort: str):
        return self.get_all({"sort": sort})

    def get_between(self, between: str):
        return self.get_all({"between": between})

    def get_by_id(self, product_id: str):
        return self.client.get(f"/products/{product_id}")

    def get_related(self, product_id: str):
        return self.client.get(f"/products/{product_id}/related")

    def search(self, q: str):
        return self.client.get("/products/search", params={"q": q})
