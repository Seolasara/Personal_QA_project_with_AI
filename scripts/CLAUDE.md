# scripts/

리포트 생성 + CI 게이트 스크립트.

- `gen_traceability.py`는 **CI 게이트**다: `testcases/*.md`의 `automation.test`와
  실제 `@pytest.mark.tc` 마커가 어긋나면 non-zero로 종료해야 한다.
  이 exit-code 동작을 완화/제거하지 말 것 (가드레일의 "검증을 항상 통과하게 바꿔치기 금지"와 동일 취지).
- `gen_test_report.py`가 만드는 `test-results/test-report.md` / `report.html`의
  필드/표 구조를 바꾸면 테스트플랜 "Test 결과" 단계 산출물과 어긋날 수 있으니 변경 시 `testplan.md`도 함께 갱신.
- `_common.py`는 다른 스크립트가 공유하는 헬퍼 — 순수 함수 유지, 부수효과(출력/네트워크) 추가 금지.
- TC frontmatter 스키마는 [testcases/CLAUDE.md](../testcases/CLAUDE.md)가 원본, 여기서 재정의하지 않는다.