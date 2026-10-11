# API 분석: Cart

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Cart |
| 목적 | 인증 없이 장바구니를 만들고 상품 추가, 수량 변경, 상품 삭제, 장바구니 삭제를 합니다 |
| 사용처 | 결제 흐름의 시작점, Invoice 생성 시 `cart_id` |
| 스펙 근거 | `POST /carts`, `POST /carts/{id}`, `GET /carts/{cartId}`, `DELETE /carts/{cartId}`, `PUT /carts/{cartId}/product/quantity`, `DELETE /carts/{cartId}/product/{productId}` |

## 2. 핵심 흐름

1. `POST /carts`로 장바구니를 만들고 `id`를 받습니다 (201).
2. `POST /carts/{id}`로 `product_id`, `quantity`를 추가합니다 (200, `result` 문자열).
3. `PUT /carts/{cartId}/product/quantity`로 수량을 바꿉니다.
4. `GET /carts/{cartId}`로 내용을 확인합니다.
5. `DELETE /carts/{cartId}/product/{productId}`로 상품을 빼거나 `DELETE /carts/{cartId}`로 장바구니를 지웁니다 (204).

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| POST | `/carts` | 없음 | 없음 | 201 (`id`), 404, 405, 422 |
| POST | `/carts/{id}` | 없음 | 바디 `product_id`(string, required), `quantity`(integer, required) | 200 (`result`), 404, 405, 422 |
| GET | `/carts/{cartId}` | 없음 | 경로 `cartId` | 200 (`CartResponse`), 404, 405 |
| DELETE | `/carts/{cartId}` | 없음 | 경로 `cartId` | 204, 401, 404, 405, 409, 422 |
| PUT | `/carts/{cartId}/product/quantity` | 없음 | 바디 `product_id`(string, required), `quantity`(integer, required) | 200, 404, 405, 422 |
| DELETE | `/carts/{cartId}/product/{productId}` | 없음 | 경로 `cartId`, `productId` | 204, 401, 404, 405, 409, 422 |

스키마: `CartResponse`는 `id` 하나만 정의합니다. 스펙상 `DELETE` 두 개에는 `security`가 없는데 응답에 401이 있어 정의가 어긋납니다 (확인 필요).

## 4. 리스크

- R1 (높음): `Accept` 헤더 누락 시 검증 실패(422)와 미존재(404)가 302로 나옴
  - 근거: 백로그 #4. `POST /carts/{id}`에 잘못된 `product_id`를 보낼 때 헤더가 없으면 302, 있으면 스펙대로 422로 라이브 확인됨
- R7 (중간): 스펙 응답 코드와 소스가 다름 [불일치]
  - 근거: 스펙 `POST /carts/{id}`, `PUT .../quantity`는 200/404/405/422만 있으나 소스는 일반 예외에서 400도 반환
  - 판단: 스펙 기준으로 400은 "확인 필요"
- R8 (중간): `CartResponse`가 `id`만 정의한 반면 소스는 cartItems(과 product)를 포함해 반환 [불일치]
  - 근거: 스펙 `components/schemas/CartResponse`, 소스 `CartService::getCartById`
  - 대응: `extra="forbid"` 스키마면 contract 실패가 날 수 있음. 판단은 스펙 기준이고 상세 필드는 확인 필요
- R9 (중간): 상태 의존 리소스이고 수량 상한이 스펙에 없음
  - 근거: 스펙 `quantity`는 integer 예시 1뿐. 소스 검증은 1~99지만 스펙에 없어 TC 근거로 쓰지 않음 (경계값은 확인 필요)
  - 대응: 각 TC가 자기 장바구니를 만들고 `DELETE /carts/{cartId}`로 정리

## 5. 테스트 범위 (포함)

- 장바구니 생성, 상품 추가, 수량 변경, 조회, 상품/장바구니 삭제의 정상 흐름
- 필수값 누락과 존재하지 않는 `product_id`/`cart_id`에 대한 422/404
- 같은 상품 재추가 시 동작: 스펙 `result` 예시가 "item added or updated"여서 수량 갱신으로 해석되나 정확한 결과는 확인 필요
- 제외: 동시성, 대량 수량 경계 (스펙에 상한 없음)

## 6. TC 작성 입력값

공통: 헤더 `Accept: application/json`, 인증 불필요. `product_id`는 `GET /products`에서 취득합니다.

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| CA1 | `POST /carts` | 없음 | 201, 바디 `id`(string) | High |
| CA2 | `POST /carts/{id}` | CA1의 id, 유효한 `product_id`, `quantity`=1 | 200, `result` 문자열 | High |
| CA3 | `GET /carts/{cartId}` | CA2 이후 id | 200, 바디에 `id` 존재. 담긴 상품 구조는 확인 필요 | High |
| CA4 | `PUT /carts/{cartId}/product/quantity` | 담긴 상품, `quantity`=3 | 200. 변경 반영은 GET으로 확인, 필드 구조는 확인 필요 | High |
| CA5 | `DELETE /carts/{cartId}/product/{productId}` | 담긴 상품 | 204 | High |
| CA6 | `DELETE /carts/{cartId}` | 유효한 id | 204 | High |
| CA7 | `POST /carts/{id}` | 같은 상품을 2회 추가 | 200. 수량 합산/갱신 여부는 확인 필요 | Medium |
| CA8 | `POST /carts/{id}` | 서로 다른 상품 2개 | 각각 200 | Medium |
| CA9 | `GET /carts/{cartId}` | CA6 이후 같은 id | 404 (삭제 확인) | Medium |
| CA10 | `POST /carts` | 2회 호출 | 서로 다른 `id` | Low |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| CA11 | `POST /carts/{id}` | 존재하지 않는 `product_id` (헤더 포함) | 422 (스펙 정의, 백로그 #4에서 라이브 확인됨) | High |
| CA12 | `POST /carts/{id}` | `product_id` 누락 | 422 | High |
| CA13 | `POST /carts/{id}` | `quantity` 누락 | 422 | High |
| CA14 | `POST /carts/{id}` | `quantity`가 문자열 (예: `"abc"`) | 422 | Medium |
| CA15 | `POST /carts/{id}` | 존재하지 않는 cart id | 404 | High |
| CA16 | `GET /carts/{cartId}` | 존재하지 않는 id | 404 | High |
| CA17 | `PUT /carts/{cartId}/product/quantity` | 존재하지 않는 `product_id` | 422 | Medium |
| CA18 | `PUT /carts/{cartId}/product/quantity` | `quantity` 누락 | 422 | Medium |
| CA19 | `DELETE /carts/{cartId}` | 존재하지 않는 id | 404 | Medium |
| CA20 | `POST /carts/{id}` | `quantity`=0 또는 음수 | 확인 필요 (스펙에 하한 없음) | Low |
| CA21 | `DELETE /carts/{cartId}/product/{productId}` | 담기지 않은 `productId` | 확인 필요 (스펙은 404/409/422 정의, 구분 기준 없음) | Low |
