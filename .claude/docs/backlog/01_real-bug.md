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

### #25 결제 완료 후 장바구니 페이지가 빈 화면으로 노출
- 발생 배경: UI_37 스크립트 작성 중 발견(2026-10-10).
- 추정 원인과 근거: 결제 후 `cart_id`가 없는 상태에서 장바구니 화면이 `null` 응답의 `cart_items`를 읽다 예외가 나 렌더링이 멈추는 것으로 추정한다. 근거는 결제 없이 `cart_id`를 지운 상태에서 콘솔 `TypeError: Cannot read properties of null (reading 'cart_items')` 재현(2026-10-10). 소스는 확인하지 않았다.
- 분류와 상태: real-bug(유형 A) / 중요도 Low / 테스트 내부에서 `pytest.xfail("백로그 #25")`로 pin / 발견 2026-10-10, 마지막 확인 2026-10-10 라이브
- 대상 TC
  1. [UI_37] 결제 완료 후 장바구니 비워짐 확인
     - 스펙: `v5` Checkout Cart AC4는 빈 장바구니에서 "Your shopping cart is empty"를 표시한다. Payment AC9의 "the cart is cleared"는 충족된다(헤더 장바구니 아이콘 사라짐).
     - 라이브: `/checkout` 진입 시 장바구니 영역(`app-cart`)이 비어 있고 문구가 없다.
     - 현재 테스트: 문구 확인 단계만 `pytest.xfail`로 pin. 문구가 #15의 라이브 문구로 나오면 #15로 xfail한다.

### #26 상품 검색의 일치 기준이 스펙에 없고 검색어 길이에 따라 결과가 다름
- 발생 배경: UI_13 스크립트 작성 중 발견(2026-10-10). "hammer" 검색 결과에 상품명에 hammer가 들어간 "Sledgehammer"가 빠졌다.
- 추정 원인과 근거: sprint5 `ProductService::searchProducts`가 4자 이상은 FULLTEXT 단어 시작 일치(`+term*`), 3자 이하는 `LIKE %term%`를 쓰는 것으로 보인다(소스는 원인 추정 근거로만 씀). 라이브 확인(2026-10-10): "hammer" 6건(Sledgehammer 없음), "ham" 7건(Sledgehammer 포함), "ammer" 0건.
- 분류와 상태: real-bug(유형 E 스펙 미정의에서 전환) / 중요도 Low / 사용자 판단(2026-10-10): 스펙에 기준이 없어도 기능 의도상 기대결과와 실제결과가 달라 real-bug로 판단 / Jira QA-7 등록(2026-10-10) / 발견 2026-10-10, 마지막 확인 2026-10-10 전체 실행(UI_13 실패로 재현)
- 대상 TC
  1. [UI_13] 상품 검색 시 검색어 포함 상품 결과 노출 확인
     - 스펙: `v5` Product Overview AC4는 "only matching products"라고만 쓰고 일치 기준(부분 일치, 단어 시작 일치)과 검색 대상 필드를 정의하지 않는다.
     - 라이브: 4자 이상 검색어는 단어 시작 일치라 "Sledgehammer"가 "hammer" 결과에서 빠진다.
     - 현재 테스트: 3-1(누락 없이 노출)에서 실패. real-bug로 바뀌어 strict xfail 고정 대상이 될 수 있다(미적용).
