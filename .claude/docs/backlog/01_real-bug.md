# 백로그: real-bug
Jira로 올릴 실제 결함. 등록 뒤에도 수정될 때까지 여기 둔다. 작성 형식은 `.claude/guides/backlog-format.md`를 따른다.

### #13 존재하지 않는 상품의 연관 상품 조회가 500
- 발생 배경: API-TC 작성 중 라이브 확인.
- 추정 원인과 근거: 연관 상품 조회에서 상품 존재 여부를 확인하지 않고 처리하다 예외가 나는 것으로 추정한다. 소스는 확인하지 않았다.
- 분류와 상태: real-bug(유형 A) / 중요도 Medium / Jira QA-4 등록(2026-10-07) / 발견 2026-10-05, 마지막 확인 2026-10-08 라이브
- 대상 TC
  1. [API_53] 연관 상품 조회 - 존재하지 않는 상품 id 확인
     - 스펙: `GET /products/{productId}/related`는 `404 ItemNotFoundResponse`를 정의한다.
     - 라이브: `500 {"message": "Server Error"}`. 형식이 맞는 ULID와 잘못된 id 모두 500이다. 같은 id로 `GET /products/{productId}`는 404 `Requested item not found`다(2026-10-08 재확인).
     - 현재 테스트: `xfail(strict=True)`로 pin

### #15 빈 장바구니 문구가 스펙과 다름
- 발생 배경: UI 스크립트 작성 중 발견. 시트 기대결과를 라이브 문구로 바꿨다가 스펙이 정답이라 롤백했다.
- 추정 원인과 근거: 앱 i18n 값이 스펙과 다르다. 근거는 `.claude/docs/spec analysis/ui/ui-cart.md`.
- 분류와 상태: real-bug(유형 A) / Jira 등록 대기(전체 테스트 뒤 근거 정리) / 발견 2026-10-05, 마지막 확인 2026-10-05 라이브
- 대상 TC
  1. [UI_31] 마지막 상품 삭제 시 빈 장바구니 문구 확인
     - 스펙: `v5` Checkout Cart AC4는 "Your shopping cart is empty"다.
     - 라이브: "The cart is empty. Nothing to display."(`en.json` `pages.checkout.cart.empty`)
     - 현재 테스트: `xfail(strict=True)`로 pin

### #16 수량 상한이 스펙과 다름
- 발생 배경: UI 스크립트 작성 중 수량 입력 TC에서 발견.
- 추정 원인과 근거: 소스 `detail.component.ts`의 `MAX_QUANTITY = 99`. 근거는 `.claude/docs/spec analysis/ui/ui-product-detail.md` R3 [불일치].
- 분류와 상태: real-bug(유형 A) / Jira 등록 대기(전체 테스트 뒤 근거 정리) / 발견 2026-10-05, 마지막 확인 2026-10-05 라이브
- 대상 TC
  1. [UI_22] 수량 100 입력 시 입력값 유지 확인
     - 스펙: `v5` Product Detail AC7의 상한은 999,999,999다.
     - 라이브: 입력란이 `max="99"`이고 큰 값은 99로 보정한다.
     - 현재 테스트: `xfail(strict=True)`로 pin
  2. [UI_28] 장바구니 수량 0, 1000000000 입력 시 보정 확인
     - 스펙/라이브: 장바구니 수량 입력란도 같은 상한(99)이다.
     - 현재 테스트: 상한 비교만 테스트 안에서 `pytest.xfail("백로그 #16")`로 pin (2026-10-10). 0 → 1 보정은 통과

### #26 상품 검색의 일치 기준이 스펙에 없고 검색어 길이에 따라 결과가 다름
- 발생 배경: UI_13 스크립트 작성 중 발견(2026-10-10). "hammer" 검색 결과에 상품명에 hammer가 들어간 "Sledgehammer"가 빠졌다.
- 추정 원인과 근거: sprint5 `ProductService::searchProducts`가 4자 이상은 FULLTEXT 단어 시작 일치(`+term*`), 3자 이하는 `LIKE %term%`를 쓰는 것으로 보인다(소스는 원인 추정 근거로만 씀). 라이브 확인(2026-10-10): "hammer" 6건(Sledgehammer 없음), "ham" 7건(Sledgehammer 포함), "ammer" 0건.
- 분류와 상태: real-bug(유형 E 스펙 미정의에서 전환) / 중요도 Low / 사용자 판단(2026-10-10): 스펙에 기준이 없어도 기능 의도상 기대결과와 실제결과가 달라 real-bug로 판단 / Jira QA-7 등록(2026-10-10) / 발견 2026-10-10, 마지막 확인 2026-10-10 전체 실행(UI_13 실패로 재현)
- 대상 TC
  1. [UI_13] 상품 검색 시 검색어 포함 상품 결과 노출 확인
     - 스펙: `v5` Product Overview AC4는 "only matching products"라고만 쓰고 일치 기준(부분 일치, 단어 시작 일치)과 검색 대상 필드를 정의하지 않는다.
     - 라이브: 4자 이상 검색어는 단어 시작 일치라 "Sledgehammer"가 "hammer" 결과에서 빠진다.
     - 현재 테스트: 3-1 비교만 테스트 안에서 `pytest.xfail("백로그 #26(QA-7)")`로 pin(2026-10-10). 누락 상품이 모두 단어 중간 일치일 때만 xfail하고, 다른 누락은 그대로 실패한다. 3-2는 통과

