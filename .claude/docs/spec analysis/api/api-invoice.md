# API 분석: Invoice

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Invoice |
| 목적 | 로그인 사용자가 Cart를 결제해 인보이스를 만들고 목록/단건을 조회합니다 |
| 사용처 | 결제 완료 단계, 주문 내역 |
| 스펙 근거 | `GET /invoices`, `POST /invoices`, `GET /invoices/{invoiceId}` (모두 `apiAuth` 필요) |

## 2. 핵심 흐름

1. 로그인해서 토큰을 받습니다 ([api-auth.md](api-auth.md)).
2. Cart를 만들고 상품을 담습니다 ([api-cart.md](api-cart.md)).
3. 필요하면 `GET /postcode-lookup`으로 주소를 얻습니다 ([api-postcode.md](api-postcode.md)).
4. `POST /invoices`에 `billing_*`, `payment_method`, `payment_details`, `cart_id`를 보냅니다.
5. 응답의 `InvoiceResponse`(`id`, `invoice_number`, `total`, `status`, `invoicelines` 등)를 확인합니다.
6. `GET /invoices`, `GET /invoices/{invoiceId}`로 조회합니다.

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| GET | `/invoices` | 필요 | 쿼리 `page`(integer) | 200 (`PaginatedInvoiceResponse`), 401, 404, 405 |
| POST | `/invoices` | 필요 | 바디 required: `billing_street`, `billing_city`, `billing_state`, `billing_country`, `billing_postal_code`, `payment_method`(enum), `payment_details`, `cart_id` | 200 (`InvoiceResponse`), 401, 404, 405, 422 |
| GET | `/invoices/{invoiceId}` | 필요 | 경로 `invoiceId`(string) | 200 (`InvoiceResponse`), 401, 404, 405 |

`InvoiceResponse` 주요 필드: `id`, `user_id`, `invoice_date`, `invoice_number`, `billing_*`, `additional_discount_percentage`, `additional_discount_amount`, `subtotal`, `total`, `status`, `status_message`, `invoicelines`, `created_at`

## 4. 리스크

- R2 (높음): `billing_street`/`city`/`state`/`country`가 postcode-lookup 응답값과 일치해야 하고, 임의의 실주소는 "The billing_country does not match the entered address" 422
  - 근거: 백로그 #3 (TC API_40 Note). 스펙의 `InvoiceRequest`에는 이 제약이 없고 `billing_*`는 단순 string
  - 판단: 일치 제약은 스펙에 없어 정상 케이스의 전제 조건으로 쓰되, 기대 코드는 스펙의 422 정의까지만 근거로 사용
- R5 (높음): 인증/권한 범위가 불명확함
  - 근거: 스펙은 세 엔드포인트에 `apiAuth`와 401만 정의. 다른 사용자의 `invoiceId` 접근 시 코드(403/404 등)는 스펙에 없어 확인 필요
- R7 (중간): `POST /invoices` 성공 코드가 스펙과 소스에서 다름 [불일치]
  - 근거: 스펙 응답은 200, 소스 `InvoiceController::store`는 201 (HTTP_CREATED)
  - 판단: 스펙 기준 200이나, 배포본의 실제 코드는 확인 필요. TC-Writer가 라이브 결과와 대조할 때 스펙 기준 실패인지 스펙 문서 오류인지 triage 필요
- R3 (높음): `payment_details`가 서버에서 검증되지 않을 수 있음
  - 근거: 백로그 #2, `InvoiceRequest.payment_details`가 `oneOf` 구조
- R6 (중간): `invoicelines[].product`가 `ProductResponse`로 정의되어 중첩 brand/category가 축소 필드일 수 있음
  - 근거: 백로그 #1, `InvoiceLineResponse.product`
- R1 (높음): `Accept` 헤더 누락 시 422/404가 302로 나옴
  - 근거: 백로그 #4

## 5. 테스트 범위 (포함)

- `POST /invoices` 정상 생성과 응답 스키마, 결제 수단 변형
- 생성한 인보이스의 목록/단건 조회
- 인증 없음(401), 존재하지 않는 id(404), 필수값 누락(422)
- billing 주소 불일치의 422
- 제외: 게스트 인보이스, 수정/상태 변경, PDF, 검색 (개요 4번)

## 6. TC 작성 입력값

공통: 헤더 `Accept: application/json`, 인증은 fixture로 받은 토큰(값을 문서에 쓰지 않음). 정상 케이스는 매번 새 Cart를 만들어 상품을 담은 뒤 사용합니다. billing 값은 `GET /postcode-lookup` 응답에서 가져옵니다 (백로그 #3).

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| I1 | `GET /invoices` | 유효한 토큰 | 200, `data` 배열 | High |
| I2 | `GET /invoices` | 유효한 토큰 | 200, `current_page`, `from`, `last_page`, `per_page`, `to`, `total` 존재 | Medium |
| I3 | `POST /invoices` | 유효한 billing + `cash-on-delivery` + `payment_details`=`{}` + 유효한 `cart_id` | 200 (스펙 기준. 소스는 201이라 R7 확인) | High |
| I4 | `POST /invoices` | I3과 동일 | 응답에 `id`, `invoice_number`, `total`, `status`, `invoicelines` 존재 | High |
| I5 | `POST /invoices` | `credit-card`, `bank-transfer`, `buy-now-pay-later`, `gift-card` 각각 | 200 (각 수단별 details 사용) | Medium |
| I6 | `GET /invoices/{invoiceId}` | I3에서 생성한 id | 200, `InvoiceResponse` | High |
| I7 | `GET /invoices/{invoiceId}` | I3의 id | `invoicelines`가 담은 상품/수량과 일치 | Medium |
| I8 | `POST /invoices` | I3과 동일 | 응답의 `billing_*`가 요청값과 일치 | Medium |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| I9 | `GET /invoices` | `Authorization` 없음 | 401 | High |
| I10 | `POST /invoices` | `Authorization` 없음 | 401 | High |
| I11 | `GET /invoices/{invoiceId}` | `Authorization` 없음 | 401 | High |
| I12 | `GET /invoices/{invoiceId}` | 존재하지 않는 id | 404 | High |
| I13 | `POST /invoices` | 필수값 누락 (예: `billing_street`, `payment_method`, `cart_id` 각각) | 422 | High |
| I14 | `POST /invoices` | enum 밖 `payment_method` | 422 | Medium |
| I15 | `POST /invoices` | postcode-lookup과 다른 billing 주소 | 422 (스펙에 422 정의, 구체 메시지 규칙은 스펙에 없어 메시지 비교는 확인 필요, 백로그 #3) | High |
| I16 | `POST /invoices` | 존재하지 않는 `cart_id` | 확인 필요 (스펙은 404/422 둘 다 정의, 기준 없음) | Medium |
| I17 | `GET /invoices/{invoiceId}` | 다른 사용자의 invoice id | 확인 필요 (스펙에 권한 오류 코드 없음) | High |
