import httpx

class UserClient:
    """관리자 토큰이 있는 클라이언트로 쓴다(사용자 검색, 수정)."""
    def __init__(self, client: httpx.Client):
        self.client = client

    def search(self, query):
        response = self.client.get("/users/search", params={"q": query})
        return response

    def patch(self, user_id, body: dict):
        response = self.client.patch(f"/users/{user_id}", json=body)
        return response
