# API 분석: Payment

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Payment |
| 목적 | 결제 수단과 상세 정보를 보내 결제 가능 여부를 확인합니다 |
| 사용처 | 결제 화면의 결제 수단 검증, Invoice 생성의 `payment_method`/`payment_details`와 같은 구조 |
| 스펙 근거 | `POST /payment/check`, 스키마 `PaymentRequest`와 결제 수단별 Details |

## 2. 핵심 흐름

1. `POST /payment/check`에 `payment_method`와 `payment_details`를 보냅니다.
2. 200 응답의 `message`를 받습니다 (스펙 예시 "Success status").
3. 이후 Invoice 생성에서 같은 구조를 다시 보냅니다.

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| POST | `/payment/check` | 없음 | 바디 `payment_method`(enum: `bank-transfer`, `cash-on-delivery`, `credit-card`, `buy-now-pay-later`, `gift-card`), `payment_details`(method별 oneOf) | 200 (`message`) 하나만 정의 |

`payment_details` 스키마
- `bank-transfer`: `bank_name`, `account_name`, `account_number`
- `credit-card`: `credit_card_number`, `expiration_date`, `cvv`, `card_holder_name`
- `gift-card`: `gift_card_number`, `validation_code`
- `buy-now-pay-later`: `monthly_installments`
- `cash-on-delivery`: 빈 객체

모든 필드는 string이고 `required`, 형식, 길이 제약이 스펙에 없습니다.

## 4. 리스크

- R3 (높음): 결제 정보에 대한 서버 측 검증이 없어 보이고, 스펙도 422를 정의하지 않음
  - 근거: 백로그 #2 (Confluence 5996545 축3). 스펙 `POST /payment/check`는 200만 정의
  - [불일치] 소스의 `PaymentController::check`는 method별 검증 규칙(카드 번호 형식 등)을 두고 있어 배포본과 다를 수 있음. 배포본 동작은 확인 필요
  - 판단: 스펙 기준으로는 모든 입력에 200이 기대됨. 네거티브 TC의 기대 코드는 스펙에 없으므로 "확인 필요"로 둠. 관찰된 무검증 동작을 기대값으로 쓰지 않음
- R7 (중간): 스펙 응답 메시지와 소스가 다름 [불일치]
  - 근거: 스펙 예시 "Success status", 소스는 "Payment was successful". `message` 값은 문자열 존재 여부만 검증하고 값은 확인 필요
- R2 (높음): 같은 `payment_details` 구조가 Invoice 생성에도 쓰임
  - 근거: `InvoiceRequest.payment_details`가 같은 oneOf 구조. Payment 검증 공백이 Invoice에서도 영향

## 5. 테스트 범위 (포함)

- 5개 결제 수단별 정상 요청의 200 응답과 `message`
- `payment_method` 누락, enum 밖 값 등 스펙에서 도출되는 네거티브 (응답 코드는 확인 필요 표기)
- 카드 번호 형식, 만료일 등 상세 형식 검증은 스펙에 없으므로 "확인 필요" 후보로만 남깁니다.

## 6. TC 작성 입력값

공통: 헤더 `Accept: application/json`, 인증 불필요. 카드/계좌 값은 가짜 값을 씁니다. 스펙에 유효 형식 예시가 없어 값 형식은 확인 필요입니다.

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| PY1 | `POST /payment/check` | `bank-transfer` + `bank_name`, `account_name`, `account_number` | 200, `message` | High |
| PY2 | `POST /payment/check` | `cash-on-delivery` + `{}` | 200, `message` | High |
| PY3 | `POST /payment/check` | `credit-card` + 4개 필드 | 200, `message` | High |
| PY4 | `POST /payment/check` | `buy-now-pay-later` + `monthly_installments` | 200, `message` | Medium |
| PY5 | `POST /payment/check` | `gift-card` + `gift_card_number`, `validation_code` | 200, `message` | Medium |
| PY6 | `POST /payment/check` | PY1~PY5 | `message`가 string. 값은 확인 필요 | Medium |
| PY7 | `POST /payment/check` | `cash-on-delivery`, `payment_details` 생략 | 확인 필요 | Low |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| PY8 | `POST /payment/check` | `payment_method` 누락 | 확인 필요 (스펙은 200만 정의) | High |
| PY9 | `POST /payment/check` | enum 밖 `payment_method` (예: `bitcoin`) | 확인 필요 | High |
| PY10 | `POST /payment/check` | `credit-card`, `payment_details` 필수 필드 누락 | 확인 필요 (백로그 #2 대상, 스펙에 코드 없음) | High |
| PY11 | `POST /payment/check` | `credit-card`, `credit_card_number`가 숫자가 아닌 값 | 확인 필요 (백로그 #2 대상) | High |
| PY12 | `POST /payment/check` | `credit-card`, 과거 `expiration_date` | 확인 필요 | Medium |
| PY13 | `POST /payment/check` | `bank-transfer`, `payment_details` 누락 | 확인 필요 | Medium |
| PY14 | `POST /payment/check` | 빈 바디 `{}` | 확인 필요 | Low |
