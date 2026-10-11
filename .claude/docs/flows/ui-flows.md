# UI 흐름 지도
`/flow-map`이 쓰고, TC-Writer가 UI TC의 스텝과 사전 조건을 이 지도와 대조한다. 실제 화면에서 확인한 것만 쓴다. 계정은 UI 테스트 계정(customer2)이다.

## 화면 목록
- 메인 (`/`)
- 상품 상세 (`/product/<id>`), 품절 상품 상세
- 로그인 (`/auth/login`)
- 내 계정 (`/account`), 사용자 메뉴
- 체크아웃 (`/checkout`): 1단계 장바구니 → 2단계 Sign in → 3단계 Billing Address → 4단계 Payment. 네 단계가 모두 같은 URL이다.

## 핵심 흐름
- 비로그인: 메인 → 상품 상세 [Add to cart] → 헤더 장바구니 아이콘 → 장바구니 [Proceed to checkout] → Sign in 단계에서 로그인 폼 → (로그인 후) Billing Address → Payment
- 로그인: 메인 → 상품 상세 [Add to cart] → 헤더 장바구니 아이콘 → 장바구니 [Proceed to checkout] → Sign in 단계 [Proceed to checkout] → Billing Address [Proceed to checkout] → Payment [Check payment]
- 헤더 장바구니 아이콘은 장바구니에 상품이 있을 때만 보인다. 빈 장바구니로 체크아웃에 들어가려면 URL(`/checkout`)로 직접 가야 한다.

## 메인 (/) — 확인 2026-10-10
- 진입 경로: 헤더 [Home], 로그아웃 직후
- 상태 조건
  - 비로그인: 헤더에 [Sign in]
  - 로그인: 헤더에 사용자명 메뉴(ex: Jack Howe), [Sign in] 없음
  - 장바구니가 비어 있으면 헤더 장바구니 아이콘이 없다. 상품이 있으면 아이콘과 수량 배지가 보인다.
- 주요 요소
  - 헤더: [Home], [Categories], [Contact], [Sign in] 또는 사용자명, 언어 [EN]
  - 왼쪽: Sort 드롭다운(Name (A - Z) 등), Price Range, Search 입력과 [Search], [X](검색 초기화), 카테고리·브랜드 필터, Eco-friendly 필터
  - 상품 카드: 이름, 가격, [Compare], 품절이면 "Out of stock"
  - 페이지 이동: [«], [»], 페이지 번호
- 다음 화면: 상품 카드 → 상품 상세 / 장바구니 아이콘 → 체크아웃 1단계 / [Sign in] → 로그인
- 정렬 드롭다운 옵션(6개): Name (A - Z), Name (Z - A), Price (High - Low), Price (Low - High), CO₂ Rating (A - E), CO₂ Rating (E - A)
- Price Range 슬라이더: 범위 표시 0~200, 기본 선택 1~100
- 상품 카드에 CO₂ 등급 배지(A~E), 친환경 상품은 "ECO" 배지가 붙는다. Eco-friendly 필터를 켜면 ECO 배지 상품만 남는다(2026-10-11 확인).
- [»]를 누르면 다음 페이지 상품이 같은 URL(`/`)에서 바뀐다.
- 검색(2026-10-11 확인)
  - 결과 없음: "Searched for: <검색어>", "0 products found for '<검색어>'", "There are no products found." 문구, 상품 카드 없음
  - 2자 입력 후 [Search]: 검색이 실행되지 않고 이전 결과가 그대로 남는다(스펙 AC4는 3~40자).
  - [X]: 검색어가 지워지고 전체 목록으로 돌아간다.
- [Compare]: 누르면 하단에 비교 바("1 product(s) selected", [Clear All], [Compare Now])가 나타난다.
- 미확인: 브랜드 필터와 카테고리 필터 조합 결과의 세부, 비교 화면([Compare Now] 이후)

## 카테고리 페이지 (/category/<slug>) — 확인 2026-10-11
- 진입 경로: 헤더 [Categories] 메뉴 → [Hand Tools], [Power Tools], [Other], [Special Tools]
- 주요 요소: 제목 "Category: <카테고리명>", 정렬, 하위 카테고리 필터(ex: Hand Tools → Hammer, Hand Saw, Wrench, Screwdriver, Pliers, Chisels, Measures), 브랜드 필터, "Sustainability:" Eco-Friendly 필터, 상품 카드, 페이지 이동. 메인과 달리 검색과 Price Range는 없다.
- 헤더 [Categories] 메뉴 항목: Hand Tools, Power Tools, Other, Special Tools, Rentals, 그리고 언어(DE, EL, EN, ES, FR, NL, TR)
- 미확인: 하위 카테고리 체크 결과

