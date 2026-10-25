# 결함 주입 측정 수리 기록 (2026-10-17)
- 대상: `with-bugs-result.md` 6·8번에서 사라가 분류한 UI_82, UI_11, UI_33
- 실행: 운영 사이트 단독 3회. 로컬 Toolshop 1회는 스택이 떠 있지 않아(4200, 8091 연결 거부) 실행하지 못함

### UI_82 — test-bug
- 원인: `PaymentPage.address_heading`이 `get_by_role("heading", name="Billing Address")` 부분 일치라 제목이 "Type Billing Address"로 바뀌어도 통과함
- 수정: `playwright-demo/pages/payment_page.py:PaymentPage.__init__` / `address_heading`에 `exact=True` 추가
- 근거: TC 기대결과 5 "BILLING ADDRESS 페이지 정상 노출", 흐름 지도 3단계 제목 표기 "Billing Address"(확인 2026-10-10)
- 점검: repair_guard 오류 0, 주의 0 / script_lint 오류 0 / 실행 통과 3회/전체 3회
  - 같은 로케이터를 쓰는 테스트 1회 확인: UI_34, 35, 85~91 통과, UI_83(QA-16)과 UI_84(QA-17)는 기존 이슈 어설션에서 실패(제목 확인 단계는 통과). UI_36, 37은 결제 확정이라 실행하지 않음
- 사람 확인 필요: 없음

### UI_11 — test-bug
- 원인: 최댓값을 PageDown 2회(100 → 60)로만 내려, 첫 페이지 상품이 모두 그보다 싸면 범위 밖 상품이 빠지는지 확인하지 못함
- 수정: `playwright-demo/pages/catalog_page.py:CatalogPage.lower_max_price_below` 추가(최댓값이 주어진 가격보다 낮아질 때까지 PageDown, 핸들이 더 안 내려가면 실패), 사용처가 없어진 `lower_max_price` 삭제 / `tests/product_search_test.py:test_product_price_slider_max`가 조정 전 첫 페이지 최고가를 읽고 그보다 낮게 내린 뒤 `moved_max < 조정 전 최고가` 어설션 추가
- 근거: TC 목적 "가격 범위를 줄이면 범위 밖 가격의 상품이 목록에서 빠지는지 확인", 사전 조건 "조정한 가격 범위 내 상품 1건 이상 존재". 기대결과 3 어설션(모든 가격이 범위 안, 목록 비어 있지 않음)은 그대로 유지. 가격 고정값은 쓰지 않음
- 점검: repair_guard 오류 0, 주의 0 / script_lint 오류 0 / 실행 통과 3회/전체 3회(정리 후 파일 단위 1회 추가 통과)
- 사람 확인 필요: 없음

### UI_33 — timing
- 원인: 화면은 postal_code를 `debounceTime(300)` + `distinctUntilChanged`로 보고 조회하므로, 비운 직후 같은 값을 다시 넣으면 조회가 일어나지 않는데 `refill_postcode`가 `/postcode-lookup` 응답을 기다림
- 수정: `playwright-demo/pages/payment_page.py:PaymentPage.refill_postcode` / 조회 응답 대기를 빼고 값만 입력. 테스트는 기존 어설션(기대결과 8 값 노출, 9 버튼 활성)의 자동 대기로 기다림
- 근거: TC 기대결과 8 "[Postcode] 필드에 입력한 값 노출", 9 "활성 상태의 [Proceed to checkout] 버튼 노출". 조회 재실행은 기대결과에 없음. trace 확인(2026-10-17, 사라)
- 점검: repair_guard 오류 0, 주의 0 / script_lint 오류 0 / 실행 통과 2회/전체 3회
  - 실패 1회는 수리한 단계가 아니라 그 앞 스텝 2~4의 `fill_address_by_lookup`에서 `/postcode-lookup` 응답 30초 대기 시간 초과
  - trace와 스크린샷: Billing 진입 후 계정 주소 자동 채움(`getDetails` → `patchValue(customer)`)이 테스트의 Country, Postcode, House number 입력 뒤에 도착해 세 필드를 빈 값으로 덮어씀. Street "Test street 654", City "Frankfurt"만 남고 조회는 일어나지 않음
  - `go_to_address_step`의 `wait_for_load_state("networkidle")`가 0.4ms 만에 반환되어(이미 도달한 상태라 다시 기다리지 않음) 자동 채움을 기다리지 못한 것으로 추정함. 확인 방법: 실패 trace에서 Billing 진입 후 `GET /users/me` 응답 시각과 입력 시각 비교
