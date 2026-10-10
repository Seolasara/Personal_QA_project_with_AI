# 백로그: 판단 보류
확인이 끝나지 않아 분류를 정하지 못한 것. 작성 형식은 `.claude/guides/backlog-format.md`를 따른다.

### #6 결제 첫 Confirm 클릭에서 `checkPayment()`가 undefined를 반환할 가능성
- 문제 정의: UI 결제에서 첫 Confirm 클릭 시 `of(this.state)`(undefined)가 반환될 수 있다.
- 발생 배경: 앱 소스 확인 중 발견. 재현해 보지 않았다.
- 추정 원인과 근거: 앱 코드의 `checkPayment()` 구현. 재현되면 수리하지 않고 보고만 하기로 확정했다(가드레일).
- 분류와 상태: 판단 보류(real-bug 후보) / UI에서 재현 필요 / 발견 날짜 미상, 마지막 확인 2026-10-10 미재현(`/flow-map` 결제 완료 탐색, UI_35~37 실행에서 [Check payment] 1회 후 [Confirm]으로 정상 진행)
