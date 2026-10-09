# API 분석: Category

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Category |
| 목적 | 상품 카테고리 목록, 트리(하위 카테고리 포함), 단건, 검색을 조회합니다 |
| 사용처 | 상품 목록 필터(`by_category`), 화면의 카테고리 메뉴 |
| 스펙 근거 | `GET /categories`, `GET /categories/tree`, `GET /categories/tree/{categoryId}`, `GET /categories/search` |

## 2. 핵심 흐름

1. `GET /categories/tree`로 전체 카테고리 트리를 받습니다.
2. 필요하면 `by_category_slug`로 특정 부모 카테고리만 받습니다.
3. `GET /categories/tree/{categoryId}`로 단건과 하위 카테고리를 확인합니다.
4. `GET /categories/search?q=`로 이름 검색합니다.
5. 얻은 `id`를 Product 목록의 `by_category`에 사용합니다.

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| GET | `/categories` | 없음 | 없음 | 200 (`CategoryResponse[]`), 404, 405 |
| GET | `/categories/tree` | 없음 | 쿼리 `by_category_slug`(optional) | 200 (`CategoryTreeResponse[]`), 404, 405 |
| GET | `/categories/tree/{categoryId}` | 없음 | 경로 `categoryId`(string) | 200 (`CategoryTreeResponse`), 404, 405 |
| GET | `/categories/search` | 없음 | 쿼리 `q`(string, required) | 200 (`CategoryResponse[]`), 404, 405 |

스키마: `CategoryResponse`/`CategoryTreeResponse`는 `id`, `parent_id`(string 또는 null), `name`, `slug`, `sub_categories`(재귀)입니다. 둘 다 `required` 지정이 없습니다.

## 4. 리스크

- R1 (높음): `Accept` 헤더 누락 시 404가 302로 나올 수 있음
  - 근거: 백로그 #4. 존재하지 않는 id의 404 TC에 해당
- R13 (낮음): `categoryId` 형식 제한이 없어 형식 오류 id의 응답이 404인지 불명
  - 근거: `GET /categories/tree/{categoryId}`의 path 파라미터가 `type: string`뿐
- R14 (낮음): `q` 필수인데 누락 시 응답 코드가 스펙에 없음
  - 근거: `GET /categories/search`는 `q` required이고 responses에 422가 없음
- R6 (중간): 같은 이름의 `CategoryResponse`가 Product 중첩에서는 축소된 필드로 내려옴
  - 근거: 백로그 #1. Category 단독 응답은 전체 스키마, Product 내부와 구분 필요

## 5. 테스트 범위 (포함)

- 목록/트리/단건/검색 조회 성공과 응답 스키마
- 트리의 `sub_categories` 구조와 `parent_id` 정합성
- 존재하지 않는 id의 404, `q` 누락 등 스펙에서 도출되는 네거티브
- 제외: 쓰기(`POST`/`PUT`/`PATCH`/`DELETE`)와 `QUERY` 변형 (개요 4번)

## 6. TC 작성 입력값

공통: 헤더 `Accept: application/json`, 인증 불필요.

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| C1 | `GET /categories` | 없음 | 200, 배열, 각 항목이 `CategoryResponse` 구조 | High |
| C2 | `GET /categories/tree` | 없음 | 200, 배열, 각 항목이 `CategoryTreeResponse` 구조 | High |
| C3 | `GET /categories/tree/{categoryId}` | C2에서 얻은 유효한 id | 200, 해당 id의 객체 | High |
| C4 | `GET /categories/search` | `q`=목록에 있는 이름의 일부 (스펙 예시 `tools`) | 200, 배열. 매칭 규칙은 확인 필요 | High |
| C5 | `GET /categories/tree` | `by_category_slug`=`hand-tools` (스펙 QUERY 예시) | 200, 배열. 결과 범위는 확인 필요 | Medium |
| C6 | `GET /categories/tree` | 없음 | 최상위 항목의 `parent_id`가 null 허용, `sub_categories`는 배열 | Medium |
| C7 | `GET /categories` | 없음 | 응답 타입 검증: `id` string, `slug` string | Medium |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| C8 | `GET /categories/tree/{categoryId}` | 존재하지 않는 id | 404 | High |
| C9 | `GET /categories/search` | `q` 누락 | 확인 필요 (스펙은 required만 명시) | Medium |
| C10 | `GET /categories/search` | 매칭되지 않는 `q` | 200 빈 배열인지 404인지 확인 필요 | Low |
| C11 | `GET /categories/tree` | 존재하지 않는 `by_category_slug` | 확인 필요 | Low |
| C12 | `GET /categories/tree/{categoryId}` | 형식이 잘못된 id (예: 짧은 문자열) | 404 또는 다른 코드, 확인 필요 | Low |