## Rentals (/rentals) — 확인 2026-10-11
- 진입 경로: 헤더 [Categories] → [Rentals]
- 주요 요소: 제목 "Rentals", 렌탈 상품 3개(Excavator, Bulldozer, Crane)와 설명
- 미확인: 렌탈 상품 상세로 가는 링크와 상세 화면(카드 링크를 찾지 못함), Rental duration slider

## 상품 상세 (/product/<id>) — 확인 2026-10-10
- 진입 경로: 메인 또는 카테고리 목록의 상품 카드, 상세 하단 "Related products"
- 상태 조건
  - 재고 있음: 수량 [-] 입력 [+], [Add to cart] 활성
  - 품절: 수량 [-]·입력·[+]와 [Add to cart]가 모두 비활성, "Out of stock" 문구
- 주요 요소: 상품명, 가격, 설명, [Add to cart], [Add to favourites], [Compare], "Specifications" 표, "Related products"
- 다음 화면: [Add to cart] → 같은 화면 유지, 토스트 "Product added to shopping cart.", 헤더 장바구니 아이콘과 수량 배지 나타남
- 분기: 비로그인에서 [Add to favourites]를 누르면 "Unauthorized, can not add product to your favorite list." 알림이 나온다(2026-10-11 확인). 로그인 상태 결과는 미확인.
- 수량 입력: "0"을 입력하고 밖을 누르면 "1"로 바뀐다. 숫자 입력란(type=number)이라 문자는 입력되지 않는다(2026-10-11 확인).
- 같은 상품을 [Add to cart]로 두 번 담으면 헤더 장바구니 배지가 2가 된다(2026-10-11 확인).
- 미확인: 로그인 상태 [Add to favourites], Related products 카드 이동

## 로그인 (/auth/login) — 확인 2026-10-10
- 진입 경로: 헤더 [Sign in], 직접 URL
- 주요 요소: 제목 "Login", [Sign in with Google], 필드 [Email address], [Password](보기 토글 버튼 있음), [Login], 링크 [Register your account], [Forgot your Password?]
- 다음 화면: 로그인 성공 → 내 계정(`/account`)
- 빈 값으로 [Login]: 필드 아래 "Email is required", "Password is required"가 나오고 요청은 보내지 않는다(2026-10-11 확인).
- [Forgot your Password?] → `/auth/forgot-password`: 제목 "Forgot Password", 필드 [Email address], 버튼 [Set New Password]
- [Register your account] → `/auth/register`: 제목 "Customer registration"(회원가입은 범위 밖)
- 미확인: 잘못된 계정 정보 로그인 실패 메시지(계정 잠금 방지로 탐색 중 시도하지 않음)

## 내 계정 (/account)와 사용자 메뉴 — 확인 2026-10-10
- 진입 경로: 로그인 성공 직후, 사용자 메뉴 [My account]
- 주요 요소: 헤더 사용자명 메뉴(ex: Jack Howe). 누르면 [My account], [My favorites], [My profile], [My invoices], [My messages], [Sign out]
- 다음 화면: [Sign out] → 메인(비로그인)
- 분기: 장바구니(`/checkout`) 화면에서 [Sign out]을 누르면 메인으로 이동하지 않고 같은 화면에 머문다(2026-10-11 확인). 메인과 내 계정 화면에서는 메인으로 이동한다.
- 분기: 로그아웃해도 장바구니는 남는다(헤더 장바구니 아이콘 수량 1 유지). 브라우저 저장소 기반으로 추정되며 서버 장바구니와의 관계는 미확인.
- 미확인: 각 메뉴 하위 화면

