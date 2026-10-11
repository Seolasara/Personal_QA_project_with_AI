# UI 분석: 결제

> 개요, 판단 기준, 우선순위별 리스크 목록: [00_ui-overview.md](00_ui-overview.md)

## 1. 기능 목적
| 기능 | 목적 |
|---|---|
| 결제 | 4단계 위저드(Cart, Sign in, Billing Address, Payment)에서 결제 수단별로 입력한 뒤 Confirm으로 주문을 확정합니다. |

## 2. 핵심 흐름
1. Sign in 단계
   - 비로그인이면 로그인 폼을 표시합니다. (게스트 폼은 소스 전용 기능이라 제외)
   - 로그인 상태면 "already logged in" 메시지 → Proceed
2. Billing Address 단계
   - 입력: Country, Postal code, House number, Street, City, State (필수값 미입력 시 Proceed 비활성)
   - 우편번호 자동조회가 비동기로 street, city, state를 채웁니다.
3. Payment 단계
   - 결제 수단 선택: Bank Transfer, Cash on Delivery, Credit Card, Buy Now Pay Later, Gift Card
   - 수단별 필드 입력 → Confirm
   - 성공 메시지(`payment-success-message`)와 인보이스 번호가 표시되고 장바구니가 비워집니다.

## 3. 리스크
- **R1** 결제 Confirm 첫 클릭 race
  - `checkPayment()`가 비동기 검증 완료 전에 `of(this.state)`(undefined)를 반환해 첫 클릭이 무반응일 수 있습니다.
  - real-bug 후보이며, 이 파일에서는 수정하지 않고 보고만 합니다.
  - 근거: `payment.component.ts` `checkPayment`, `playwright-demo/CLAUDE.md` 기술부채 항목
- **R4** [불일치] Billing Address 필드
  - 스펙: Street, City, State, Country, Postal code 5개
  - 소스: House number(필수, max 10)가 추가됨
  - 근거: v5.md Billing AC1 vs `address.component.ts`, `data-test="house_number"`
  - 판단: 스펙 기준 5개 필드로 작성합니다.
- **R5** Billing Address 자동채움과 우편번호 조회 race
  - 조회 응답이 사용자 입력을 덮어쓸 수 있습니다.
  - 한국 등 일부 국가는 조회 실패 메시지가 노출됩니다.
  - 근거: `address.component.ts` postcodeService.lookup, 자동화 코드의 `networkidle` 우회
- **R7** [불일치] 신용카드 검증
  - 스펙: 카드 필드 표시를 명시합니다.
  - 소스: 필수(required) 검증이 없고 패턴만 있습니다. (빈 값도 통과할 가능성)
  - 근거: `payment.component.ts` `updateValidation` credit-card case
  - Confirm 활성화와 서버 검증 동작은 라이브 확인이 필요합니다.
  - 판단: 스펙에 필수 검증 규정이 없으면 기대결과는 '확인 필요'로 씁니다.
- **R8** [불일치] Gift Card 형식
  - 스펙: "alphanumeric"
  - 소스: 카드번호 16자, 검증코드 4자 고정
  - 근거: `payment.component.ts` 정규식 `{16}`, `{4}`
  - 판단: 스펙은 'alphanumeric'만 있어 길이 검증 TC의 기대결과는 '확인 필요'로 씁니다.

## 4. 테스트 범위 (포함)
- 결제: Sign in 단계, Billing Address 필수값/비활성, 결제 수단별 필드 노출, Cash on Delivery 해피패스, Confirm 성공 메시지, 필드 검증 에러

## 5. TC 작성 입력값 (후보)
**F. 결제**
- 후보 F-1: Billing Address 필수값 미입력(각 필드 1개씩 공란) → 필드 invalid, Proceed(`proceed-3`) 비활성
- 후보 F-2: 필드 길이 경계 (street 70/71, city/state 40/41, postal_code 10/11)
- 후보 F-3: 로그인 사용자 주소 자동채움 확인 (스펙 기준 Billing 필드는 5개, House number는 소스에만 필수 — R4)
- 후보 F-4: 결제 수단 드롭다운 5종 노출과 수단별 필드 노출
  - Bank Transfer: bank_name, account_name, account_number
  - Credit Card: credit_card_number, expiration_date, cvv, card_holder_name
  - Buy Now Pay Later: monthly_installments (3, 6, 9, 12)
  - Gift Card: gift_card_number, validation_code
  - Cash on Delivery: 추가 필드 없음
- 후보 F-5: 수단 변경 시 폼 초기화
- 후보 F-6: Bank Transfer 해피패스와 검증 에러
  - 해피패스 예: bank `Test Bank`, account name `Jane Doe`, number `12345678`
  - 검증 에러 예: 숫자가 아닌 계좌번호, 특수문자 은행명
- 후보 F-7: Credit Card 검증
  - 카드번호 형식: `1111-2222-3333-4444`
  - 만료일 `MM/YYYY` 과거 → "Expiration date must be in the future."
  - CVV 3~4자리
  - 카드 소유자: 영문과 공백
- 후보 F-8: Gift Card 형식 (16자 영숫자 + 4자 코드), Buy Now Pay Later 해피패스
- 후보 F-9: Confirm 후 성공 메시지와 인보이스 번호 표시, 장바구니 비워짐
- 후보 F-10: Confirm 첫 클릭 무반응 재현 여부 (R1, real-bug 후보 확인용 관찰 TC)
- (제외) 후보 F-11: 비로그인 상태 결제 진입 시 Sign in/게스트 폼 — 게스트 체크아웃은 소스에만 있는 기능이라 제외합니다.
- 참고: F-4~F-8의 필드 이름, 형식, 검증 문구는 소스에서 가져온 값입니다. 스펙에 규정이 없으면 TC 기대결과는 '확인 필요'로 씁니다.
