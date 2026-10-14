# UI 분석 개요 (메인 문서)

> 이 파일이 UI 분석의 메인입니다. 기능별 상세는 "2. 기능별 분석 파일"에서 엽니다.

## 1. 분석 개요
- 작성일: 2026-10-05 (최근 변경분 반영: 2026-10-14)
- 분석 기준
  - 서비스 레포 기준 커밋: `ae7caec` (2026-10-11, 2026-10-14 변경분 분석 시점의 HEAD). 최초 분석은 `c752a70`(2026-10-04, 추정) 기준이었습니다.
  - 분석일: 2026-10-14
  - 감시 경로: `docs/user-stories/`, `docs/features.md`, `sprint5/UI/src/app/`, `sprint5/UI/src/assets/i18n/en.json`
- 대상: https://practicesoftwaretesting.com (Toolshop v5.0)
- 근거 자료
  - 레포: testsmith-io/practice-software-testing (clone)
    - `docs/user-stories/v5.md`
    - `docs/features.md`
    - `sprint5/UI/src/app/**` (Angular 소스)
    - `sprint5/UI/src/assets/i18n/en.json`
  - 사이트: WebFetch 결과 SPA라 title("Practice Software Testing - Toolshop - v5.0")만 확인되고 본문은 비어 있습니다. (동적 렌더링) 화면 구성은 레포 소스로 대체했습니다.
- 주의: 라이브 사이트 동작과 레포 소스(sprint5)가 다를 수 있습니다. 리스크 표의 [불일치] 항목은 실제 사이트에서 재확인이 필요합니다.
- 판단 기준 (2026-10-04 사용자 결정)
  - 기대 동작은 항상 스펙(`docs/user-stories/v5.md`) 기준입니다. 소스와 달라도 스펙을 따릅니다.
  - 스펙에 규정이 없는 값은 '확인 필요'로 씁니다.
  - 소스에만 있는 기능은 이번 범위에서 제외합니다.
    - Eco 필터와 배지
    - CO2 정렬
    - 5% Eco 할인
    - 게스트 체크아웃
    - 상품 비교 바

## 2. 기능별 분석 파일
| 기능 | 파일 | TC 후보 수 | 비고 |
|---|---|---|---|
| 로그인 | [ui-login-logout.md](ui-login-logout.md) | 4 | 잠김 검증은 전용 계정 필요 |
| 로그아웃 | [ui-login-logout.md](ui-login-logout.md) | 2 | |
| 상품 조회·검색·필터 | [ui-product-browse.md](ui-product-browse.md) | 10 | 정렬, 검색, 가격, 페이지네이션 |
| 상품 상세(수량) | [ui-product-detail.md](ui-product-detail.md) | 7 | 수량 상한은 스펙 기준 |
| 장바구니 | [ui-cart.md](ui-cart.md) | 6 | 수량 변경, 삭제, 합계 |
| 결제 | [ui-payment.md](ui-payment.md) | 10 | 게스트 체크아웃은 제외 |

## 3. 리스크 목록 (우선순위 높은 순)
- 우선순위 기준: 분석과 테스트 결과를 틀어지게 할 가능성과 영향 범위를 함께 본 분석 시점의 판단입니다.
- 번호(R1~R12)는 우선순위 순입니다. 기능 파일의 리스크도 같은 번호를 쓰며, 근거와 판단 상세는 해당 기능 파일에 있습니다.

