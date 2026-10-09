import httpx

class LoginClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def login(self, email, password):
        response = self.client.post("/users/login", json={"email":email, "password":password})
        return response

    def login_with_payload(self, payload: dict):
        response = self.client.post("/users/login", json=payload)
        return response

    def get_user(self):
        response = self.client.get("/users/me")
        return response