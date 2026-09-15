# testcases/
TC 원본. **Confluence는 이 폴더의 파생본**이다.

## 포맷
```markdown
---
id: QA-12
title: Confirm 버튼 클릭 시 결제 완료 확인
priority: High            # High / Medium / Low
component: payment        # main | login | product | cart | payment | logout
confluence_page_id: 360539
automation:
  status: automated        # automated | manual | planned
  test: playwright-demo/tests/payment_test.py::test_payment_checkout
---
## 조건
## 스텝
1. <행동> → <기대결과>
## 비고
```
- ID는 Confluence "Test Case 설계" 표(page 360539)와 맞춰 `QA-01` ~ 순번 유지 (임의 재번호 금지).
- 테스트 쪽 역참조: `@pytest.mark.tc("QA-12")`.
- TC 변경 시 연결된 테스트 어설션이 여전히 기대결과와 맞는지 확인 후,
  `python scripts/gen_traceability.py`로 정합성 재생성 (마커-frontmatter 불일치면 CI 실패).

## Confluence 동기화
- 방향: **원본은 이 폴더**. `/tc-sync push`로 발행, `/tc-sync pull`로 반영.
- pull 시 자동 수리 금지 — 변경분은 `needs-review`로 표시만.
- CI 헤드리스에서는 OAuth 불가 → CI는 Confluence를 건드리지 않는다.
