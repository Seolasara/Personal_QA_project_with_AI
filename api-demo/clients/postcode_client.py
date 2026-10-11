import httpx

class PostcodeClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_postcode(self, country=None, postcode=None, house_number=None):
        params = {"country": country, "postcode": postcode, "house_number": house_number}
        params = {k: v for k, v in params.items() if v is not None}
        response = self.client.get("/postcode-lookup", params=params)
        return response
