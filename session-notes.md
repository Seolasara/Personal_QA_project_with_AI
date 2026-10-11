# Claude Code 세션 관리 메모

QA 프로젝트 작업과는 별개로, Claude Code 세션을 여러 개 오갈 때 쓰는 방법 정리.

## 세션 목록
- sara: 메인
- jd: JD 맞춤
- study: 공부용
- anything: 아무거나

## 세션 이름 붙이는 절차 (2026-10-04 확정)
- **터미널에서 열 때**: `sara` / `study` / `jd` / `anything` 함수로 실행 (`~/.zshrc`에 정의, 실행 시 `claude -n <이름>`으로 이름이 자동 붙음).
- **VS Code 확장으로 열 때**: 세션을 연 직후 첫 번째로 `/rename <이름>` 입력.
- 기존에 열려 있던 세션은 함수 방식이 적용되지 않으니, 한 번 나갔다가 함수로 다시 열거나 `/rename`을 칠 것.

## 세션 이름표가 풀리는 문제
- 세션 이름(sara/gugu/study/qq)은 `/rename <이름>`으로 직접 지정해야 붙는다.
- 새로 열리거나 재시작되면 이름표가 없어지고 자동 생성 ID(`personal-qa-project-34` 같은 형태)로 보임 — 다른 세션에서 이름으로 찾으려 하면 안 보일 수 있음.
- `ListAgents`로 봤을 때 이름 없이 뜨는 피어 세션은 아직 `/rename` 안 한 상태일 가능성이 큼. 세션 바꿔가며 쓸 때는 그 세션에서 먼저 `/rename <이름>` 해두는 게 안전.
- 2026-09-26 기준 `ListAgents` 관찰: 이 세션은 `personal-qa-project-34` → `/rename sara`로 재지정. 피어로 `personal-qa-project-b6`, `personal-qa-project-82` 두 개가 보였는데 이름표가 없어서 이 중 어느 게 gugu/study/qq인지는 미확인 (해당 세션에서 직접 `/rename` 해야 구분 가능).
