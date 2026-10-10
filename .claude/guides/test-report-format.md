# 테스트 결과 보고서 형식
대상: Confluence "Test Result Report"(11665420) 하위의 `Test Result Report (YYYY-MM-DD)`. `/report-write`가 쓴다. 이 파일이 원본이고, Confluence "Test result Report Template"(11632643)은 섹션 제목만 맞춘 사본이다. 형식을 바꾸면 템플릿 페이지의 제목도 같이 고친다. 문체는 전역 "문서 문체"를 따른다.

## 1. 원칙
- 숫자는 보관본 report.json 기준이고, 노션 실행 행과 Slack 본문의 숫자와 같아야 한다.
- 이슈, 백로그, 노션 행은 링크로 잇는다. 읽는 사람이 근거로 바로 갈 수 있게 한다.
- 표는 수치와 목록에만 쓰고, 판단과 설명은 불릿으로 쓴다.

## 2. 섹션 (템플릿 순서 + 4~6번 추가)
1. Test Result Summary
   - Test Period(실행 일시), Environment(사이트 URL, 브라우저, 도구 버전), Build / Version(커밋과 브랜치), Tester(사라 AI, 검토자), Comment(사인오프 판정 한 줄)
2. Test Scope
   - UI, API별 대상 기능(대분류)과 TC 수, 자동/수동 TC 수, 제외 범위
3. Test Result (TC 커버리지 포함)
   - Total, Pass, Fail, Blocked, xfail, Pass Rate(통과/전체). Blocked는 실행하지 못한 TC(수동 미실행, 사전 조건 미충족)
   - 대분류별 표: 대분류, 전체, 통과, 실패, xfail
   - 커버리지: 시트 TC 수 대비 자동화된 TC 수
4. BTS Status
   - 이번 실행에서 새로 등록한 이슈: 키, 제목, 중요도, TC
   - 남은 이슈 표: 키, 제목, 중요도, 상태, 관련 TC. 표 위에 JQL `project = QA AND type = 버그 AND statusCategory != Done ORDER BY priority DESC`를 적는다.
   - Known Issues: xfail로 고정된 백로그 항목과 Jira 키
5. 실패 분류
   - 리포트 그룹(리얼버그, 테스트버그, flaky, 안건)별 건수와 TC, 처리 결과(등록, 수리, 보류). 노션 이슈 행 링크를 붙인다.
   - 안건: 스펙 판단이 필요한 항목과 백로그 링크. 승인된 안건은 wiki 안건 문서 대상으로 표시한다.
6. 사인오프와 다음 조치
   - 판정: 사인오프 기준 충족 여부와 근거(미해결 High 결함 수)
   - 다음 조치: 보류 항목, 수리 대상, 다음 실행 계획
