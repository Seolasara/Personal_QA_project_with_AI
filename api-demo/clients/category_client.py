import httpx

class CategoryClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_all(self):
        return self.client.get("/categories")

    def get_tree(self, by_category_slug: str | None = None):
        params = {} if by_category_slug is None else {"by_category_slug": by_category_slug}
        return self.client.get("/categories/tree", params=params)

    def get_tree_by_id(self, category_id: str):
        return self.client.get(f"/categories/tree/{category_id}")

    def search(self, q: str | None = None):
        params = {} if q is None else {"q": q}
        return self.client.get("/categories/search", params=params)
