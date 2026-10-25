#!/usr/bin/env python3
"""로컬 Toolshop에 운영에서 만들 수 없는 테스트 조건 데이터를 만든다. 로컬 DB에만 쓴다.

사용:  python3 local/seed_data.py out-of-stock --category hammer --count 2
       (되돌리기는 local/reset.sh)
조건
  out-of-stock: 카테고리 목록 기본 순서의 앞 N개 상품을 품절(stock 0)로 만든다.
    ex: 운영에서 Hammer 첫 상품들이 품절된 상황(2026-10-17)을 재현해 "재고 있는 첫 상품" fixture를 확인한다.
상품 수정 API는 stock 을 받지 않아(검증 규칙에 없음, 2026-10-17 확인) DB를 직접 고친다.
"""
import argparse, json, subprocess, sys, urllib.request

API_URL = "http://localhost:8091"
API_CONTAINER = "pst-laravel-api-1"
DB_CONTAINER = "pst-mariadb-1"


def get(path):
    with urllib.request.urlopen(API_URL + path, timeout=10) as r:
        return json.load(r)


def require_local():
    names = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True).stdout.split()
    if API_CONTAINER not in names or DB_CONTAINER not in names:
        sys.exit("로컬 Toolshop 컨테이너가 없습니다. 이 스크립트는 로컬에서만 동작합니다.")


def sql(statement):
    subprocess.run(["docker", "exec", DB_CONTAINER, "sh", "-c", f'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" toolshop -e "{statement}"'],
                   check=True, capture_output=True)


def clear_cache():
    subprocess.run(["docker", "exec", API_CONTAINER, "php", "artisan", "cache:clear"], check=True, capture_output=True)


def out_of_stock(category, count):
    def find(nodes):
        for n in nodes:
            if n["slug"] == category:
                return n
            hit = find(n.get("sub_categories") or [])
            if hit:
                return hit
    node = find(get("/categories/tree"))
    if not node:
        sys.exit(f"카테고리 slug 없음: {category}")
    ids = [node["id"]] + [s["id"] for s in node.get("sub_categories") or []]
    products = get(f"/products?by_category={','.join(ids)}")["data"][:count]
    for p in products:
        if not all(c.isalnum() for c in p["id"]):
            sys.exit(f"예상하지 못한 상품 ID: {p['id']}")
        sql(f"UPDATE products SET stock = 0 WHERE id = '{p['id']}'")
        print(f"품절 처리: {p['name']}")
    clear_cache()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("out-of-stock")
    o.add_argument("--category", required=True, help="카테고리 slug (ex: hammer)")
    o.add_argument("--count", type=int, default=1)
    args = ap.parse_args()
    require_local()
    if args.cmd == "out-of-stock":
        out_of_stock(args.category, args.count)


if __name__ == "__main__":
    main()
