# 테스트 결과 보고서 형식
대상: Confluence 결과 보고서. UI는 "UI Test Results"(12222506), API는 "API Test Results"(12288047) 하위에 쓴다. `/report-write`가 쓴다. 이 파일이 원본이고, Confluence "Test result Report Template"(11632643)은 섹션 제목만 맞춘 사본이다. 형식을 바꾸면 템플릿 페이지도 같이 고친다. 문체는 전역 "문서 문체"를 따른다.

## 1. 원칙
- UI와 API는 실행도 보고서도 따로 쓴다. 보고서 하나가 실행 하나(`test-runs/<일시>-<ui|api>`)다.
- Iteration: 사인오프 기준을 맞출 때까지 3회까지 돌린다. Iteration마다 결과 보고서를 쓰고, 마지막에 사인오프용 결과 보고서를 쓴다.
  - Iteration 1: 개발 완료 후 1차 QA / Iteration 2: 결함 수정 후 재검증 / Iteration 3: 배포 전 Regression Test
  - Iteration 번호는 UI와 API가 따로 센다.
  - "스크립트 작성 후 전체 시범 실행"은 보고서 대상이 아니다.
- **Iteration 보고서에는 그 회차에 일어난 일만 쓴다.** 앞 회차에서 등록한 이슈, 남은 이슈, known issue 목록을 다시 쓰지 않는다. 누적 정리는 사인오프 보고서에만 둔다.
- 제목 (날짜는 QA plan 일정의 해당 단계 날짜. 실제 실행일은 Test Period에 쓴다)
  - Iteration 보고서: `YYYYMMDD_<UI|API>_Iteration<N>_Test Result Report`
  - 사인오프용 최종 보고서: `YYYYMMDD_<UI|API>_Test Result Report: <PASS|FAIL>`
- 숫자 단위는 TC다. 파라미터로 나뉜 테스트는 모두 통과해야 그 TC가 Pass다. 숫자는 보관본 report.json 기준이고 노션 실행 행, Slack 본문과 같아야 한다.
- 실패 TC 수와 이슈 수를 구분한다. 한 이슈에 TC가 여럿 걸리면 이슈 표의 "관련 TC" 칸에 TC 수를 쓴다.
- 용어
  - N/A: 스펙에 정확한 기대결과가 없어 실행에서 뺀 TC(`spec_undefined`). 안건으로 따로 다룬다. 실행률 분모에서 뺀다.
  - Blocked: 판정할 수 있지만 실행하지 못한 TC. ex: 수정 미배포 이슈의 TC, 사이트 장애, 사전 조건 데이터 없음. 실행률을 낮춘다.
  - known issue: 수정하지 않기로 승인한 결함. Jira 레이블 `known-issue`를 붙이고 그 TC는 Blocked로 세되 실행률 분모에서 뺀다.
  - 판정 대상: Total - N/A
- Iteration 2, 3에는 Jira 등록 결함의 TC(`@pytest.mark.issue`)를 포함한다. 수정 배포가 없으면 실행하지 않고 Blocked(수정 미배포)로 센다.
- Iteration 3(Regression)은 회귀 TC만 실행한다. 회귀 TC는 smoke, 중요도 High, Jira 결함이 걸린 기능의 TC, Iteration 1·2 실패 이력, 간헐 후보의 합집합이다.
- 제목(h2)마다 앞에 구분선을 넣는다. 아래에 없는 섹션을 더하지 않는다.

## 2. Iteration 보고서
섹션은 3개다.
1. Test Result Summary: 2열 표(왼쪽 머리글 셀)
   - Test Period: 실행일, 실행 종류와 횟수, 소요 시간. ex: `2026-09-28, 전체 실행 1회(소요 9.3분)`
   - Result: 사인오프 기준 항목 값을 줄바꿈으로 나열한다. 기준 미달이 있으면 그 항목만, Blocked가 있으면 Blocked 건수도 쓴다. ex: `통과율 88.1%(52/59)`, `실행률 88.1%<br>통과율 98.1%<br>Blocked 7건`
   - Comment: 불릿 2~4개
     - 이번 회차 결과 한 문장. ex: `테스트 실행 대상 59건을 모두 실행해 Pass 52건, Fail 7건입니다.`
     - 실패가 있으면 성격과 영향 한 문장. ex: `실패 7건은 모두 스펙과 다른 동작이며 Jira 이슈 6건으로 등록했습니다. 핵심 흐름을 막는 결함은 없습니다.`
     - Blocked, 재실행, 회귀 선정처럼 숫자를 읽는 데 필요한 사정이 있으면 한 줄
     - 사인오프 기준 항목별 값 한 줄. UI는 `실행률, 통과율, 미해결 High 결함`, API는 `실행률, High TC 통과율, Medium/Low TC 통과율, 미해결 High 결함`
2. Test Result: 숫자 표 한 줄
   - 열: Total, N/A (스펙 미정의), 실행, Pass, Fail, Blocked, 실행률, Pass Rate
   - Blocked가 있으면 N/A 다음에 판정 대상 열을 넣고, Iteration 3은 그 자리에 회귀 대상 열을 넣는다.
   - 실행률 = 실행 / (판정 대상 - known issue Blocked). Pass Rate = Pass / 실행
   - Iteration 3은 표 아래에 `회귀 대상이 아닌 N건은 실행하지 않음` 한 줄을 둔다.
3. 이번 회차 실패와 이슈
   - 이번 회차에 새로 등록한 이슈를 표로 쓴다: 키(Jira 링크), 내용, 우선순위, 관련 TC 수. 표 아래에 `이슈 N건, 관련 TC N건` 합계를 쓴다.
   - 이슈가 아닌 실패(flaky, env, test-bug)는 불릿으로 TC, 증상, 결함이 아닌 이유를 한 줄씩 쓴다.
   - 새 이슈가 없으면 `새로 등록한 이슈 없음` 한 줄을 쓴다.
- 쓰지 않는 것: Environment, Build / Version, Tester, Test Scope 표, 남은 이슈 목록, Known Issues 목록

## 3. 사인오프용 최종 보고서
- Test Result Summary 표
  - 맨 위 행 `Test Result | PASS`(또는 FAIL), Test Period는 Iteration 1 ~ 3 기간
  - Environment, Build / Version, Tester는 마지막 실행 기준으로 쓴다.
  - Comment 순서
    1. 건수 문장: TC별 최종 결과 기준 `총 N건의 케이스 중 Pass N건, Fail N건, Blocked N건입니다.`
    2. 건수 문장 아래 하위 불릿으로 Iteration마다 주요 상황 한 줄. 실패 TC 수와 이슈 수를 구분해 쓴다. ex: `Iteration 1: 판정 대상 59건 중 Fail 7건, Jira 이슈 6건 등록`
    3. 판단이 필요한 이슈(키와 이유)와 `나머지 N건은 ~로 사용 흐름에 영향이 적어 보입니다.`
    4. Blocked(known issue 사인오프 예외)와 N/A(안건 관리) 설명
    5. 핵심 흐름 영향 요약
    6. 사인오프 기준 항목별 값과 `위 Sign-off 기준을 모두 충족합니다.`
- Test Scope: 대상 기능 목록, 제외(N/A, Blocked), 범위 밖
- Test Result: TC별 최종 결과(마지막으로 실행한 결과) 표, 자동화율과 실행률
- BTS Status: 전체 Iteration에서 등록한 이슈를 Jira 목록(jira 매크로, `key in (...)`)으로 두고, Total remaining issues와 Known Issues 목록을 둔다. 누적 이슈 목록은 사인오프 보고서에만 둔다.
