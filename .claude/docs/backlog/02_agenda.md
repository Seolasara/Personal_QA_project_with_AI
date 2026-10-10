# 백로그: 안건
스펙과 라이브가 다르지만 결함 여부는 스펙 쪽 판단이 필요한 것. wiki 안건 문서로 올린다. 작성 형식은 `.claude/guides/backlog-format.md`를 따른다.
- 확인 순서(2026-10-06): 스펙(`api-docs.json`) → Swagger → wiki "API specification"(Confluence 6750210) → TC. Swagger는 로컬 `api-docs.json`과 같고, wiki는 대부분 타입만 적고 값은 적지 않았다.

### #1 상품 응답의 중첩 brand/category가 스펙보다 축소됨
- 발생 배경: api-demo Product 스키마 작업(study 세션) 중 발견.
- 추정 원인과 근거: 같은 이름의 스키마를 재사용해 실제보다 풍부한 구조로 보이는 문서화 방식의 문제다. `BrandResponse`/`CategoryResponse`/`ProductResponse` 모두 `required`가 없어 계약 위반으로 보기 어렵다.
- 분류와 상태: 안건(유형 C) / 남은 일: API 스펙 문서(Confluence 6750210)나 TC 문서(5898268)에 "Product 응답의 brand/category는 요약형"이라 명시 / 발견 2026-09-27, 마지막 확인 2026-10-08 라이브
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
- 분류와 상태: 안건(유형 B + 유형 C) / 메시지 비교만 부분 xfail. API_96, 97은 xfail하지 않고 안건으로 올린다(2026-10-06 사용자 결정) / 발견 2026-10-05, 마지막 확인 2026-10-08 라이브
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

### #3 인보이스 생성 시 billing address 검증이 일부만 있음
- 발생 배경: API-TC 작성 중 postcode-lookup(API_86) 응답과 대조하며 라이브 확인.
- 추정 원인과 근거: 검증 대상에 street가 빠져 있다. 스펙 미정의 동작이라 #22와 같은 성격이다.
- 분류와 상태: 안건(유형 E) / 발견 2026-10-05, 마지막 확인 2026-10-05 라이브(인보이스가 남아 재확인 생략)
- 대상 TC
  1. [API_108] postcode-lookup과 다른 billing_city로 인보이스 생성 실패 확인
     - 스펙: 이 제약은 명시되어 있지 않다. `POST /invoices`는 200/401/404/405/422를 정의한다.
     - 라이브: `billing_city`, `billing_state`, `billing_postal_code` 중 하나라도 다르면 422를 반환한다.
       - ex: `{"billing_country": ["The billing_country does not match the entered address. The city does not belong to the selected country."]}` (state가 다르면 마지막 문구가 "The state does not belong...")
  2. [API_100] 신용카드 결제 인보이스 생성 확인
     - 라이브: `billing_street`만 다르게 보내면 검증을 통과해 201로 생성된다.

### #12 인보이스 생성 성공 코드가 스펙과 다름
- 발생 배경: API-TC 작성 중 라이브 확인. 스펙 기준으로 쓴 기대결과(200)는 실행하면 실패한다.
- 추정 원인과 근거: 생성 API의 일반적인 201 응답이고 스펙이 낡았을 가능성이 있다. 스펙을 고칠지 TC를 고칠지 결정이 필요하다.
- 분류와 상태: 안건(유형 A, 스펙이 낡았을 가능성) / 성공 코드 비교만 부분 xfail / 발견 2026-10-05, 마지막 확인 2026-10-05 라이브
- 대상 TC
  1. [API_99] 인보이스 정상 생성 확인
  2. [API_100] 신용카드 결제 인보이스 생성 확인
     - 스펙: `POST /invoices` 응답은 `200`만 정의한다.
     - 라이브: `201`을 반환한다.

