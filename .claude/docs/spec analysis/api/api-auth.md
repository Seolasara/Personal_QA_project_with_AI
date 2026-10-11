# API 분석: Login / Logout

> 개요와 전체 리스크 표는 [00_api-overview.md](00_api-overview.md)를 참고합니다.

## 1. 기능 목적

| 항목 | 내용 |
|---|---|
| 리소스 | Login, Logout (스펙 태그 User의 일부) |
| 목적 | 이메일/비밀번호로 JWT를 발급하고, 로그아웃으로 토큰을 무효화합니다 |
| 사용처 | Invoice 등 인증이 필요한 엔드포인트의 선행 단계 |
| 스펙 근거 | `POST /users/login`(`login-customer`), `GET /users/logout`(`logOut`), 보안 스킴 `apiAuth`(HTTP bearer, JWT) |

## 2. 핵심 흐름

1. `POST /users/login`에 `email`, `password`를 보냅니다.
2. 200 응답의 `access_token`을 받습니다 (`token_type`, `expires_in` 포함).
3. 이후 요청에 `Authorization: Bearer <access_token>`을 붙입니다.
4. `GET /users/logout`을 호출하면 토큰이 무효화됩니다 (`message` 반환).
5. 무효화된 토큰으로 인증 엔드포인트를 호출하면 401이 되는지는 스펙에 명시되지 않아 확인 필요입니다.

## 3. 엔드포인트 요약

| 메서드 | 경로 | 인증 | 주요 요청 | 스펙상 응답 코드 |
|---|---|---|---|---|
| POST | `/users/login` | 없음 | 바디 `email`(string, required), `password`(string, required) | 200 (`TokenResponse`: `access_token`, `token_type`, `expires_in`) |
| GET | `/users/logout` | 필요 (`apiAuth`) | 없음 | 200 (`message`), 400, 401 |

## 4. 리스크

- R4 (높음): 로그인 3회 실패 시 계정이 잠겨 423이 되고, 올바른 비밀번호로도 해제되지 않음
  - 근거: 백로그 #8. 스펙의 `POST /users/login`은 200만 정의하고 잠김 응답은 없음. 소스의 `UserController::login`은 잠김 423, 비활성 403, 기타 401로 매핑 [불일치: 스펙 미정의]
  - 대응: 네거티브 TC는 전용 계정으로만 수행하고, 잠김 TC는 스펙 기대값이 없어 확인 필요로 둠
- R7 (중간): 로그인 실패 상태코드가 스펙에 없음
  - 근거: `POST /users/login` responses에 200만 존재. 소스는 실패 시 401/423/403/400 반환 [불일치: 스펙 미정의]
  - 판단: 스펙 기준으로 실패 코드는 "확인 필요"
- R10 (중간): 토큰 만료 시간이 짧아 인증 TC가 타이밍에 민감함
  - 근거: `TokenResponse.expires_in` 예시 120. 로그아웃은 `GET /users/logout`의 400/401 조건이 스펙에 설명되지 않음
  - 소스상 로그아웃 실패는 500이지만 스펙은 400이라 [불일치], 스펙 기준으로 400은 "확인 필요"
- R1 (높음): `Accept: application/json` 없이 호출하면 검증 실패 응답이 302로 나올 수 있음
  - 근거: 백로그 #4, `api-demo/CLAUDE.md`

## 5. 테스트 범위 (포함)

- 로그인 성공 응답의 필드와 타입 (`access_token`, `token_type`, `expires_in`)
- 발급 토큰으로 `security`가 걸린 엔드포인트에 접근 가능한지
- 로그아웃 성공 응답과 토큰 없는 호출의 401
- 필수값 누락 등 스펙에서 도출되는 로그인 네거티브 (응답 코드는 확인 필요 표기)
- 계정 잠김(423) 실행은 제외하고 리스크로만 둡니다. 스펙에 기대값이 없고 계정이 잠기기 때문입니다.

## 6. TC 작성 입력값

공통: 계정/토큰 값은 TC에 쓰지 않고 fixture에서 받습니다. 헤더는 `Accept: application/json`을 포함합니다.

### 6-1. 정상 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| A1 | `POST /users/login` | 유효한 `email`, `password` | 200, 바디에 `access_token` | High |
| A2 | `POST /users/login` | 유효한 계정 | 200, `token_type`(string), `expires_in`(number) 존재 | Medium |
| A3 | `GET /invoices` | A1의 토큰으로 `Authorization: Bearer` | 200 (인증 통과 확인) | High |
| A4 | `GET /users/logout` | 유효한 토큰 | 200, `message`(string) | High |
| A5 | `GET /invoices` | A4 이후 같은 토큰 | 확인 필요 (스펙에 무효화 후 코드 없음, 401 추정은 근거 아님) | Medium |

### 6-2. 네거티브 케이스

| 후보 | 엔드포인트 | 입력 | 기대 결과 | 중요도 |
|---|---|---|---|---|
| A6 | `POST /users/login` | `email` 누락 | 확인 필요 (스펙은 required만 명시, 응답 코드 없음) | High |
| A7 | `POST /users/login` | `password` 누락 | 확인 필요 | High |
| A8 | `POST /users/login` | 올바른 이메일 + 틀린 비밀번호 (1회만) | 확인 필요 (스펙에 코드 없음). 잠김 방지를 위해 반복 금지 | High |
| A9 | `POST /users/login` | 존재하지 않는 이메일 | 확인 필요 | Medium |
| A10 | `POST /users/login` | 형식이 잘못된 `email` | 확인 필요 | Low |
| A11 | `GET /users/logout` | `Authorization` 없음 | 401 | High |
| A12 | `GET /users/logout` | 형식이 잘못된 토큰 | 401 (스펙은 401 정의, 토큰 형식별 코드는 확인 필요) | Medium |
| A13 | `POST /users/login` | 3회 이상 연속 실패 | 확인 필요 (스펙에 기대값 없음. 백로그 #8 참고, 전용 계정으로만, 실행 여부는 TC-Writer 판단) | Low |