| ID | 우선순위 | 리스크 | 예상 영향 범위 | 상세 |
|---|---|---|---|---|
| R1 | 높음 | 결제 Confirm 첫 클릭이 무반응일 수 있음 (비동기 검증 완료 전 반환). real-bug 후보 | 결제 확정 흐름. 주문 완료에 의존하는 모든 흐름이 간헐 실패 | [ui-payment.md](ui-payment.md) |
| R2 | 높음 | 공개 공용 데모 계정, 데이터 매시간 초기화. 3회 연속 실패 시 계정 잠김(423) | 로그인, 장바구니, 주문 상태 전반. 잠김 검증을 공용 계정에 하면 다른 테스트가 같이 실패 | [ui-login-logout.md](ui-login-logout.md) |
| R3 | 높음 | [불일치] 수량 상한: 스펙 1~999,999,999 vs 소스 99 + 경고 토스트 | 상품 상세와 장바구니의 수량 입력·보정 | [ui-product-detail.md](ui-product-detail.md) |
| R4 | 중간 | [불일치] Billing 필드: 스펙 5개 vs 소스에 House number(필수) 추가 | 결제 Billing 단계. 필수값 때문에 Proceed가 스펙과 다르게 막힐 수 있음 | [ui-payment.md](ui-payment.md) |
| R5 | 중간 | 우편번호 조회 응답이 사용자 입력을 덮어씀. 일부 국가는 조회 실패 메시지 | 결제 Billing 입력 후 값 검증 | [ui-payment.md](ui-payment.md) |
| R6 | 중간 | 위치 기반 할인: 브라우저 지리 위치에 따라 가격이 달라짐 | 가격·합계가 나오는 모든 화면(조회, 상세, 장바구니, 결제) | 아래 "공통 리스크" |
| R7 | 중간 | [불일치] 신용카드 검증: 스펙은 필드 표시만 명시, 소스는 필수 검증 없음 | 결제 Credit Card 수단의 오류·Confirm 동작 | [ui-payment.md](ui-payment.md) |
| R8 | 중간 | [불일치] Gift Card 형식: 스펙 alphanumeric vs 소스 16자/4자 고정 | 결제 Gift Card 수단의 길이 검증 | [ui-payment.md](ui-payment.md) |
| R9 | 낮음 | [불일치] 빈 장바구니 문구: 스펙과 소스 i18n 문구가 다름 | 장바구니 빈 상태 화면 | [ui-cart.md](ui-cart.md) |
| R10 | 낮음 | 검색 시 기존 필터와 슬라이더 값이 초기화됨 | 상품 조회의 검색 후 목록 확인 | [ui-product-browse.md](ui-product-browse.md) |
| R11 | 낮음 | 장바구니 삭제 버튼에 `data-test`가 없음 | 장바구니 삭제 동작 확인(셀렉터) | [ui-cart.md](ui-cart.md) |
| R12 | 낮음 | 강좌 홍보 배너(`course-promo`)가 production 빌드에서만 홈 상단과 결제 완료 화면에 추가됨. 같은 `data-test`가 두 화면에 있고 외부 링크(새 탭)를 포함 | 홈 상단 레이아웃(상품 그리드 위치), 결제 완료 화면의 `order-confirmation` 주변, 텍스트·링크 셀렉터 | [ui-payment.md](ui-payment.md), [ui-product-browse.md](ui-product-browse.md) |

### 공통 리스크
- **R2** 공유 데모 계정과 데이터
  - 공개 공용 계정이고 데이터가 매시간 초기화(privacy 문서)되므로 장바구니와 주문 상태가 오염될 수 있습니다.
  - 근거: v5.md Login AC4, Privacy AC1
- **R6** 위치 기반 할인
  - 브라우저 지리 위치에 따라 가격이 바뀝니다.
    - New York
    - Mumbai
    - Tokyo
    - Amsterdam
    - London
  - 근거: v5.md Geo-Location Discount AC1

## 4. 제외
- 제외 대상
  - 회원가입, 비밀번호 찾기/변경, 프로필, 즐겨찾기, 인보이스, 메시지, 연락 폼, 관리자 기능
  - TOTP/소셜 로그인(Google), 챗 위젯, 다국어, 상품 비교, 렌탈 상품, 위치 할인/콤비네이션 할인
  - 성능, 보안, API 직접 호출 (API는 `api-demo/`에서 별도 관리)
  - 소스에만 있는 기능 (1번의 판단 기준 참고)
- 제외 사유
  - QA 플랜의 Out 범위(회원가입, 관리자, 카드 결제 일부, 다국어, 성능/보안)와 이번 요청 범위(로그인~결제)에 해당하지 않습니다.
  - 카드 결제와 계정 잠김은 공용 데모 환경과 외부 의존 때문에 자동화 위험이 커서 우선순위를 낮췄습니다. 결제 수단별 필드 노출과 검증 에러는 범위를 사용자가 정하도록 남깁니다.
  - TOTP/Google 로그인은 외부 서비스나 시크릿이 필요합니다.

## 5. 확인 못 한 것
- 라이브 사이트 화면
  - SPA 본문이 비어 title만 확인했습니다.
  - 문구, 슬라이더 값, 상품 목록, 정렬 옵션은 레포 소스 기준이며 라이브와 다를 수 있습니다. 브라우저 렌더링 확인이 필요합니다.
- 스펙과 소스 불일치(R3, R4, R7, R8, R9)의 라이브 실제 동작
- 로그인이 필요한 화면
  - 장바구니 로그인 상태, Billing 자동채움, 결제 완료 화면은 로그인하지 않아 직접 확인하지 못했습니다.
- 계정 잠김, 위치 기반 할인, 결제 Confirm race의 실제 재현
  - 테스트 실행 금지 원칙에 따라 실행하지 않았습니다.
- 상품 데이터
  - 품절 상품 존재 여부, 가격 분포, 페이지 수를 확인하지 못했습니다. 데이터 의존 항목의 기대 결과는 확인 후 확정해야 합니다.
