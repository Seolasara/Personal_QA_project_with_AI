# UI 분석: 상품 조회·검색·필터

> 개요, 판단 기준, 우선순위별 리스크 목록: [00_ui-overview.md](00_ui-overview.md)

## 1. 기능 목적
| 기능 | 목적 |
|---|---|
| 상품 조회·검색·필터 | 페이지네이션 그리드, 키워드 검색(3~40자), 카테고리/브랜드 필터, 정렬, 가격 슬라이더로 상품을 탐색합니다. |

## 2. 핵심 흐름
1. 홈 진입: 타이틀 `Practice Software Testing - Toolshop - v5.0`, 상품 그리드 표시
2. 상품 탐색
   - 카테고리/브랜드 체크박스
   - 정렬: Name A-Z/Z-A, Price High-Low/Low-High
   - 가격 슬라이더: 기본 1~100, 최대 200
   - 검색: 제출 시 필터 초기화
   - 그리드 갱신 후 상품 카드 클릭

## 3. 리스크
- **R10** 검색 시 필터 초기화와 슬라이더 기본값 리셋
  - 검색 후 기존 필터가 남아 있다고 가정하면 오탐이 생깁니다.
  - 근거: v5.md Product Overview AC4, `overview.component.ts` 슬라이더 1/100 리셋

- **R12** 강좌 홍보 배너(`course-promo`) 추가
  - production 빌드에서만 보이므로 로컬과 라이브 화면이 다르고, 두 화면에서 `data-test`가 중복됩니다.
  - 근거: `overview.component.html` (2026-10-14 변경 분석, 라이브 노출은 후보)

## 4. 테스트 범위 (포함)
- 상품 목록: 그리드 표시, 카테고리/브랜드 필터, 필터 조합, 정렬 4종, 가격 슬라이더, 검색(유효/최소 3자 미만/결과 없음), 페이지네이션

## 5. TC 작성 입력값 (후보)
**C. 상품 조회·검색·필터**
- 후보 C-1: 홈 그리드 기본 표시 (카드마다 이미지, 이름, 가격)
- 후보 C-2: 검색 유효 입력 `hammer` → `search-caption`, 결과 카드 이름에 포함, `search-result-count`
- 후보 C-3: 검색 경계값 (2자 `ha`, 3자, 40자, 41자) → 제출 비활성/에러 또는 결과
- 후보 C-4: 검색 결과 없음 `zzzzzz` → `no-results` "There are no products found."
- 후보 C-5: 정렬 4종 (Name A-Z/Z-A, Price Low-High/High-Low) → 첫 페이지 이름/가격 순서 검증
- 후보 C-6: 브랜드 필터, 카테고리+브랜드 조합 (AND)
- 후보 C-7: 가격 슬라이더 (기본 1~100) → 범위 내 가격만 표시
- 후보 C-8: 페이지네이션 2페이지 이동 시 그리드 변경
- 후보 C-9: 필터 해제 시 전체 목록 복귀
- 후보 C-10: 품절 상품 카드의 "Out of stock" 표시
- 참고: 데이터 의존이 큰 항목(C-7, C-10)은 상품 데이터가 바뀔 수 있으므로 TC 입력 시 기대 결과를 상대 조건으로 작성하길 권장합니다.

## 6. 변경 이력

### 2026-10-14 변경 요약 (기준 커밋 c752a70 → ae7caec)
- 변경 내용
  - `sprint5/UI/src/app/products/overview/overview.component.html`, `.ts`: 홈 상단 배너 이미지 아래에 강좌 홍보 배너(`data-test="course-promo"`, 링크 `course-promo-link`)를 추가했습니다. `environment.production`이 true일 때만 렌더링합니다. 같은 파일에 시각적으로 숨긴 `<h1>`(`visually-hidden`)과 배너 이미지의 `width`/`height` 속성도 추가했습니다.
  - `sprint5/UI/src/app/app.component.ts`, `app-routing.module.ts`, `_services/seo.service.ts`(신규), `products/detail/detail.component.ts`: 라우트별 meta description, canonical 링크, `og:url` 설정(SEO). 화면 표시 변화는 없습니다.
  - `sprint5/UI/src/app/chat-widget/chat-widget.component.css`: 폭 420px 이하에서 챗 버튼 위치 조정(챗 위젯은 제외 범위)
  - `sprint5/UI/src/assets/i18n/en.json`: `pages.course-promo.*` 추가
  - 스펙(`docs/user-stories/`, `docs/features.md`) 변경은 없습니다.
- 영향 기능과 영향 범위: 홈(상품 조회) 화면 상단 레이아웃. 홈 타이틀은 기존 로직 그대로입니다.
- 리스크: R12 신규(낮음)
- 사이드이펙트
  - `h1`이 홈에 새로 생겨 `h1` 기반 셀렉터나 getByRole('heading')을 쓰는 스크립트가 영향을 받을 수 있습니다(후보, 스크립트에서 확인).
  - 배너 높이만큼 상품 그리드가 아래로 밀립니다. 뷰포트 기준 클릭·스크롤 동작이 달라질 수 있습니다(후보).
  - 상품 상세는 `updateTitle`에서 description 메타만 추가되어 표시에 영향이 없습니다.
  - 결제 완료 화면과 `data-test="course-promo"`가 중복됩니다([ui-payment.md](ui-payment.md)).
- 확인 필요
  - 라이브 홈에서 배너 노출 여부와 그리드가 밀리는 정도: 홈 화면 직접 확인
  - 라이브 `<head>`의 meta description, canonical 반영: 페이지 소스 확인(스펙에 규정이 없어 TC 대상은 아님)
- TC-Writer 후속
  - 기존 C-1(홈 그리드 기본 표시)은 기대결과를 바꾸지 않습니다. 배너는 검증 대상이 아닙니다.
  - 스크립트 쪽에서 홈 화면의 `h1`, 첫 화면 위치(뷰포트) 의존 여부를 점검하도록 Script-Writer에 알립니다.
