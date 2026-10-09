# 백로그: real-bug
Jira로 올릴 실제 결함. 등록 뒤에도 수정될 때까지 여기 둔다. 작성 형식은 `.claude/guides/backlog-format.md`를 따른다.

### #13 존재하지 않는 상품의 연관 상품 조회가 500
- 발생 배경: API-TC 작성 중 라이브 확인.
- 추정 원인과 근거: 연관 상품 조회에서 상품 존재 여부를 확인하지 않고 처리하다 예외가 나는 것으로 추정한다. 소스는 확인하지 않았다.
- 분류와 상태: real-bug(유형 A) / Jira QA-4 등록(2026-10-07) / 발견 2026-10-05, 마지막 확인 2026-10-08 라이브
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
     - 현재 테스트: 스크립트 작성 전
