#!/usr/bin/env bash
# 로컬 Toolshop(sprint5, docker compose)을 시드 데이터로 초기화한다. 운영 사이트와 무관하다.
# DB 초기화 → API 캐시 비우기(옛 ID가 캐시에 남는 문제) → php-fpm 재적재(opcache) → 응답 확인
set -euo pipefail
API=pst-laravel-api-1
docker ps --format '{{.Names}}' | grep -qx "$API" || { echo "로컬 Toolshop 컨테이너($API)가 없습니다. 서비스 레포에서 docker compose up 을 먼저 하세요."; exit 1; }
docker exec "$API" php artisan migrate:fresh --seed --force >/dev/null
docker exec "$API" php artisan cache:clear >/dev/null
docker exec "$API" kill -USR2 1
for url in http://localhost:8091/status http://localhost:4200; do
  for _ in $(seq 1 30); do [ "$(curl -s -o /dev/null -w '%{http_code}' "$url")" = 200 ] && break; sleep 1; done
  echo "$url $(curl -s -o /dev/null -w '%{http_code}' "$url")"
done
echo "초기화 완료"
