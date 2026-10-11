# UI 분석: 장바구니

> 개요, 판단 기준, 우선순위별 리스크 목록: [00_ui-overview.md](00_ui-overview.md)

## 1. 기능 목적
| 기능 | 목적 |
|---|---|
| 장바구니 | 담긴 상품을 확인하고 수량 변경, 삭제, 합계 재계산을 합니다. |

## 2. 핵심 흐름
1. 장바구니(`/checkout`)
   - 행(Item, Quantity, Price, Total, Actions) 확인
   - 수량 변경(토스트 "Product quantity updated.") 또는 삭제
   - 합계 재계산 → Proceed to checkout

## 3. 리스크
- **R9** [불일치] 빈 장바구니 문구
  - 스펙: "Your shopping cart is empty"
  - 소스 i18n: "The cart is empty. Nothing to display."
  - 근거: v5.md Checkout Cart AC4 vs `en.json` `pages.checkout.cart.empty`
  - 판단: 문구는 스펙 기준으로 작성합니다.
- **R11** 장바구니 삭제 버튼에 `data-test`가 없습니다.
  - `a.btn.btn-danger`에 의존하므로 셀렉터 드리프트 위험이 있습니다.
  - 근거: `playwright-demo/CLAUDE.md` 기술부채
- R3(수량 상한)은 [ui-product-detail.md](ui-product-detail.md)를 참고합니다. 장바구니 수량 변경에도 같은 상한이 적용됩니다.

## 4. 테스트 범위 (포함)
- 장바구니: 행/합계 표시, 수량 변경과 재계산, 삭제, 빈 장바구니

## 5. TC 작성 입력값 (후보)
**E. 장바구니**
- 후보 E-1: 수량 변경(예: 1 → 3) → "Product quantity updated." 토스트, 행 합계 = 단가 x 수량, 카트 합계 갱신
- 후보 E-2: 수량 0/공란 입력 → 1로 보정, 상한 초과 입력 → 스펙 기준 999,999,999로 clamp (소스는 99 + 경고, R3)
- 후보 E-3: 상품 삭제 → 행 제거, 합계 재계산, 마지막 상품 삭제 시 빈 장바구니 문구 (문구는 스펙 기준 "Your shopping cart is empty", R9)
- 후보 E-4: 2종 이상 상품 합계 = 행 합계의 합
  - 소스에는 5% Eco 할인이 있어 합계가 달라질 수 있습니다.
  - Eco 할인은 범위 제외이므로 CO2 A/B 비율이 50% 이하가 되는 상품 조합으로 작성합니다.
- 후보 E-5: Continue shopping → 홈 이동
- 후보 E-6: 장바구니가 비었을 때 Proceed 버튼 비노출