- 사람 확인 필요: 위 새 실패 원인(분류 전). Billing 진입 공용 단계라 UI_34~37, 85~91에도 같은 위험이 있음

### UI_33, UI_85, UI_90, UI_91 — 계정 주소 자동 채움 덮어쓰기 대응 (2026-10-17)
- 배경: TC 사전 조건에 "3. 프로필에 주소를 등록하지 않은 상태" 추가(사용자 승인). 테스트 계정(customer2)은 주소가 등록되어 있고 계정을 따로 만들 수 없어, 스크립트에서 자동 채움을 비워 사전 조건을 맞춤
- 수정
  - `playwright-demo/pages/payment_page.py:PaymentPage.go_to_address_step_with_autofill_cleared` 추가: Billing 진입 클릭 중 나간 `GET /users/me`를 모아 응답 본문까지 기다리고, 계정 Street(직접 조회한 값)가 [Street] 칸에 반영된 것을 확인한 뒤 Street, City, State, Postcode, House number를 비움. 고정 대기와 주소 고정값 없음
  - `PaymentPage.autofill_fields` 추가. Country는 안내 옵션이 disabled, hidden이라 비울 수 없고 계정 국가도 선택되지 않아(백로그 #31) 제외. 각 TC의 첫 입력이 국가 선택
  - `playwright-demo/tests/payment_test.py:_go_to_address_step`에 `clear_autofill` 인자 추가(기본 False). 네 TC만 `clear_autofill=True`, 비운 칸이 빈 값인지 확인
  - 바꾸지 않은 것: `go_to_address_step`(networkidle), `_go_to_payment_step`(UI_34~37, UI_86~89), UI_84. 직전 수리(`refill_postcode`, `address_heading` exact)와 기존 어설션 유지
- 근거: 서비스 소스 `sprint5/UI/src/app/checkout/address/address.component.ts`의 `setAddress()`가 체크아웃 진입 때와 Billing 진입 때(주소를 아직 못 받았으면) `getDetails()` 응답을 `patchValue` 함. 로컬 probe에서 체크아웃 진입 때 `/users/me` 2건, 운영에서는 Billing 진입 때도 조회가 나감(2026-10-17 확인)
- 점검: script_lint 오류 0 / repair_guard 오류 0, 주의 1(자동 채움 확인 대기 timeout=15000, 운영 지연 대비) / tc_marker_check 오류 5건은 모두 시트 ID의 검수 표시(`UI_33*`, `UI_85*`, `UI_90*`, `UI_91*`, `UI_37*`) 때문이며 마커는 지시대로 유지
- 실행: 운영 3회 4/4 통과, 로컬 1회 4/4 통과. UI_36, UI_37은 로컬 1회 2/2 통과(공유 단계 미변경 확인용, 운영 미실행)
  - 첫 운영 3회도 4/4 통과했으나 `Response.finished()`가 teardown에 asyncio 로그 오류를 남겨 `body()`로 바꾼 뒤 다시 3회 실행함
- 남은 위험(추정): 체크아웃 진입 때 조회 응답이 Billing 진입 때 조회 응답보다 늦게 오면 비운 뒤 다시 채워질 수 있음. 이때는 다음 입력 어설션에서 실패로 드러남. 확인 방법: 실패 trace에서 `/users/me` 응답 순서
- 사람 확인 필요: UI_34~37, UI_86~89(`_go_to_payment_step`)에도 같은 덮어쓰기 위험이 있음. 비우기 대신 "자동 채움 완료 대기"만 넣는 공유 단계 변경안을 보고에 올림(미적용)

### UI_95, UI_96, UI_97, UI_98 — test-bug (원인 태그 `data`, 2026-10-17)
- 원인: 공유 fixture `product_detail`, `guest_product_detail`, `cart_two_items`(와 이를 쓰는 `cart`, `cart_ready`, `guest_cart`, `favorite_ready`)가 "Hammer(또는 Pliers) 카테고리 첫 상품"에 고정되어 있음. 운영에서 Hammer 첫 두 상품과 Pliers 첫 상품이 품절(`in_stock: false`)이라 [Add to cart]가 비활성이 되어 setup에서 막힘(2026-10-17 API 확인)
- 수정
  - `playwright-demo/pages/catalog_page.py:CatalogPage.in_stock_cards`, `open_first_in_stock_product` 추가: 현재 목록(첫 페이지)의 카드 링크 중 `data-test="out-of-stock"` 표시가 없는 첫 상품의 상세로 이동. 재고 있는 상품이 없으면 "사전 조건 불충족(env)" 메시지로 실패(skip 없음)
  - `playwright-demo/conftest.py`: `product_detail`, `guest_product_detail`, `cart_two_items`가 `open_first_product` 대신 `open_first_in_stock_product`를 쓰고, 상세에서 `[Add to cart]` 활성을 사전 조건으로 확인. 카테고리 필터(Hammer, Pliers)와 `cart_two_items`의 서로 다른 2종 조건은 유지. 상품명, 가격 고정값 없음
  - `playwright-demo/tests/add_to_cart_test.py:test_cart_header_icon_and_badge_after_add`(UI_66): 같은 원인(카테고리 첫 상품 직접 진입)이라 `open_first_in_stock_product`로 바꿈. 어설션 변경 없음
- 근거: TC 사전 조건 원문 UI_95 "상품 재고 1개 이상 존재", UI_96 "장바구니 내 상품 1건 이상 존재", UI_97, UI_98 "2. 장바구니에 상품 1건 이상 존재". 특정 상품을 정하지 않음. 품절 카드 표시는 흐름 지도와 기존 `out_of_stock_cards`(2026-10-10 확인)
- 점검: repair_guard 오류 0, 주의 3(이번 변경분: fixture의 사전 조건 확인 `to_be_enabled` 3건, TC 어설션 아님. 나머지 주의 14건은 작업 트리에 이미 있던 다른 변경) / script_lint 오류 0 / tc_marker_check 오류 15건은 모두 시트 ID 검수 표시(`*`) 때문
- 실행
  - UI_95~98 운영 단독: 4회 중 3회 4/4 통과. 1회는 3건이 수정 단계 이전(메인 `goto`, 카테고리 응답, 로그인 이동)에서 시간 초과(env, 사이트 지연), 직후 재실행 통과
  - 영향 범위 운영 1회(UI_17~32, 54~70, 81~98, 101 중 결제 확정 UI_36, 37 제외, 50건): 44 통과, 실패 4는 기존 이슈(UI_22·UI_28 QA-11, UI_31 QA-10, UI_83 QA-16), 오류 2는 env(UI_84 로그인 이동 시간 초과 → 재실행 시 fixture 통과 후 QA-17로 실패, UI_85 담기 후 헤더 [cart] 미노출 → 재실행 통과)
  - 로컬 1회(위 50건 + UI_36, 37): 47 통과, 실패 5는 같은 기존 이슈(QA-10, 11, 16, 17), 오류 2는 UI_25, UI_26의 `cart_ready` teardown(아래)
- 사람 확인 필요
  - TC 4건 모두 시트 ID에 검수 표시(`*`)가 남아 있음. 이번 수리는 TC 내용이 아닌 공유 fixture만 바꿈
  - 별건(이번 수정과 무관, 미수리): 로컬에서 UI_25, UI_26이 `cart_ready` teardown에서 시간 초과로 재현됨(2회). 테스트가 이미 장바구니 화면에서 끝났는데 teardown이 헤더 [cart]를 다시 눌러 장바구니 조회 응답을 기다림(추정). 로컬은 Hammer 첫 상품이 재고 있어 변경 전과 같은 상품을 고르므로 이번 수정의 영향이 아님. 운영 실행에서는 통과. 확인 방법: 로컬 trace에서 teardown 클릭 뒤 `GET /carts/{id}` 요청 유무
  - 남은 위험(추정): 재고 있는 첫 상품이 데이터 변경으로 바뀌면 상품별 제약이 있는 상품(ex: 수량 제한 상품)이 골라질 수 있음