### #14 검색 엔드포인트가 `q` 누락을 허용함
- 발생 배경: API-TC 작성 중 라이브 확인. 상품 검색은 2026-10-08에 확인했다.
- 추정 원인과 근거: 서버가 필수 파라미터를 검증하지 않는다. 위반 시 에러 응답이 스펙, Swagger, wiki 어디에도 없다.
- 분류와 상태: 안건(유형 C) / xfail하지 않고 안건으로 올린다(2026-10-06 사용자 결정) / 발견 2026-10-05, 마지막 확인 2026-10-08 라이브
- 대상 TC
  1. [API_22] 필수 파라미터 q 누락 시 브랜드 검색 응답 확인
  2. [API_37] 필수 파라미터 q 누락 시 카테고리 검색 응답 확인
     - 스펙: `q`는 `required: true`이고 응답은 200/404/405만 정의한다(422 없음).
     - 라이브: `q` 없이 호출하면 200으로 전체 목록을 반환한다.
  3. [TC 없음] 상품 검색 `q` 누락
     - 라이브: `GET /products/search`는 200 빈 목록(`data: []`)을 반환한다.

### #18 연관 상품, 상품 검색, 인보이스 목록의 항목 구조가 스펙과 다름
- 발생 배경: API 스크립트 작성 중 pydantic 검증 실패로 발견.
- 추정 원인과 근거: 스펙 스키마에 `required`가 없어 필드 누락이 계약 위반인지 판단이 필요하다.
- 분류와 상태: 안건(유형 A이나 `required` 없음) / API_54는 상품 모델 기준 검증 + `xfail(strict=True)`로 pin(2026-10-06 사용자 결정) / 발견 2026-10-06, 마지막 확인 2026-10-08 라이브(연관 상품)
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
- 분류와 상태: 안건(유형 B) / 메시지 비교만 부분 xfail / 발견 2026-10-06, 마지막 확인 2026-10-08 라이브(DELETE 2곳)
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
- 분류와 상태: 안건(유형 B) / 해당 비교만 부분 xfail / 발견 2026-10-06, 마지막 확인 2026-10-08 라이브
- 대상 TC
  1. [API_08] 유효한 계정으로 정상 로그인 확인
     - 스펙 예시: `token_type` "Bearer", `expires_in` 120
     - 라이브: "bearer", 300

### #21 장바구니 수량 변경 응답 바디가 스펙과 다름
- 발생 배경: 2026-10-06 스펙 불일치 목록 작성 중 확인. 이번 통합에서 백로그에 처음 등록했다.
- 추정 원인과 근거: 응답 클래스(`UpdateResponse`)와 실제 구현이 다르다. 소스는 확인하지 않았다.
- 분류와 상태: 안건(유형 A) / 시트 기대결과를 스펙 값으로 고칠지 결정 대기 / 발견 2026-10-06, 마지막 확인 2026-10-06
- 대상 TC
  1. [API_68] 장바구니 상품 수량 정상 변경
     - 스펙: `PUT /carts/{cartId}/product/quantity`의 200 응답은 `UpdateResponse` `{"success": true}`다.
     - 라이브: `{"result": "item added or updated"}`
     - 현재 테스트: 시트 기대결과가 라이브 값으로 되어 있어 스펙 기준 규칙과 어긋난다.