### #1 상품 응답의 중첩 brand/category가 스펙보다 축소됨
- 발생 배경: api-demo Product 스키마 작업(study 세션) 중 발견.
- 추정 원인과 근거: 같은 이름의 스키마를 재사용해 실제보다 풍부한 구조로 보이는 문서화 방식의 문제다. `BrandResponse`/`CategoryResponse`/`ProductResponse` 모두 `required`가 없어 계약 위반으로 보기 어렵다.
- 분류와 상태: real-bug(2026-10-10 재분류: 스펙이 정한 값과 라이브가 다름, 이전 안건 유형 C) / 남은 일: API 스펙 문서(Confluence 6750210)나 TC 문서(5898268)에 "Product 응답의 brand/category는 요약형"이라 명시 / 발견 2026-09-27, 마지막 확인 2026-10-08 라이브
- 대상 TC
  1. [TC 없음] 상품 목록 응답의 brand/category 구조
     - 스펙: `ProductResponse.brand`는 `BrandResponse`(id/name/slug), `category`는 `CategoryResponse`(id/name/slug/parent_id/sub_categories)다.
     - 라이브: `GET /products`는 `brand: {id, name}`, `category: {id, name, slug}`만 내려준다.
       - ex: `"brand": {"id": "01M3H8BVA0CNXSY7MS0VQ03VTZ", "name": "ForgeFlex Tools"}`
       - ex: `"category": {"id": "01M3H8BVP0KSY9KZ0ZBGQ0FK8Q", "name": "Pliers", "slug": "pliers"}`
     - 현재 테스트: api-demo가 `ProductBrandRef`/`ProductCategoryRef` 축소 모델로 통과한다.

