# Jira 버그 이슈 작성 형식
대상: real-bug로 분류되어 Notion "이슈 검수" DB에서 승인된 이슈. 등록 전에 백로그와 Jira에서 중복을 찾고, 같은 원인은 이슈 하나로 묶는다.

## 1. 필드
- 프로젝트 `QA`, 이슈 유형 "버그"
- 레이블: 종류 레이블(`ui` 또는 `api`)을 붙인다. 스펙과 라이브 불일치이면 `spec-mismatch`도 붙인다.
- 에픽: 종류별 에픽 하위에 둔다(키는 각 폴더 `CLAUDE.md`).
- 우선순위: 이슈 중요도(High/Medium/Low)와 같게 둔다. 기준은 `.claude/guides/issue-severity.md`. 컴포넌트는 쓰지 않는다.

## 2. 제목
- `[종류] 어떤 기능에서 어떤 현상` (ex: `[API] 연관 상품 조회 시 존재하지 않는 상품 id를 보내면 404 대신 500 Server Error 반환`)
- 기대와 실제를 제목에서 알 수 있게 쓴다.

## 3. 본문
섹션 제목은 대괄호 안에 영어로 `## [Summary]`처럼 쓴다. 순서대로 `[Summary]`, `[Test Environment]`, `[Pre-conditions]`, `[Steps]`, `[Expected Result]`, `[Actual Result]`, `[Screenshots/Logs]`, `[Severity]`, `[Reference]`다. 문체는 "~함" 혹은 명사형으로 끝내며, 아래 순서를 지킨다.
1. Summary: 무엇이 어떻게 다른지 1~2불릿.
2. Test Environment: 재현이 가능하도록 테스트 했던 환경을 작성. ex. OS, 브라우저, 테스트 툴, 프레임워크, 버전 등, 대상 URL, 테스트 대상, 테스트 계정
  - 테스트 실행일은 날짜만 쓴다(시각 제외). ex: `테스트 실행일: 2026-10-11 (Iteration 1 UI 전체 실행)`
  - 자동화 테스트 파일과 테스트 함수도 여기에 쓴다. ex: `자동화 테스트: playwright-demo/tests/catalog_test.py::test_category_page_filters (UI_50)`
3. Pre-conditions: TC번호, 테스트에 사용한 계정과 데이터, 테스트에 꼭 필요한 사전 정보나 상태
4. Steps: 번호 목록. TC 스텝을 그대로 옮기지 않고, 처음 보는 사람이 재현할 수 있게 시작 지점(ex: 로그인, 메인 페이지, 토큰 발급)부터 결함 확인까지의 흐름을 쓴다.
  - ex: 1. 해당 계정으로 로그인 / 2. 메인페이지에서 랜덤 상품 장바구니에 추가 / 3. 장바구니 페이지 진입 / 4. [Proceed to checkout] 버튼 클릭 / 5. SIGN IN 단계 화면 확인
  - API의 POST, PUT 같은 바디 있는 요청은 테스트에서 사용한 요청 바디를 그 스텝 아래 코드 블록으로 그대로 쓴다. 계정 값만 `<email>`처럼 가린다.
5. Expected result: 테스트에 대한 최종 기대 결과 작성
6. Actual result: 테스트에 대한 최종 실제 결과 작성
7. Screenshots/Logs:
  - UI는 실패 시점 스크린샷을 첨부한다.
  - API는 응답 원문(상태 코드와 바디)을 쓴다. 요청 바디는 4번 Steps에 있다.
  - 실제로 실패한 자동화 테스트 로그(pytest 실패 출력의 파일:줄, 어설션, 기대값과 실제값)를 코드 블록으로 붙인다.
8. Severity: `High`, `Medium`, `Low` 중 하나만 쓴다. 이유나 설명은 붙이지 않는다(기준은 `.claude/guides/issue-severity.md`).
9. Reference: 이슈 재현에 필요한 정보와 뒷받침하는 근거 자료만 쓴다. 추정 원인, 문구 출처 추정, 백로그 같은 QA 프로젝트 내부 문서는 넣지 않는다.
  - 스펙 링크. UI: `https://github.com/testsmith-io/practice-software-testing/blob/main/docs/user-stories/v5.md#<AC 앵커>` (ex: `#ac5--already-logged-in`), API: Swagger `https://api.practicesoftwaretesting.com/api/documentation#/<태그>/<operationId>`
  - 비교 근거. ex: 같은 id로 `GET /products/{id}`는 404를 반환함

## 4. 주의
- 라이브 값은 바뀔 수 있으나 반드시 테스트에 확인한 동일 정보를 적는다. 확인 일시를 반드시 적는다.