import httpx

class LogoutClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def logout(self):
        response = self.client.get("/users/logout")
        return response

    def logout_with_token(self, token: str):
        response = self.client.get(
            "/users/logout", headers={"Authorization": f"Bearer {token}"}
        )
        return response
