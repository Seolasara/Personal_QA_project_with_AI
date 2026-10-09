> 이 파일이 API 분석의 메인입니다. 기능별 상세는 아래 2번 표의 파일을 참고합니다.

# Toolshop API 요구사항 분석 개요

## 1. 분석 개요

- 작성일: 2026-10-05
- 분석 기준
  - 서비스 레포 기준 커밋: `c752a70` (2026-10-04, 분석일 직전 마지막 커밋, 추정)
  - 분석일: 2026-10-05
  - 감시 경로: `sprint5/API/storage/api-docs/api-docs.json`, `sprint5/API/routes/`, `sprint5/API/app/`, 스펙 `docs/user-stories/`
- 대상: Toolshop API (`https://api.practicesoftwaretesting.com`), in-scope 리소스 9개, 엔드포인트 24개
  - Category, Brand, Product, Cart, Postcode, Payment, Login, Logout, Invoice
- 근거 자료
  - 스펙 원본: `api-demo/api-docs.json` (OpenAPI, 기대 동작의 기준)
  - 보조 소스: GitHub `testsmith-io/practice-software-testing`의 `sprint5/API` (routes, Controller, Request 검증 규칙)
  - 알려진 이슈 백로그: `.claude/docs/backlog/00_index.md` (이하 "백로그 #N")
  - 컨벤션: `api-demo/CLAUDE.md`
- 판단 기준
  - 스펙이 기대 동작의 기준입니다.
  - 소스는 보조 자료입니다. 스펙과 다르면 "[불일치]"로 표시하고 판단은 "스펙 기준"으로 씁니다.
  - 스펙에 없는 값은 만들지 않고 "확인 필요"로 씁니다. 소스에만 있는 동작은 TC 근거로 쓰지 않습니다.
  - 라이브 API는 호출하지 않았습니다. 라이브 관찰 사실은 백로그에 있는 것만 인용합니다.
