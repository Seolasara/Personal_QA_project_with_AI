# 백로그: 해결·폐기
해결되었거나 더 이상 유효하지 않은 것. 번호가 참조되므로 지우지 않는다. 작성 형식은 `.claude/guides/backlog-format.md`를 따른다.

### #4 Cart addItem이 404/422 대신 302를 반환하는 것처럼 보임
- 발생 배경: Cart 테스트 작성 중 발견. `GET /postcode-lookup`의 필수 쿼리 누락도 같은 패턴이라 API 전체 negative-path 테스트의 공통 함정이었다.
- 추정 원인과 근거: 테스트 클라이언트(`clients/base_client.py`의 `get_client()`)가 `Accept: application/json`을 보내지 않아 Laravel이 기본 동작(302)을 탔다. 헤더를 붙이면 `422 {"message":"The selected product id is invalid."}`로 스펙과 일치한다(라이브 검증).
- 분류와 상태: test-bug(2026-09-28 real-bug에서 재분류) / 해결됨: 클라이언트가 항상 헤더를 보내고 기대값을 422로 고쳤다. Confluence 5996545 축3 패널의 "Cart addItem 302" 기록은 재검토 필요 / 발견 2026-09-28, 마지막 확인 2026-10-08 테스트 통과
- 대상 TC
  1. [API_77] 장바구니에 존재하지 않는 상품 추가 시도 확인
     - 스펙: 잘못된 product_id는 422다.
     - 라이브: 헤더 없이는 302, 헤더를 붙이면 422(스펙과 일치)

### #9 리포트 스크립트가 UI 테스트만 스캔함
- 문제 정의: `scripts/gen_traceability.py`, `scripts/gen_test_report.py`가 `playwright-demo/tests`만 스캔한다.
- 발생 배경: api-demo에 TC가 쌓이면서 확인.
- 추정 원인과 근거: 스크립트가 UI 폴더 기준으로 작성되었다.
- 분류와 상태: 폐기 / `gen_traceability.py`는 삭제되었고 `gen_test_report.py`는 TC를 읽지 않는다 / 발견 날짜 미상, 마지막 확인 2026-10-08

### #11 테스트 결과 리포트 방식 재검토
- 문제 정의: TC 원본이 스프레드시트로 옮겨지면서 `scripts/gen_test_report.py`가 TC 메타 없이 pytest 결과만 표로 만든다.
- 발생 배경: TC 관리를 스프레드시트로 이전한 뒤 서브에이전트를 만든 다음 다시 정하기로 했다.
- 추정 원인과 근거: 리포트 생성 방식이 TC 메타를 읽던 시절 구조 그대로다.
- 분류와 상태: 폐기 / 리포트 방식은 `/test-report` 스킬 설계에서 다룬다(`pipeline-design.md`) / 발견 2026-10-05, 마지막 확인 2026-10-08

### #23 시트 기대결과 오기 수정
- 발생 배경: 2026-10-06 스펙 불일치 목록 작성 중 확인(유형 D). 스펙 불일치가 아니라 TC 수정 대상이다.
- 추정 원인과 근거: TC 작성 시 출처 없이 쓴 값이다.
- 분류와 상태: test-bug(TC 오기) / 해결됨: API_84는 "Requested item not found", API_101은 `"status": "string"`으로 시트가 수정되어 있다 / 발견 2026-10-06, 마지막 확인 2026-10-08 시트
- 대상 TC
  1. [API_84] 존재하지 않는 장바구니 조회 실패 확인
     - 스펙/라이브: `GET /carts/{cartId}` 404 `ItemNotFoundResponse` "Requested item not found"
     - 시트(수정 전): "Cart not found"
  2. [API_101] 인보이스 단건 정상 조회 확인
     - 스펙: `status`는 string이고 예시만 "COMPLETED"다.
     - 라이브: `AWAITING_FULFILLMENT`
     - 시트(수정 전): `AWAITING_SHIPMENT`(출처 불명)
