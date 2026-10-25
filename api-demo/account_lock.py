"""테스트 계정 잠금(423) 해제. 백로그 #8의 방법(관리자 `PATCH /users/{id}`로 `failed_login_attempts: 0`)을 코드로 둔다.

- 데모 사이트 공개 계정이라 외부 사용으로도 잠길 수 있다(2026-10-25 야간 실행 6건 실패). 잠금은 env이고 서비스 결함이 아니다.
- 실행 전 점검(`conftest.py`의 `pytest_sessionstart`)과 로그인 준비 코드(`login_or_unlock`)에서만 쓴다.
  잠금 동작 자체를 확인하는 TC는 이 함수를 쓰지 않는다(실패를 숨기지 않도록).
- 해제할 때마다 `UNLOCKS`에 남기고, report.json의 `account_unlocks`와 Slack 요약에 횟수로 보인다. 계정 값은 남기지 않는다.
"""
import httpx

from clients.base_client import get_client
from clients.login_client import LoginClient
from clients.user_client import UserClient
from config import ADMIN_EMAIL, ADMIN_PASSWORD

MAX_LOGIN_ATTEMPTS = 3  # 서비스 UserService.php 기준, 스펙 v5 User Login AC4(3회 실패 후 423)
UNLOCKS: list[dict] = []  # {"account": "API_EMAIL", "stage": "실행 전 점검" | "테스트 중", "where": nodeid}


def _admin() -> httpx.Client | None:
    if not (ADMIN_EMAIL and ADMIN_PASSWORD):
        return None
    client = get_client()
    login = LoginClient(client).login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if login.status_code != 200:
        client.close()
        return None
    client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
    return client


def _find_user(admin: httpx.Client, email: str) -> dict | None:
    response = UserClient(admin).search(email)
    if response.status_code != 200:
        return None
    return next((u for u in response.json().get("data", []) if u.get("email") == email), None)


def unlock_if_locked(email: str, account: str, stage: str, where: str = "") -> bool:
    """잠겨 있으면 풀고 True. 관리자 계정이 없거나 잠겨 있지 않으면 False."""
    admin = _admin()
    if admin is None:
        return False
    try:
        user = _find_user(admin, email)
        if not user or (user.get("failed_login_attempts") or 0) < MAX_LOGIN_ATTEMPTS:
            return False
        response = UserClient(admin).patch(user["id"], {"failed_login_attempts": 0})
        if response.status_code != 200:
            return False
        UNLOCKS.append({"account": account, "stage": stage, "where": where})
        return True
    finally:
        admin.close()


def login_or_unlock(client: httpx.Client, email: str, password: str, account: str, where: str = "") -> httpx.Response:
    """로그인하고, 423이면 관리자 계정으로 풀어 한 번만 다시 로그인한다."""
    response = LoginClient(client).login(email, password)
    if response.status_code == 423 and unlock_if_locked(email, account, "테스트 중", where):
        response = LoginClient(client).login(email, password)
    return response