- 공통 전제
  - 스펙의 서버 URL은 `https://api.practicesoftwaretesting.com`이고, 인증은 `apiAuth`(HTTP Bearer JWT) 한 가지입니다.
  - 스펙에서 `security`가 지정된 in-scope 엔드포인트는 `GET /users/logout`, `GET /invoices`, `POST /invoices`, `GET /invoices/{invoiceId}` 4개입니다.
  - 검증 실패(422)와 미존재(404)를 확인하는 네거티브 케이스는 `Accept: application/json` 헤더가 필수입니다. 없으면 302로 나옵니다 (백로그 #4, `api-demo/CLAUDE.md`).

## 2. 기능별 분석 파일

| 기능 | 파일 | 엔드포인트 수 | TC 후보 수 | 비고 |
|---|---|---|---|---|
| Login / Logout | [api-auth.md](api-auth.md) | 2 | 13 | 계정 잠김(423), 토큰 만료 120 |
| Category | [api-category.md](api-category.md) | 4 | 12 | 읽기 전용만 포함 |
| Brand | [api-brand.md](api-brand.md) | 3 | 10 | 읽기 전용만 포함 |
| Product | [api-product.md](api-product.md) | 4 | 16 | nested brand/category 불일치(백로그 #1) |
| Cart | [api-cart.md](api-cart.md) | 6 | 21 | 상태 의존, 응답 스키마 불일치 |
| Postcode | [api-postcode.md](api-postcode.md) | 1 | 9 | 외부 조회 의존(502) |
| Payment | [api-payment.md](api-payment.md) | 1 | 14 | 무검증 이슈(백로그 #2) |
| Invoice | [api-invoice.md](api-invoice.md) | 3 | 17 | billing 주소 검증(백로그 #3), 인증 필수 |
| 합계 |  | 24 | 112 | 후보 수는 중복 포함, 선별은 TC-Writer 판단 |

## 3. 리스크 목록

- 우선순위 기준: 틀어질 가능성 x 영향 범위
  - 높음: 틀어질 가능성이 높고(백로그 확인 또는 스펙 공백이 큼) 여러 리소스나 핵심 결제 흐름에 영향
  - 중간: 한 리소스 또는 한 흐름에 영향, 또는 가능성이 중간
  - 낮음: 가능성이 낮거나 영향이 국소적
- ID는 우선순위 순으로 매겼고, 기능 파일에서도 같은 ID를 씁니다.

| ID | 우선순위 | 리스크 | 예상 영향 범위 | 상세 링크 |
|---|---|---|---|---|
| R1 | 높음 | `Accept: application/json` 헤더가 없으면 검증 실패가 422/404 대신 302로 나와 네거티브 TC가 오판됨 (백로그 #4) | 전 리소스의 422/404 네거티브 TC | [api-cart.md](api-cart.md), [api-postcode.md](api-postcode.md) |
| R2 | 높음 | `POST /invoices`의 billing 주소가 postcode-lookup 결과와 일치해야 하는 제약이 스펙에 없음 (백로그 #3) | Invoice 생성, 결제 흐름 E2E | [api-invoice.md](api-invoice.md) |
| R3 | 높음 | `POST /payment/check`의 결제 정보 서버 검증이 없어 보임, 스펙도 422를 정의하지 않음 (백로그 #2) | Payment 전체, Invoice 생성 시 payment_details | [api-payment.md](api-payment.md) |
| R4 | 높음 | 로그인 3회 실패 시 계정 잠김(423), 올바른 비밀번호로도 해제 안 됨 (백로그 #8). 스펙은 200만 정의 | Login 네거티브 TC, 같은 계정을 쓰는 모든 인증 TC | [api-auth.md](api-auth.md) |
| R5 | 높음 | Invoice 인증/권한 범위가 불명확함. 스펙은 401만 정의, 타 사용자 invoice 접근 시 응답은 확인 필요 | Invoice 조회 전체, 개인 정보 노출 | [api-invoice.md](api-invoice.md) |
| R6 | 중간 | Product 중첩 `brand`/`category`가 스펙 스키마보다 축소된 필드만 내려옴 (백로그 #1) | Product 응답 스키마 검증 TC, Invoice line의 product | [api-product.md](api-product.md) |
| R7 | 중간 | 스펙 응답 코드 누락/불일치 [불일치]: `POST /invoices` 스펙 200 vs 소스 201, 로그인 실패 코드 미정의, Cart 400 미정의 | 상태코드 기대값을 쓰는 모든 TC | [api-invoice.md](api-invoice.md), [api-auth.md](api-auth.md), [api-cart.md](api-cart.md) |
| R8 | 중간 | `CartResponse`가 `id`만 정의하나 소스는 cartItems를 포함해 반환 [불일치]. `extra="forbid"` 스키마 검증이 contract 실패로 나올 수 있음 | `GET /carts/{cartId}` 응답 검증 | [api-cart.md](api-cart.md) |
| R9 | 중간 | Cart는 생성/추가가 쌓이는 상태 의존 리소스이고 수량 상한이 스펙에 없음 (소스는 1~99) | Cart TC 전체, 데이터 정리 | [api-cart.md](api-cart.md) |
| R10 | 중간 | 토큰 `expires_in` 120 예시와 로그아웃 후 토큰 무효화 동작으로 인증 TC가 타이밍에 민감함 | Login/Logout, Invoice 인증 TC | [api-auth.md](api-auth.md) |
| R11 | 중간 | Postcode 조회가 외부 서비스와 국가별 형식에 의존하고 502가 있음 | Postcode TC, 데이터 의존하는 Invoice TC | [api-postcode.md](api-postcode.md) |
| R12 | 낮음 | Product 목록 필터/정렬 파라미터(`between`, `sort`, `is_rental`)가 모두 string이고 형식이 설명 문자열뿐임 | Product 목록/검색 TC | [api-product.md](api-product.md) |
| R13 | 낮음 | path id 형식(ULID string)이 스펙에 없어 형식 오류 id의 응답이 404인지 422인지 불명 | 모든 `{id}` 경로 네거티브 TC | [api-category.md](api-category.md), [api-brand.md](api-brand.md) |
| R14 | 낮음 | 검색 `q` 필수인데 누락 시 응답 코드를 스펙이 정의하지 않음 | Category/Brand/Product 검색 네거티브 TC | [api-category.md](api-category.md), [api-brand.md](api-brand.md), [api-product.md](api-product.md) |

## 4. 제외와 제외 사유

- 리소스 단위 제외
  - User 중 회원가입, 프로필, 비밀번호 변경/찾기, 사용자 관리: 범위 밖 요청에 따라 제외
  - Favorite, Contact(messages), Product Spec, Report, TOTP, Stream(sales-stream), Image: 범위 밖
  - ex: `POST /users/register`, `GET /users/me`, `GET /favorites`, `POST /messages`, `GET /reports/*`
- in-scope 리소스 안에서 제외한 엔드포인트
  - Brand/Category/Product의 쓰기(`POST`, `PUT`, `PATCH`, `DELETE`): 스펙에서 `DELETE`만 `security`가 있고 나머지 쓰기는 인증이 지정되지 않아 공개 데모 데이터를 변경할 위험이 있어 이번 범위에서 뺍니다.
    - 이 쓰기 엔드포인트의 보안 정의 공백(소스에서도 `DELETE`만 admin role 미들웨어)은 별도 보안 점검 후보로 남깁니다.
  - `QUERY` 메서드 변형(`/brands/search`, `/categories/tree`, `/categories/search`, `/products`, `/products/search`): HTTP QUERY는 httpx 표준 지원 밖이고 GET과 같은 키를 쓰므로 GET으로 대표합니다.
  - Invoice의 `POST /invoices/guest`, `PUT`/`PATCH /invoices/{invoiceId}`, `PUT /invoices/{invoiceId}/status`, `GET /invoices/search`, `download-pdf`, `download-pdf-status`: 범위의 Invoice 3개 엔드포인트(목록, 생성, 단건 조회) 밖이고 관리자/PDF 흐름이 섞여 있어 제외합니다.
  - `GET /products/{productId}/specs` 계열: Product Spec 리소스이므로 제외합니다.

## 5. 확인 못 한 것

- 라이브 API 응답: 호출하지 않았으므로 모든 실제 응답 형태는 백로그에 적힌 것 외에는 확인하지 못했습니다.
- 스펙 `error` 응답 본문 스키마: 404/405/422/401 응답이 `components/responses` 참조이고 본문 구조는 이번 분석에서 TC 기대값으로 쓰지 않았습니다. 필요하면 TC-Writer가 `api-docs.json`의 `components/responses`를 확인해야 합니다.
- 소스 버전과 배포본의 일치 여부: `sprint5/API`(main, 2026년 저작권 표기)가 배포 환경과 같은 버전인지 확인하지 못했습니다. 특히 백로그 #2(결제 무검증)와 달리 소스의 `PaymentController`에는 검증 규칙이 있어서, 배포본 동작은 확인 필요입니다.
- 백로그 #3의 상세 근거(TC API_40 Note)와 Confluence 5996545 축3 패널: 접근하지 않았습니다.
- 검색 결과 매칭 규칙(대소문자, 부분일치), 페이지당 건수(`per_page`), 정렬 기본값: 스펙에 없어 확인 필요입니다.
- 인증 만료/잠김 상세 정책(해제 방법 포함): 백로그 #8만 근거이고 스펙에 없습니다.
