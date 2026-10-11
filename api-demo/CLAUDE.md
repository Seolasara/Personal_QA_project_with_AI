# api-demo

API 테스트의 구조와 규칙이다. 프로젝트 공통 QA 규칙은 루트 [CLAUDE.md](../CLAUDE.md)를 따른다.

## 스펙 기준
- 스펙과 라이브가 다를 때 확인 순서(TC는 스펙 기준, 루트 "판단 기준")
  - `api-docs.json` → Swagger(`https://api.practicesoftwaretesting.com/api/documentation`, 같은 스펙을 읽음) → wiki "API specification"(Confluence 6750210) → TC
- QA plan: wiki "API Test QA Plan"(Confluence 5996545)
- TC ID 접두어 `API_`, 마커 `@pytest.mark.tc("API_NN")`, 시트: API 스프레드시트 https://docs.google.com/spreadsheets/d/1ozTySggSsHVertVhwUatZUIFI6ZMOLS5PVC5-m8T_-4/edit?usp=sharing 의 `API-TC` 탭
- Jira: 레이블 `api`, 에픽 QA-6(API 테스트 이슈). 증거는 요청과 응답 원문.
- 스펙 응답 스키마에는 `required`가 없다. 필드 누락을 계약 위반으로 볼지는 안건으로 판단한다.

## 구조
- `clients/` — 리소스별 HTTP 클라이언트. `httpx.Client`를 받아 엔드포인트 메서드만 노출한다 (UI의 Page Object에 해당).
- `schemas/` — pydantic 응답 모델. 스펙 원본 `api-docs.json`의 `components/schemas`를 옮기고, 모두 `schemas/common.py`의 `StrictModel`을 상속한다.
- `tests/` — 리소스별 테스트 파일 (`brand_test.py` 등).
- `conftest.py` — fixture: `api_client`(인증 없음), `authed_client`/`auth_token`(customer3 토큰), `other_user_client`(두 번째 고객 계정, 다른 사용자 데이터 접근 검증용), `admin_client`(관리자 토큰, 계정 잠금 해제 등 관리자 작업용), `cart_id`(종료 시 삭제), `cart_cleanup`(테스트가 만든 장바구니 정리), `product_id`, `address_info`.
- 테스트가 데이터를 남기면 fixture의 `yield` 뒤에서 정리한다. 인보이스는 삭제 API가 없어 정리하지 못한다.

## 실행
```bash
cd api-demo
source .venv/bin/activate
pytest            # 전체
pytest -m tc      # TC 마커 붙은 테스트만
pytest -m "not spec_undefined"   # /test-run 전체 실행 기준
```
- 의존성은 `requirements.txt`, venv는 `api-demo/.venv` (playwright-demo와 별도).
- 결과 리포트: `python3 ../scripts/gen_test_report.py --type api` → `test-results/test-report.md`.
- 계정은 코드에 쓰지 않고 `config.py`가 `.env`에서 읽는다. 최초 1회 `cp .env.example .env`.
- 계정별 용도
  - customer3(`API_EMAIL`): API 테스트 기본 계정. UI 계정(customer2)과 분리해 한쪽 계정 잠금(423)이 다른 쪽에 영향 주지 않게 한다.
  - customer(`API_EMAIL2`): 다른 사용자 데이터 접근 검증
  - admin(`ADMIN_EMAIL`): 계정 잠금 해제(백로그 #8), 계정 상태 조회 등 관리자 작업

## 컨벤션
- httpx는 sync만 쓴다.
- `get_client()`는 항상 `Accept: application/json`을 보낸다. 없으면 검증 실패가 422/404 대신 302 리다이렉트로 나온다.
- 인증이 필요한 엔드포인트(Invoice 등)만 `authed_client`를 쓰고, 나머지는 `api_client`.
- 응답은 status code와 pydantic 검증 두 단계로 확인한다. `StrictModel`은 `extra="forbid"`라 필드 누락/미문서화 필드가 실패로 드러나고(triage 원인 태그 `contract`), `strict=False`라 `"120"`→`120` 같은 타입 변환은 허용한다 (노이즈로 triage 비용만 늘어서).
- 필드 존재와 타입은 pydantic 모델 검증에 맡긴다. `isinstance`, `assert 필드`(비어 있지 않은지만 보는 어설션)는 쓰지 않는다. 어설션은 시트 기대결과에 값이 적힌 항목만 값 비교로 쓴다.
- 시나리오명이 "필드 타입 확인"인 TC만 `Model.model_validate(body, strict=True)`로 타입 변환 없이 검증한다.
- 데모 서버는 DB가 주기적으로 리셋되어 id가 바뀌고, 리셋 중에는 404/500/422가 일시적으로 날 수 있다(env, 백로그 #17). id는 테스트 안에서 조회한 값을 쓴다.
- xfail 교훈 사례: Cart addItem 302를 real-bug로 pin했다가 `Accept: application/json` 헤더 누락(test-bug)으로 밝혀졌다(2026-09-28, 백로그 #4).

## 아직 안 한 것
- schemathesis(negative-case 자동 생성). 서브에이전트 스킬로 설계만 정했다.
