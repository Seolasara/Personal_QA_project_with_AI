# API 분석: Postcode

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Postcode |
| 목적 | 국가와 우편번호로 주소(거리, 도시, 주)를 조회합니다 |
| 사용처 | 결제 화면의 Billing Address 자동 채움, Invoice 생성 시 billing 값의 기준 |
| 스펙 근거 | `GET /postcode-lookup` |

## 2. 핵심 흐름

1. `GET /postcode-lookup`에 `country`, `postcode`(선택으로 `house_number`)를 보냅니다.
2. 200 응답으로 `street`, `house_number`, `city`, `state`, `country`, `postcode`를 받습니다.
3. 이 값을 Invoice 생성의 `billing_*` 필드에 사용합니다 (R2 참고).

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| GET | `/postcode-lookup` | 없음 | 쿼리 `country`(string, required, maxLength 40), `postcode`(string, required, maxLength 10), `house_number`(string, optional, maxLength 10) | 200 (`street`, `house_number`, `city`, `state`, `country`, `postcode`), 422, 502 (Upstream lookup failure) |

## 4. 리스크

- R1 (높음): 필수 파라미터 누락 시 `Accept` 헤더가 없으면 422 대신 302
  - 근거: 백로그 #4. `GET /postcode-lookup`의 필수 쿼리 누락에서 동일 패턴이 재현됨
- R11 (중간): 외부 조회 서비스와 국가별 우편번호 형식에 의존함
  - 근거: 스펙의 502 "Upstream lookup failure". 소스는 국가와 맞지 않는 우편번호 형식을 422로 거절 [소스 보조, 스펙에는 형식 규칙 없음]
  - 대응: 조회 성공 케이스는 실제로 조회 가능한 국가/우편번호 쌍이 필요하고 스펙에 예시 값이 없어 확인 필요
- R2 (높음): 이 응답이 Invoice 생성 시 billing 주소의 기준이 됨
  - 근거: 백로그 #3. 상세는 [api-invoice.md](api-invoice.md)

## 5. 테스트 범위 (포함)

- 유효한 국가/우편번호 조회의 응답 필드
- 필수 파라미터 누락, maxLength 초과의 422
- 502는 외부 장애 재현이 어려워 TC 후보에서 제외하고 확인 필요로 둡니다.

## 6. TC 작성 입력값

공통: 헤더 `Accept: application/json`, 인증 불필요. 유효한 `country`/`postcode` 쌍은 스펙에 없어 확인 필요입니다.

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| PC1 | `GET /postcode-lookup` | 유효한 `country`, `postcode` (값 확인 필요) | 200, `street`, `city`, `state`, `country`, `postcode` 존재 | High |
| PC2 | `GET /postcode-lookup` | PC1 + `house_number` | 200, 응답 `house_number`가 입력과 일치하는지 확인 필요 | Medium |
| PC3 | `GET /postcode-lookup` | 유효한 입력 | 응답 필드가 모두 string | Medium |
| PC4 | `GET /postcode-lookup` | `postcode` 10자 (경계) | 200 (maxLength 이내). 조회 가능한 값은 확인 필요 | Low |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| PC5 | `GET /postcode-lookup` | `country` 누락 | 422 | High |
| PC6 | `GET /postcode-lookup` | `postcode` 누락 | 422 | High |
| PC7 | `GET /postcode-lookup` | `country` 41자 | 422 (maxLength 40) | Medium |
| PC8 | `GET /postcode-lookup` | `postcode` 11자 | 422 (maxLength 10) | Medium |
| PC9 | `GET /postcode-lookup` | `house_number` 11자 | 422 (maxLength 10) | Low |
