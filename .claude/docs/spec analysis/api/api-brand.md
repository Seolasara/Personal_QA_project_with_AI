# API 분석: Brand

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Brand |
| 목적 | 상품 브랜드 목록, 단건, 검색을 조회합니다 |
| 사용처 | 상품 목록 필터(`by_brand`) |
| 스펙 근거 | `GET /brands`, `GET /brands/{brandId}`, `GET /brands/search` |

## 2. 핵심 흐름

1. `GET /brands`로 전체 브랜드를 받습니다.
2. `GET /brands/{brandId}`로 단건을 확인합니다.
3. `GET /brands/search?q=`로 이름 검색합니다.
4. 얻은 `id`를 Product 목록의 `by_brand`에 사용합니다.

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| GET | `/brands` | 없음 | 없음 | 200 (`BrandResponse[]`), 404, 405 |
| GET | `/brands/{brandId}` | 없음 | 경로 `brandId`(string) | 200 (`BrandResponse`), 404, 405 |
| GET | `/brands/search` | 없음 | 쿼리 `q`(string, required) | 200 (`BrandResponse[]`), 404, 405 |

스키마: `BrandResponse`는 `id`, `name`, `slug`이고 `required` 지정이 없습니다.

## 4. 리스크

- R1 (높음): `Accept` 헤더 누락 시 404가 302로 나올 수 있음
  - 근거: 백로그 #4, 존재하지 않는 `brandId` 404 TC에 해당
- R6 (중간): Product 안의 `brand`는 `slug` 없이 `id`, `name`만 내려와 `BrandResponse`와 다름
  - 근거: 백로그 #1. Brand 단독 응답과 Product 중첩 응답을 같은 스키마로 검증하면 안 됨
- R13 (낮음): `brandId` 형식 제한이 없어 형식 오류 id의 응답이 불명
  - 근거: `GET /brands/{brandId}` path가 `type: string`뿐
- R14 (낮음): `q` 누락 시 응답 코드 미정의
  - 근거: `GET /brands/search`는 `q` required, 422 응답 없음

## 5. 테스트 범위 (포함)

- 목록/단건/검색 조회 성공과 응답 스키마
- 존재하지 않는 id의 404, `q` 누락 네거티브
- 제외: 쓰기(`POST`/`PUT`/`PATCH`/`DELETE`)와 `QUERY` 변형 (개요 4번)

## 6. TC 작성 입력값

공통: 헤더 `Accept: application/json`, 인증 불필요.

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| B1 | `GET /brands` | 없음 | 200, 배열, 각 항목 `id`, `name`, `slug` | High |
| B2 | `GET /brands/{brandId}` | B1에서 얻은 유효한 id | 200, 해당 id의 `BrandResponse` | High |
| B3 | `GET /brands/search` | `q`=목록에 있는 이름의 일부 (스펙 예시 `Forge`) | 200, 배열. 매칭 규칙은 확인 필요 | High |
| B4 | `GET /brands` | 없음 | 응답 타입 검증: 필드가 string | Medium |
| B5 | `GET /brands/{brandId}` | B1 항목 | 목록 항목과 단건 응답의 `id`, `name`, `slug`가 일치 | Medium |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| B6 | `GET /brands/{brandId}` | 존재하지 않는 id | 404 | High |
| B7 | `GET /brands/search` | `q` 누락 | 확인 필요 | Medium |
| B8 | `GET /brands/search` | 매칭되지 않는 `q` | 200 빈 배열인지 404인지 확인 필요 | Low |
| B9 | `GET /brands/{brandId}` | 형식이 잘못된 id | 404 또는 다른 코드, 확인 필요 | Low |
| B10 | `GET /brands/search` | `q` 빈 문자열 | 확인 필요 | Low |