### #22 스펙에 응답이 정의되지 않은 동작을 라이브 기준으로 TC에 씀
- 발생 배경: 2026-10-06 스펙 불일치 목록 작성 중 분류. 시트 Note에 "확인 필요"로 표시되어 있다.
- 추정 원인과 근거: 스펙이 해당 응답을 정의하지 않았다. 불일치가 아니다.
- 분류와 상태: 안건(유형 E) / 스펙 보완 요청 여부 결정 대기, 전체 실행에서 제외(`spec_undefined` 마커, 2026-10-10 사용자 결정. API_01~07, 46, 96, 97, 113 포함) / 발견 2026-10-06, 마지막 확인 2026-10-10
- 대상 TC: 아래 모두 스펙에 응답 정의가 없고 시트가 라이브 응답을 기대결과로 쓴다.
  1. 로그인 실패 401과 에러 바디
     - [API_01]~[API_07] 비유효 이메일, 비유효 비밀번호, 필드 누락, 존재하지 않는 이메일 등 로그인 실패 확인
  2. 잘못된 토큰이나 로그아웃한 토큰 응답
     - [API_13] 형식이 잘못된 토큰으로 로그아웃 실패 확인
     - [API_14] 로그아웃한 토큰으로 로그아웃 재호출 실패 확인
     - [API_110] 형식이 잘못된 토큰으로 인보이스 단건 조회 실패 확인
     - [API_116] 로그아웃한 토큰으로 인보이스 목록 조회 확인
  3. 대소문자와 부분 일치 검색 규칙
     - [API_23] 소문자 검색어 "forge" 입력 시 "ForgeFlex Tools" 브랜드 조회 확인
     - [API_38] 소문자 검색어 "hammer" 입력 시 "Hammer" 카테고리 조회 확인
     - [API_39] 검색어 "tools" 입력 시 이름에 "Tools"가 포함된 카테고리 조회 확인
     - [API_57] 소문자 검색어 "hammer" 입력 시 "Hammer" 상품 검색 결과 확인
  4. 장바구니 관련 동작
     - [API_60] 바디 없이 장바구니 생성 확인
     - [API_63] 상품 추가 후 장바구니 조회 확인
     - [API_64] 삭제한 장바구니 조회 실패 확인
     - [API_65] 수량 변경 후 장바구니 조회 반영 확인
     - [API_67] 같은 상품 2회 추가 확인
     - [API_74] 장바구니에 담기지 않은 상품 삭제 확인
     - [API_76] 상품 삭제 후 장바구니 조회에서 상품 제거 확인
  5. 신용카드 필수 필드 검증, 주소 불일치 검증
     - [API_98] 신용카드 "payment_details" 필수 필드 누락 확인
     - [API_108] postcode-lookup과 다른 billing_city로 인보이스 생성 실패 확인(#3)
  6. 타 사용자 인보이스 조회
     - [API_112] 다른 사용자의 인보이스 조회 확인(스크립트 미작성)

### #24 로그인 후 헤더의 [Sign in] 링크 미노출이 스펙에 정의되지 않음
- 발생 배경: 2026-10-09 `/tc-write` 시범(UI 로그인 TC 2개) 중 UI_41* 작성에서 발견. 분석 파일 `ui-login-logout.md` 후보 A-4에 올라 있던 항목이다.
- 추정 원인과 근거: 스펙 `User Login` AC2(로그인 성공 시 역할별 이동)는 로그인 후 헤더 상태를 정의하지 않는다. 라이브 동작은 TC-Writer가 확인했다.
- 분류와 상태: 안건(유형 E 스펙 미정의) / 사용자 판단 대기. 사용자가 기대결과와 Note를 라이브 동작으로 두는 것을 승인했다(2026-10-09) / 발견 2026-10-09, 마지막 확인 2026-10-09 라이브
- 대상 TC
  1. [UI_41] 로그인 후 헤더 [Sign in] 링크 미노출 확인
     - 스펙: 로그인 후 헤더 상태를 정의하지 않는다.
     - 라이브: 로그인 후 헤더에 [Sign in] 링크가 노출되지 않는다.
     - 현재 테스트: 시트 기대결과대로 통과 (2026-10-10)

### #28 UI 스펙 미정의 동작을 라이브 기준으로 TC에 씀
- 발생 배경: 2026-10-10 결과 보고서 형식 정리 중 분류. 시트 Note에 "확인 필요"로 표시된 UI TC다.
- 추정 원인과 근거: 스펙이 해당 동작이나 문구를 정의하지 않았다. 불일치가 아니다.
- 분류와 상태: 안건(유형 E) / 전체 실행에서 제외(`spec_undefined` 마커, 2026-10-10 사용자 결정), 결과 보고서에 N/A로 표기 / 발견 2026-10-10, 마지막 확인 2026-10-10
- 대상 TC
  1. [UI_02] 이메일/비밀번호 공란 로그인 시 필수값 에러 확인
     - 스펙: 필수값 에러 문구를 정의하지 않는다.
  2. [UI_06] 비밀번호 1자 또는 200자 입력 시 에러 메시지 노출 확인
     - 스펙: 비밀번호 길이 기준과 문구를 정의하지 않는다.
  3. [UI_21] 수량 입력란 값 삭제 시 1로 보정 확인
  4. [UI_32] 장바구니 상품 전체 삭제 시 [Proceed to checkout] 버튼 미노출 확인
  5. [UI_39] 로그아웃 후 헤더 [Sign in] 링크 노출 확인
  6. [UI_41] 로그인 후 헤더 [Sign in] 링크 미노출 확인 (#24와 같은 항목)
     - 스펙: 3~6번 동작을 정의하지 않는다. 시트는 라이브 동작을 기대결과로 쓴다.

