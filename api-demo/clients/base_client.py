from config import API_BASE_URL
import httpx


def get_client() -> httpx.Client:
    client = httpx.Client(base_url=API_BASE_URL, headers={"Accept":"application/json"})
    return client