## 체크아웃 1단계 장바구니 (/checkout) — 확인 2026-10-10
- 진입 경로: 헤더 장바구니 아이콘(상품이 있을 때만 보임), 직접 URL
- 상태 조건
  - 상품 있음: 상품 행(상품명, 수량 입력, 가격, 행 합계, 삭제 [X]), 합계, [Continue Shopping], [Proceed to checkout]
  - 비어 있음(직접 URL 진입 또는 마지막 상품 삭제 후): 본문에 장바구니 표·안내 문구·버튼이 없고 헤더 장바구니 아이콘도 사라진다. "Your shopping cart is empty" 같은 문구는 보이지 않았다(백로그 #15).
- 주요 요소: 마지막 상품 삭제 시 토스트 "Product deleted."
- 다음 화면: [Proceed to checkout] → 2단계 Sign in / [Continue Shopping] → 메인
- 수량 입력: "0"이나 "-3"을 입력하고 Tab을 누르면 "Product quantity updated." 토스트와 함께 수량이 "1"로 바뀐다(2026-10-11 확인).
- 분기: 로그인 여부와 상관없이 1단계 화면은 같다.

## 체크아웃 2단계 Sign in (/checkout) — 확인 2026-10-10
- 진입 경로: 1단계 [Proceed to checkout]
- 상태 조건
  - 비로그인: 제목 "Login"과 로그인 폼(필드 [Email address], [Password], [Login], [Register your account], [Forgot your Password?])
  - 로그인: 로그인 폼 없이 [Proceed to checkout] 버튼만 있다.
- 다음 화면: 로그인 상태 [Proceed to checkout] → 3단계 Billing Address
- 분기: TC가 "Sign in" 단계를 거친다고 쓸 때, 로그인 상태면 이 단계에서 [Proceed to checkout]을 한 번 더 눌러야 한다.
- 미확인: 비로그인 상태에서 이 폼으로 로그인한 뒤 바로 3단계로 넘어가는지

## 체크아웃 3단계 Billing Address (/checkout) — 확인 2026-10-10
- 진입 경로: 2단계(로그인 상태) [Proceed to checkout]
- 상태 조건: 처음 들어오면 Street, City가 계정 주소로 미리 채워져 있고 Country, Postcode, House number, State는 비어 있어 [Proceed to checkout]이 비활성이다.
- 주요 요소: 제목 "Billing Address", 필드 [Country](드롭다운, "Your country *"), [Postcode](placeholder "Your Postcode *"), [House number](placeholder "e.g. 42 *"), [Street], [City], [State](placeholder "State *"), 우편번호 조회 안내 문구("Enter country, postal code ..."), [Proceed to checkout]
- 다음 화면: 필수값을 모두 채우면 [Proceed to checkout] 활성 → 4단계 Payment
- 분기: Country, Postcode, House number를 입력하면 우편번호 조회가 돌아 Street, City, State를 다른 값으로 덮어썼다(ex: Korea + 12345 + 123 입력 시 미리 채워진 Street, City가 바뀌고 State가 채워짐). 직접 입력한 값이 유지된다고 가정한 스텝은 주의한다.
- 미확인: 우편번호 조회 결과의 규칙, 필드별 에러 문구

## 체크아웃 4단계 Payment (/checkout) — 확인 2026-10-10
- 진입 경로: 3단계 [Proceed to checkout]
- 상태 조건: 결제 방법에 따라 추가 입력 필드와 [Check payment] 활성 여부가 달라진다.
  - Cash on Delivery: 추가 필드 없음, [Check payment] 활성
  - Bank Transfer: [Bank Name], [Account Name], [Account Number], 비어 있으면 [Check payment] 비활성
  - Credit Card: [Credit Card Number], [Expiration Date], [CVV], [Card Holder Name]. 비어 있어도 [Check payment]가 활성이었다(스펙 대조 필요, 후보).
  - Buy Now Pay Later: [Monthly Installments] 드롭다운("Choose your monthly installments"), 선택 전 [Check payment] 비활성
  - Gift Card: [Gift Card Number], [Validation Code], 비어 있으면 [Check payment] 비활성
- 주요 요소: 상단 단계 표시 "CART 1 / SIGN IN 2 / BILLING ADDRESS 3 / PAYMENT 4", 제목 "Payment", 결제 방법 드롭다운("Choose your payment method"), [Check payment]
- 다음 화면
  - [Check payment] → 같은 화면에 "Payment was successful" 문구가 나오고, 같은 버튼이 [Confirm]으로 바뀐다.
  - [Confirm] → 결제 완료 화면
- 분기: 결제 확정은 [Check payment]와 [Confirm] 두 번 클릭이다.
- 미확인: 결제 방법별 입력값 검증 문구, Cash on Delivery 외 결제 방법의 확정 결과

## 결제 완료 (/checkout) — 확인 2026-10-10
- 진입 경로: 4단계 [Confirm]
- 주요 요소: 문구 "Thanks for your order! Your invoice number is INV-<번호>." (번호는 매번 다르다)
- 상태 조건: 헤더 장바구니 아이콘이 사라진다. 이후 `/checkout`에 직접 들어가면 빈 장바구니 화면(본문 없음)이다.
- 다음 화면: 헤더 메뉴로만 이동한다. 완료 화면에 다른 버튼은 없다.
- 미확인: 사용자 메뉴 [My invoices]에서 새 인보이스 확인
