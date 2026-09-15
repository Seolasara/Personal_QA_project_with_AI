"""테스트 계정 정보. 코드에 직접 쓰지 않고 `.env`(gitignore 대상)에서 읽는다.

최초 1회:  cp .env.example .env   (값 채우기)
CI에서는 .env 파일 대신 같은 이름의 환경변수를 시크릿으로 주입하면 된다
(이미 설정된 환경변수는 .env 값으로 덮어쓰지 않는다).
"""
import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(Path(__file__).parent / ".env")


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} 환경변수가 없습니다. playwright-demo/.env.example 을 "
            f".env 로 복사하고 값을 채우세요 (cp .env.example .env)."
        )
    return value


TOOLSHOP_EMAIL = _require("TOOLSHOP_EMAIL")
TOOLSHOP_PASSWORD = _require("TOOLSHOP_PASSWORD")
