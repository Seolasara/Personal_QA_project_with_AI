# 테스트 결과 보고서 형식
대상: Confluence 결과 보고서. UI는 "UI Test Results"(12222506), API는 "API Test Results"(12288047) 하위에 쓴다. `/report-write`가 쓴다. 이 파일이 원본이고, Confluence "Test result Report Template"(11632643)은 섹션 제목만 맞춘 사본이다. 형식을 바꾸면 템플릿 페이지도 같이 고친다. 문체는 전역 "문서 문체"를 따른다.

## 1. 원칙
- UI와 API는 실행도 보고서도 따로 쓴다. 보고서 하나가 실행 하나(`test-runs/<일시>-<ui|api>`)다.
- Iteration: 사인오프 통과율을 맞출 때까지 3회까지 돌린다. Iteration마다 결과 보고서를 쓰고, 마지막에 사인오프용 결과 보고서를 쓴다.
  - Iteration 1: 개발 완료 후 1차 QA / Iteration 2: 결함 수정 후 재검증 / Iteration 3: 배포 전 Regression Test
  - Iteration 번호는 UI와 API가 따로 센다. 한쪽이 다음 회차로 넘어가도 다른 쪽은 자기 회차를 유지한다.
  - 사인오프용은 Iteration 결과를 모아 최종 판정을 쓴다. 노션 "테스트 실행" 행의 "실행 구분" 속성으로 묶는다. "스크립트 작성 후 전체 시범 실행"은 보고서 대상이 아니다.
- 제목 (날짜는 실행 날짜)
  - Iteration 보고서: `YYYYMMDD_Iteration<N>_Summary Report` (ex: `20261010_Iteration1_Summary Report`)
  - 사인오프용 최종 보고서: `YYYYMMDD_Test Result Report`
- Iteration 2, 3에는 Jira에 등록된 결함의 테스트(`@pytest.mark.issue`)를 반드시 포함해 실행한다. 보고서 Comment에 이슈별 재검증 결과(통과 = 수정 확인, 실패 = 미해결)를 쓴다.
- 섹션은 아래 4개만 쓴다. 템플릿에 없는 섹션, 대분류별 표, 판정 패널을 더하지 않는다.
- 숫자는 보관본 report.json 기준이고, 노션 실행 행과 Slack 본문의 숫자와 같아야 한다.

## 2. 섹션
1. Test Result Summary
   - 2열 표로 쓴다. 왼쪽 열이 기준(머리글 셀), 오른쪽 열이 값이다.
   - 행: Test Period, Environment, Build / Version, Tester, Comment
     - Test Period: 실행 일시와 소요 시간
     - Environment: 대상 URL, 브라우저 또는 HTTP 클라이언트, 도구 버전, OS
     - Build / Version: 서비스 버전(sprint5)과 테스트 코드 커밋, 브랜치
     - Tester: 사라(AI QA 리더), 검토자
     - Comment: 사인오프 판정과 기준, 근거. 기준은 해당 종류 QA plan(UI 65702, API 5996545)의 사인오프 기준이고, 근거는 미해결 High 결함 수와 Fail 건수다.
2. Test Scope
   - 대상 기능(대분류)과 TC 수, 실행한 TC 수
   - 제외한 TC: 스펙에 정확한 기대결과가 없어 전체 실행에서 뺀 TC(`spec_undefined` 마커) 수와 ID
   - 범위 밖 기능
3. Test Result
   - 표 한 줄: Total, Pass, Fail, N/A, Blocked, Pass Rate. 단위는 TC다(파라미터로 나뉜 테스트는 모두 통과해야 그 TC가 Pass).
     - Total: 시트 TC 수
     - Fail: 실패와 xfail(알려진 불일치로 고정한 테스트)을 모두 넣는다. xfail 칸은 두지 않는다.
     - N/A: 스펙에 정확한 기대결과가 없어 실행에서 뺀 TC(`spec_undefined`). 안건으로 따로 다룬다.
     - Blocked: 판정할 수 있지만 환경이나 데이터 문제로 실행하지 못한 TC(ex: 사이트 장애, 사전 조건 데이터 없음, 수동 TC 미실행). N/A와 달리 실행률을 낮춘다.
     - Pass Rate: Pass / 실행한 TC (실행한 TC = Total - N/A - Blocked)
   - 커버리지: 자동화율(자동화된 TC / 시트 TC)과 실행률(실행한 TC / (Total - N/A)). 기준은 QA plan 1.4 Sign-off Criteria
4. BTS Status
   - Jira 실시간 목록(jira 매크로)만 둔다. 각 목록 위에 JQL을 한 줄로 적고, 그 아래에 다른 표나 설명을 두지 않는다.
     - 이번 실행에서 등록한 이슈: `project = QA AND type = 버그 AND labels = <ui|api> AND created >= "<실행 날짜>" ORDER BY priority DESC`
     - Total remaining issues: `project = QA AND type = 버그 AND labels = <ui|api> AND statusCategory != Done ORDER BY priority DESC`
     - Known Issues: `project = QA AND type = 버그 AND labels = <ui|api> AND statusCategory != Done AND created < "<실행 날짜>" ORDER BY priority DESC`
