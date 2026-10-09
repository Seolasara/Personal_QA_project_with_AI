# API 분석: Product

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Product |
| 목적 | 상품 목록(필터, 정렬, 페이지), 단건, 연관 상품, 검색을 조회합니다 |
| 사용처 | 상품 목록/검색 화면, Cart의 `product_id`, Invoice line |
| 스펙 근거 | `GET /products`, `GET /products/{productId}`, `GET /products/{productId}/related`, `GET /products/search` |

## 2. 핵심 흐름

1. `GET /products`로 페이지 단위 목록을 받습니다 (`PaginatedProductResponse`).
2. `by_brand`, `by_category`, `is_rental`, `between`, `sort`, `page`로 목록을 좁히거나 정렬합니다.
3. `GET /products/{productId}`로 단건을 확인합니다.
4. `GET /products/{productId}/related`로 연관 상품을 받습니다.
5. `GET /products/search?q=`로 검색합니다.
6. 얻은 `id`를 Cart의 `product_id`로 사용합니다.

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| GET | `/products` | 없음 | 쿼리 `by_brand`, `by_category`, `is_rental`, `between`(예: `price,10,30`), `sort`(예: `name,asc`, `price,desc`) 모두 string, `page`(integer) | 200 (`PaginatedProductResponse`), 404, 405 |
| GET | `/products/{productId}` | 없음 | 경로 `productId`(string) | 200 (`ProductResponse`), 404, 405 |
| GET | `/products/{productId}/related` | 없음 | 경로 `productId`(string) | 200 (`ProductResponse[]`), 404, 405 |
| GET | `/products/search` | 없음 | 쿼리 `q`(string, required), `page`(integer) | 200 (`PaginatedProductResponse`), 404, 405 |

스키마
- `PaginatedProductResponse`: `current_page`, `data`(ProductResponse[]), `from`, `last_page`, `per_page`, `to`, `total`
- `ProductResponse`: `id`, `name`, `description`, `price`, `is_location_offer`, `is_rental`, `in_stock`, `co2_rating`, `is_eco_friendly`, `brand`, `category`, `product_image`. `required` 지정이 없습니다.

## 4. 리스크

- R6 (중간): 중첩 `brand`/`category`가 스펙의 `BrandResponse`/`CategoryResponse`보다 축소된 필드로 내려옴
  - 근거: 백로그 #1. 스펙은 `$ref`로 전체 스키마를 가리키나 `required`가 없어 엄밀한 위반은 아님
  - 대응: 중첩 객체 검증은 `id`, `name`만 필수로 보고 나머지는 선택으로 처리 (api-demo는 축소 모델로 대응 중)
- R12 (낮음): 필터/정렬 파라미터가 모두 string이고 형식은 설명문에만 있음
  - 근거: `GET /products` 파라미터 `between`, `sort`, `is_rental`의 description. 잘못된 형식의 응답은 스펙에 없음
- R14 (낮음): `q` 누락 시 응답 코드 미정의
  - 근거: `GET /products/search`는 `q` required, 422 응답 없음
- R1 (높음): `Accept` 헤더 누락 시 404가 302로 나올 수 있음
  - 근거: 백로그 #4
- R13 (낮음): `productId` 형식 제한이 없음
  - 근거: `GET /products/{productId}` path가 `type: string`뿐

## 5. 테스트 범위 (포함)

- 목록 조회와 페이지네이션 필드, `page` 이동
- 필터(`by_brand`, `by_category`), 가격 범위(`between`), 정렬(`sort`)
- 단건, 연관 상품, 검색 조회와 응답 스키마
- 존재하지 않는 id의 404
- 제외: 쓰기(`POST`/`PUT`/`PATCH`/`DELETE`)와 `QUERY` 변형 (개요 4번), Product Spec 계열

## 6. TC 작성 입력값

공통: 헤더 `Accept: application/json`, 인증 불필요. 상품 id, brand id, category id는 실행 시 목록에서 취득합니다 (시딩값이 바뀔 수 있음).

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| P1 | `GET /products` | 없음 | 200, `data` 배열 | High |
| P2 | `GET /products` | 없음 | 200, `current_page`, `from`, `last_page`, `per_page`, `to`, `total` 존재, 타입은 integer | High |
| P3 | `GET /products` | `page`=2 | 200, `current_page`=2 | Medium |
| P4 | `GET /products` | `by_brand`=유효한 brand id | 200, `data` 항목의 brand id가 모두 일치 (중첩 brand에 `id` 있음) | High |
| P5 | `GET /products` | `by_category`=유효한 category id | 200, 결과가 해당 category 소속. 하위 카테고리 포함 여부는 확인 필요 | High |
| P6 | `GET /products` | `between`=`price,10,30` (스펙 예시) | 200, 각 `price`가 10 이상 30 이하. 경계 포함 여부는 확인 필요 | Medium |
| P7 | `GET /products` | `sort`=`price,asc` | 200, `price` 오름차순 | Medium |
| P8 | `GET /products` | `sort`=`name,desc` | 200, `name` 내림차순 | Medium |
| P9 | `GET /products/{productId}` | 유효한 id | 200, `ProductResponse` 필드 (`id`, `name`, `price` 등) | High |
| P10 | `GET /products/{productId}/related` | 유효한 id | 200, 배열 | Medium |
| P11 | `GET /products/search` | `q`=`hammer` (스펙 예시) | 200, `PaginatedProductResponse` 구조 | High |
| P12 | `GET /products/{productId}` | 유효한 id | 중첩 `brand`는 `id`, `name`, `category`는 `id`, `name`, `slug` 존재 (백로그 #1 대응, 나머지 필드는 선택) | Medium |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| P13 | `GET /products/{productId}` | 존재하지 않는 id | 404 | High |
| P14 | `GET /products/{productId}/related` | 존재하지 않는 id | 404 | Medium |
| P15 | `GET /products/search` | `q` 누락 | 확인 필요 | Low |
| P16 | `GET /products` | `between` 형식 오류 (예: `price,abc`) | 확인 필요 (스펙에 응답 없음) | Low |
