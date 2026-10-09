# 문서 지도
작업별로 어떤 문서를 읽는지 정리한 목록이다. 자동으로 읽히지 않으며, 문서 위치를 모르거나 필요할 때만 연다.
- 새 문서를 만들거나 옮기면 이 목록에 한 줄을 추가하거나 고친다.
- 스킬이나 에이전트가 자기 작업의 필수 파일을 이미 지정했다면 그쪽을 먼저 따른다.
- 작업 중 문서 이름이나 경로가 바뀌면 `grep`으로 옛 경로를 찾아 함께 고친다.

## 1. 작업별로 읽을 문서
1. 기능 요구사항(User Story, AC)이 필요할 때
   - `.claude/docs/specs/v5/00_index.md`: 목록에서 해당 기능 파일만 읽는다. 통째로 읽지 않는다.
   - `.claude/docs/spec analysis/ui/`, `api/`: Document-Analyzer가 정리한 기능 목적, 핵심 흐름, 리스크. 개요 파일(`00_`)부터 읽는다.
   - API 스펙 원본: `api-demo/api-docs.json`
2. TC를 쓸 때 (TC-Writer가 읽는 문서)
   - `.claude/skills/tc-write/SKILL.md`: TC 작성 포맷과 방법(열 구성, 작성 규칙, 검수 표시와 마커, 작성 후 점검 체크리스트)
   - `.claude/agents/TC-Writer.md`: 작업 순서와 업무 규칙, 시트 쓰기 절차
   - 기능 요구사항과 스펙 분석: 위 1번에서 대상 기능 파일만. 기능 파일의 "6. 변경 이력"에 최근 서비스 변경이 있으면 TC 추가·수정 후보로 반영한다.
   - 해당 종류 폴더의 `CLAUDE.md`: 스펙 기준, QA plan 페이지
   - `.claude/docs/backlog/00_index.md`: 대상 기능과 관련된 항목만
3. 테스트 스크립트를 쓸 때 (Script-Writer가 읽는 문서)
   - `.claude/skills/script-write/SKILL.md`: 스크립트 작성 포맷과 방법(공통 규칙, xfail 규칙, 실행 규칙, 작성 후 점검 체크리스트)
   - `.claude/agents/Script-Writer.md`: 작업 순서와 업무 규칙
   - 해당 종류 폴더의 `CLAUDE.md`: `playwright-demo/` 또는 `api-demo/`의 구조, 컨벤션, 시트 주소
   - `.claude/docs/backlog/00_index.md`: xfail을 붙일 때 대상 항목 확인
4. 전체 테스트를 실행하고 실패를 분류할 때
   - `.claude/skills/test-run/SKILL.md`: 사전 점검, 실행, 보관(`test-runs/`), Slack 보고
   - `.claude/skills/test-triage/SKILL.md`
   - `.claude/docs/backlog/00_index.md`: 이미 등록된 항목인지 먼저 확인한다.
5. 백로그에 기록할 때
   - `.claude/guides/backlog-format.md`: 항목 형식, 불일치 유형, 파일 배치
   - `.claude/docs/backlog/00_index.md`: 중복 확인과 다음 번호
6. Jira 이슈를 쓸 때
   - `.claude/guides/jira-issue-format.md`: 제목, 본문 8개 섹션. 샘플은 QA-4
   - 해당 종류 폴더의 `CLAUDE.md`: 레이블, 에픽, 증거 형식
7. 스펙 분석을 새로 하거나 서비스 변경을 반영할 때 (`/spec-analysis [ui|api] [update]`)
   - `.claude/skills/spec-analysis/SKILL.md`: 분석 포맷, 기준 커밋 기록, 변경 이력 형식, 변경분 분석 방법, 분석 로그 형식
   - `.claude/docs/spec analysis/analysis-log.md`: 분석을 실행한 이력(한 줄 요약, 변경 없음 포함)
   - `.claude/agents/Document-Analyzer.md`: 작업 순서와 업무 규칙
8. 스크립트(`scripts/`)를 실행하거나 고칠 때
   - 공통 원칙: 시트와 네트워크를 직접 읽지 않고 로컬 파일만 처리한다(루트 `CLAUDE.md`). 각 파일 맨 위 설명에 사용법이 있다.
   - `script_lint.py`: 테스트 파일을 코드 규칙으로 점검
   - `tc_marker_check.py`: 테스트 마커와 시트 CSV의 ID 대조
   - `tc_lint.py`: TC 초안(JSON 또는 CSV)을 `.claude/skills/tc-write/SKILL.md`의 서식 규칙으로 점검
   - `sheet_diff.py`: 시트 쓰기 전후 CSV를 비교해 의도하지 않은 변경을 찾음
   - `backlog_index.py`: 백로그 항목 파일에서 `00_index.md` 목록을 다시 만듦
   - `spec_split.py`: 업스트림 `v5.md`를 `.claude/docs/specs/v5/` 기능별 파일로 나눔
   - `gen_test_report.py --type ui|api`, `failures.py`(UI): 테스트 결과 리포트와 실패 목록. 리포트 출력 구조(`test-results/test-report.md`, `report.html`)를 바꾸면 wiki의 "테스트 결과" 단계 문서도 같이 갱신한다.
   - `run_summary.py`: 보관한 report.json으로 Slack 요약 텍스트(본문, 실패 상세 스레드)를 만듦
   - `_common.py`: 공유 헬퍼. 순수 함수로 유지하고 출력이나 네트워크 같은 부수효과를 넣지 않는다.
9. 새 테스트 종류를 추가할 때
   - 폴더와 폴더 `CLAUDE.md`를 만든다. 들어갈 내용: 구조, 실행 방법, 스펙 기준, QA plan, 계정, 시트 주소와 TC ID 접두어, Jira 레이블·에픽, 증거 형식, 종류 전용 금지 사항
   - 새 스프레드시트 파일(TC 탭 하나)과 Jira 에픽을 만들고, `scripts/` 점검 스크립트를 확장할지 확인한다.
   - 루트 `CLAUDE.md`는 "규칙 문서와 폴더"의 테스트 종류 목록만 갱신한다.
10. 파이프라인 전체 설계가 필요할 때
   - `.claude/docs/pipeline-design.md`: 스킬과 에이전트 구성, 승인 지점, 만드는 순서

## 2. 아직 없는 문서 (만든 뒤 위 목록에 추가)
- `/test-report`, `/issue-register`, `/report-write` 스킬
- Test-Runner, Issue-Triager, Report-Writer 에이전트
- 결과 보고서 작성 지침(Confluence 템플릿 "Test result Report Template" 11632643 기반)
