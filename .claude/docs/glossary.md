# 용어 정리
이 프로젝트에서 테스트 표시와 결과 집계에 쓰는 용어의 정의다. 다른 문서가 이 용어를 쓰면 이 파일을 기준으로 읽는다. 정리 날짜 2026-10-11.

## 1. 결론
- xfail과 XPASS는 Jira 등록 전 결함을 잠깐 고정하는 단계에서만 생긴다.
- Jira에 등록된 결함은 issue 마커로 표시하고 일반 실패로 집계한다.
- Blocked는 판정할 수 있지만 이번에 실행하지 않은 TC, N/A는 스펙에 기대결과가 없어 판정할 수 없는 TC다.

## 2. 테스트 코드의 표시
1. xfail(expected fail, 실패 예상)
   - 알려진 결함 때문에 실패할 것이라고 미리 표시한 테스트다. `xfail(strict=True)` 또는 테스트 안의 `pytest.xfail("백로그 #N")`로 쓴다.
   - 백로그에 real-bug로 등록했고 아직 Jira에 등록하지 않은 동안만 쓴다. 방법은 `.claude/skills/script-write/SKILL.md` "xfail 규칙".
2. XPASS(unexpected pass, 예상 밖 통과)
   - xfail 테스트가 통과한 경우다. 결함이 고쳐졌다는 신호다.
   - `strict=True`라서 XPASS는 테스트 실패로 처리되어 바로 드러난다. xfail이 있을 때만 생긴다.
3. issue 마커(`@pytest.mark.issue("QA-N")`)
   - Jira에 등록된 결함의 테스트 표시다. 고쳐질 때까지 일반 실패로 집계한다.
   - 이 테스트가 통과하면 수정 신호다. Slack 실패 상세의 `[Jira 결함 통과 · 수정 확인 필요]`에 나온다.
4. `spec_undefined` 마커
   - 스펙에 정확한 기대결과가 없는 TC다. 전체 실행에서 빼고 안건으로 다룬다.

## 3. 결과 보고서의 칸
1. Fail: 실행했는데 실패한 TC. xfail로 고정한 테스트도 Fail에 넣는다.
2. Blocked: 판정할 수 있지만 실행하지 못했거나 실행하지 않은 TC. 실행률을 낮춘다.
   - ex: 사이트 장애, 사전 조건 데이터 없음, 수동 TC 미실행
   - 임시 운영(2026-10-11 결정): 수정 배포가 없는 Jira 결함의 issue 마커 TC는 실행하지 않고 Blocked로 센다. 데모 서비스는 결함이 고쳐지지 않아 같은 결과가 반복되기 때문이다.
3. N/A: `spec_undefined` 마커 TC. 판정할 기준이 없어 실행률 계산에서도 뺀다.
4. Known issue(2026-10-12 사용자 결정): 수정하지 않기로 승인한 Jira 결함. Jira 레이블 `known-issue`를 붙이고, 그 결함의 issue 마커 TC는 실행하지 않는다. 보고서 표에는 Blocked 칸에 쓰고 사유를 "known issue 승인"으로 적으며, 사인오프 실행률 분모에서는 뺀다(QA plan 1.4). 결과 보고서의 Known Issues 목록은 이 레이블로 만든다.
5. Blocked와 N/A의 차이: Blocked는 "판정할 수 있는데 이번에 돌리지 않은 것"이라 실행률을 낮추고, N/A는 "판정 기준이 없는 것"이라 낮추지 않는다.

## 4. 결함 하나의 흐름
1. 전체 실행에서 실패 → `/test-triage`로 real-bug 분류 → 백로그 등록(필요하면 xfail로 고정)
2. 노션 이슈 검수에서 승인 → Jira 등록 → xfail을 풀고 issue 마커를 붙인다(실패로 집계)
3. 수정 배포 전 Iteration: issue 마커 TC는 Blocked(임시 운영). 수정하지 않기로 승인하면 known issue로 두고 계속 실행하지 않는다.
4. 수정 배포 뒤 실행해 통과 → 수정 확인 → Jira 상태 갱신, issue 마커와 `known-issue` 레이블 해제