### #2 결제 성공 메시지와 입력 검증이 스펙과 다름
- 발생 배경: Confluence "API Test QA Plan"(5996545)의 "결제 무검증" 기술을 2026-10-05 라이브로 재확인해 정정했다. 은행이체, 기프트카드 등 다른 수단의 필드 검증은 미확인이다.
- 추정 원인과 근거: 결제 수단 자체는 검증하지 않는 구현이다. 위반 시 에러 응답이 스펙, Swagger, wiki 어디에도 없다.
- 분류와 상태: real-bug(2026-10-10 재분류: 스펙이 정한 값과 라이브가 다름, 이전 안건 유형 B + 유형 C) / 메시지 비교만 부분 xfail. API_96, 97은 xfail하지 않고 안건으로 올린다(2026-10-06 사용자 결정) / 발견 2026-10-05, 마지막 확인 2026-10-08 라이브
- 대상 TC
  1. [API_93] 결제 정상 동작 확인
  2. [API_94] 신용카드 결제 정상 동작 확인
  3. [API_95] 계좌이체 결제 정상 동작 확인
     - 스펙 예시: 200 `message` "Success status"
     - 라이브: "Payment was successful"(유형 B, 1~3번 공통)
  4. [API_96] 결제 방식 "payment_method" 필드 누락 확인
  5. [API_97] enum에 없는 결제 방식 확인
     - 스펙: `payment_method`는 enum 5종이고 응답은 200만 정의한다.
     - 라이브: 누락이나 "bitcoin"도 200 "Payment was successful"로 처리한다(유형 C, 4~5번 공통).
     - 참고: "credit-card"일 때 `payment_details`는 검증한다(필드 누락 422, 형식 오류 422). 이 검증 TC는 API_98(#22)이다.

### #12 인보이스 생성 성공 코드가 스펙과 다름
- 발생 배경: API-TC 작성 중 라이브 확인. 스펙 기준으로 쓴 기대결과(200)는 실행하면 실패한다.
- 추정 원인과 근거: 생성 API의 일반적인 201 응답이고 스펙이 낡았을 가능성이 있다. 스펙을 고칠지 TC를 고칠지 결정이 필요하다.
- 분류와 상태: real-bug(2026-10-10 재분류: 스펙이 정한 값과 라이브가 다름, 이전 안건 유형 A, 스펙이 낡았을 가능성) / 성공 코드 비교만 부분 xfail / 발견 2026-10-05, 마지막 확인 2026-10-05 라이브
- 대상 TC
  1. [API_99] 인보이스 정상 생성 확인
  2. [API_100] 신용카드 결제 인보이스 생성 확인
     - 스펙: `POST /invoices` 응답은 `200`만 정의한다.
     - 라이브: `201`을 반환한다.

### #18 연관 상품, 상품 검색, 인보이스 목록의 항목 구조가 스펙과 다름
- 발생 배경: API 스크립트 작성 중 pydantic 검증 실패로 발견.
- 추정 원인과 근거: 스펙 스키마에 `required`가 없어 필드 누락이 계약 위반인지 판단이 필요하다.
- 분류와 상태: real-bug(2026-10-10 재분류: 스펙이 정한 값과 라이브가 다름, 이전 안건 유형 A이나 `required` 없음) / API_54는 상품 모델 기준 검증 + `xfail(strict=True)`로 pin(2026-10-06 사용자 결정) / 발견 2026-10-06, 마지막 확인 2026-10-08 라이브(연관 상품)
- 대상 TC
  1. [API_52] 연관 상품 조회 확인
  2. [API_54] 연관 상품 항목 필드 구조 확인
     - 스펙: 항목은 `ProductResponse`이고 `co2_rating`과 `category`(`CategoryResponse`, `slug` 포함)가 있다.
     - 라이브: `co2_rating`이 없고 `category`에 `slug`가 없다.
     - 현재 테스트: 라이브 구조로 만든 `RelatedProductResponse` 모델로 통과한다.
  3. [API_55~58] 상품 검색 조회(정상, 결과 없음, 소문자 검색어, 페이지 정보 필드 타입)
     - 스펙: `GET /products/search`의 `data` 항목은 `ProductResponse`다.
     - 라이브: `category`에 `slug`가 없다.
     - 현재 테스트: `SearchProductResponse` 모델로 통과한다.
  4. [API_113] 인보이스 목록 조회 확인
  5. [API_114] 인보이스 목록 응답 바디의 페이지 정보 필드 타입 확인
     - 스펙: `GET /invoices`의 `data` 항목은 `InvoiceResponse`다.
     - 라이브: 항목에 `status_message`, `created_at`, `payment_details` 등이 없고, 상품에 `description`, `brand`, `category`, `is_rental`이 없다.
     - 현재 테스트: `InvoiceListItem` 모델로 통과한다.

### #19 장바구니 404 메시지가 스펙과 다르고 엔드포인트마다 다름
- 발생 배경: API 스크립트 작성 중 메시지 비교에서 발견. 2026-10-06에 시트를 스펙 값으로 바꿨다. wiki는 404 공통 메시지를 "Resource not found"로 적었다.
- 추정 원인과 근거: 엔드포인트별로 메시지를 따로 하드코딩한 구현이다. `example`은 계약이 아니라서 판단이 필요하다.
- 분류와 상태: real-bug(2026-10-10 재분류: 스펙이 정한 값과 라이브가 다름, 이전 안건 유형 B) / 메시지 비교만 부분 xfail / 발견 2026-10-06, 마지막 확인 2026-10-08 라이브(DELETE 2곳)
- 대상 TC
  1. [API_72] 존재하지 않는 장바구니 수량 변경 실패 확인
     - 스펙 예시: PUT은 `ResourceNotFoundResponse` "Resource not found"
     - 라이브: "Cart doesn't exist"
  2. [API_75] 존재하지 않는 장바구니의 상품 삭제 실패 확인
  3. [API_82] 존재하지 않는 장바구니 삭제 실패 확인
     - 스펙 예시: DELETE는 `ResourceNotFoundResponse` "Resource not found"
     - 라이브: "Cart doesnt exists"(오타)
  4. [API_85] 존재하지 않는 장바구니에 상품 추가 실패 확인
     - 스펙 예시: `POST /carts/{id}`는 `ItemNotFoundResponse` "Requested item not found"
     - 라이브: "Cart not found"

### #20 로그인 토큰 값이 스펙 예시와 다름
- 발생 배경: API 스크립트 작성 중 로그인 응답 비교에서 발견. 2026-10-06에 시트를 스펙 값으로 바꿨다. wiki는 타입만 적고 값은 적지 않았다.
- 추정 원인과 근거: 예시값이라 계약 위반인지는 안건이다.
- 분류와 상태: real-bug(2026-10-10 재분류: 스펙이 정한 값과 라이브가 다름, 이전 안건 유형 B) / 해당 비교만 부분 xfail / 발견 2026-10-06, 마지막 확인 2026-10-08 라이브
- 대상 TC
  1. [API_08] 유효한 계정으로 정상 로그인 확인
     - 스펙 예시: `token_type` "Bearer", `expires_in` 120
     - 라이브: "bearer", 300

### #21 장바구니 수량 변경 응답 바디가 스펙과 다름
- 발생 배경: 2026-10-06 스펙 불일치 목록 작성 중 확인. 이번 통합에서 백로그에 처음 등록했다.
- 추정 원인과 근거: 응답 클래스(`UpdateResponse`)와 실제 구현이 다르다. 소스는 확인하지 않았다.
- 분류와 상태: real-bug(2026-10-10 재분류: 스펙이 정한 값과 라이브가 다름, 이전 안건 유형 A) / 시트 기대결과를 스펙 값으로 고칠지 결정 대기 / 발견 2026-10-06, 마지막 확인 2026-10-06
- 대상 TC
  1. [API_68] 장바구니 상품 수량 정상 변경
     - 스펙: `PUT /carts/{cartId}/product/quantity`의 200 응답은 `UpdateResponse` `{"success": true}`다.
     - 라이브: `{"result": "item added or updated"}`
     - 현재 테스트: 시트 기대결과가 라이브 값으로 되어 있어 스펙 기준 규칙과 어긋난다.

### #29 카테고리 페이지에 Price Range 슬라이더가 없음
- 발생 배경: 2026-10-11 `/flow-map` 보충 탐색과 UI TC 추가(B1) 중 발견.
- 추정 원인과 근거: 카테고리 페이지 템플릿에 가격 슬라이더가 빠진 것으로 추정한다. 소스는 확인하지 않았다.
- 분류와 상태: real-bug(유형 A) 후보 / 중요도 Low(메인 화면에서 가격 필터로 우회 가능) / 사용자 검토 전 / 발견 2026-10-11, 마지막 확인 2026-10-11 라이브
- 대상 TC
  1. [UI_50] 카테고리 페이지 필터 구성 요소 노출 확인
     - 스펙: `v5` Browse Products by Category AC2는 카테고리 페이지에 상품 목록과 같은 필터(하위 카테고리, 브랜드, 정렬, 페이지 이동, 가격 슬라이더)가 있다고 정한다.
     - 라이브: `/category/hand-tools`에 정렬, 하위 카테고리, 브랜드, Eco-Friendly 필터, 페이지 이동은 있고 Price Range가 없다.
     - 현재 테스트: 아직 없음(스크립트 작성 전)

### #30 체크아웃 Sign in 단계의 로그인 상태 안내 문구가 스펙과 다름
- 발생 배경: 2026-10-11 UI TC 추가(B5) 중 라이브 확인으로 발견.
- 추정 원인과 근거: 앱 문구가 스펙 예시와 다르다. 소스는 확인하지 않았다.
- 분류와 상태: real-bug(유형 A) 후보 / 중요도 Low(문구 차이, 진행에는 영향 없음) / 사용자 검토 전 / 발견 2026-10-11, 마지막 확인 2026-10-11 라이브
- 대상 TC
  1. [UI_83] 로그인 상태로 Sign in 단계 진입 시 로그인 폼 미노출과 [Proceed to checkout] 버튼 노출 확인
     - 스펙: `v5` Checkout Sign In AC5는 "You are already signed in as [First Name] [Last Name]"을 표시한다.
     - 라이브: "Hello <이름>, you are already logged in. You can proceed to checkout."
     - 현재 테스트: 아직 없음(스크립트 작성 전)

### #31 Billing Address 자동 채움에 계정의 Country가 채워지지 않음
- 발생 배경: 2026-10-11 UI TC 추가(B5) 중 라이브와 계정 정보를 대조해 발견.
- 추정 원인과 근거: 자동 채움이 Street, City만 옮기는 것으로 보인다. 근거는 UI 테스트 계정의 `GET /users/me`에 country 값이 있는데 Billing 화면의 [Country]가 비어 있는 것(2026-10-11). State, Postcode, House number는 계정에 값이 없어 판단 대상이 아니다.
- 분류와 상태: real-bug(유형 A) 후보 / 중요도 Low(사용자가 직접 선택해 진행 가능) / 사용자 검토 전 / 발견 2026-10-11, 마지막 확인 2026-10-11 라이브
- 대상 TC
  1. [UI_84] 로그인 상태로 Billing Address 단계 진입 시 계정 주소 자동 채움 확인
     - 스펙: `v5` Checkout Billing Address AC4는 주소 필드가 계정 주소 정보로 채워진다고 정한다.
     - 라이브: [Street], [City]만 채워지고 [Country]는 선택되지 않는다.
     - 현재 테스트: 아직 없음(스크립트 작성 전)

