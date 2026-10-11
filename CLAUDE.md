# Personal QA Project
개인 테스트 경험 + AI 에이전트 + LLM judge 점검을 하나로 묶은 AI assisted QA 워크플로우 설계 프로젝트.

## QA 대상 서비스
- URL: https://practicesoftwaretesting.com
- 기획/스펙: https://github.com/testsmith-io/practice-software-testing

## 목표
1. QA 대상 서비스의 기획 문서, 요구사항을 분석하여 리스크 예방 중심의 품질 기준을 세우고 QA 프로세스를 수립한다.
2. AI QA 에이전트를 활용하여 반복 작업을 자동화하는 워크플로우를 설계한다.
   - 에이전트가 테스트 실패를 분류하고 스펙, 셀렉터 변경으로 인한 실패를 수리하며, LLM judge가 수리 결과를 채점한다.
3. 생성된 산출물을 체계적으로 관리하고 식별한 이슈의 중요도를 분류하여 지속적으로 추적, 모니터링한다.
4. 프로세스를 지속적으로 개선하여 안정적인 QA 워크플로우를 완성시킨다.

## 규칙 문서와 폴더
- 계층: 전역 `~/.claude/CLAUDE.md`(모든 프로젝트 공통) > 이 파일(프로젝트 공통) > 테스트 종류별 폴더 `CLAUDE.md` > 서브에이전트(`.claude/agents/`)와 스킬(`.claude/skills/`)
  - 위 계층의 내용을 아래 계층에 다시 쓰지 않는다. 한 테스트 종류에만 해당하면 그 폴더 `CLAUDE.md`에, 한 역할이나 작업에만 해당하면 그 에이전트나 스킬에 쓴다.
- 테스트 종류별 폴더(현재 두 종류)
  - [playwright-demo/CLAUDE.md](playwright-demo/CLAUDE.md): UI e2e(Playwright, pytest)
  - [api-demo/CLAUDE.md](api-demo/CLAUDE.md): API(httpx, pytest)
- `.claude/` 폴더
  - `agents/`: 서브에이전트 정의와 역할 행동 지침
  - `skills/`: `/이름`으로 실행하는 작업 절차와 그 작업의 규칙. 스킬 폴더 안의 SKILL.md 하나에 둔다.
  - `guides/`: 산출물 작성 형식(백로그, Jira 이슈). 쓰는 단계에서만 읽는다.
  - `docs/`: 참고 자료. 기능 스펙(`specs/v5/`), 스펙 분석(`spec analysis/`), 백로그(`backlog/`), 설계 문서, 문서 지도(`README.md`)
  - `.claude/rules/`는 세션마다 자동으로 읽히므로 쓰지 않는다.
- `scripts/`: 점검과 리포트 스크립트. 시트와 네트워크를 직접 읽지 않고 로컬 파일(CSV, JSON, md)만 처리한다.
- 어떤 작업에 어떤 문서와 스크립트를 쓰는지는 `.claude/docs/README.md`(문서 지도)에 있다. 위치를 모르면 먼저 본다.

## 판단 기준
- 동작의 정답은 스펙이다. 스펙과 라이브가 다르면 스펙을 따르고, 불일치는 백로그에 올린다. 종류별 스펙 문서와 확인 순서는 각 폴더 `CLAUDE.md`에 있다.
- 기능 요구사항(User Story, AC)은 `.claude/docs/specs/v5/00_index.md`에서 해당 기능 파일만 골라 읽는다. 기능 관련 작업 중 동작을 모르거나 판단이 필요하면 먼저 이 파일을 확인한다. 통째로 읽거나 기억으로 쓰지 않는다. 스펙에 없으면 라이브로 확인하고 안건으로 올린다.
- 서비스 소스의 기준 변형은 `sprint5`다. 서비스 레포의 `sprint5-with-bugs` 같은 다른 변형은 분석, TC, 실패 분류의 기준으로 쓰지 않는다.
- 서비스 소스 코드는 원인 추정의 근거로만 쓰고, 기대 동작의 근거로 쓰지 않는다.
- 라이브 데이터 값(상품명, 가격, 건수, id, 시각)은 DB 리셋과 데이터 변경으로 바뀌므로 기대결과와 어설션에 고정값으로 쓰지 않는다. 스키마와 요청 조건에서 정해지는 관계(필터, 정렬, 단건-목록 일치)만 확인한다.
- 라이브에서 확인한 사실은 확인 날짜와 함께 기록한다. 문서(노션, Jira, wiki, 백로그, 보고서)에는 날짜만 쓰고 시각은 쓰지 않는다.
- 저장소와 외부 문서에는 정의되지 않은 약어나 작업용 라벨(ex: 배치 번호, 분류 기호)을 쓰지 않는다. 새 용어가 필요하면 정의한 문서를 함께 가리킨다.
- 확인하지 않은 것은 '추정' 또는 '후보'로 쓰고 확인 방법을 붙인다. 추측을 사실처럼 쓰지 않는다.
- 이슈 중요도는 High/Medium/Low 3단계이고, 결함이 실제로 일으키는 영향으로 정한다. 기준은 `.claude/guides/issue-severity.md`에 있다.

## 승인과 안전
- 사용자 승인 지점: TC 확정, 전체 테스트 실행, Jira 등록(Notion "이슈 검수" DB의 "검토 결과"), wiki 게시, 커밋과 PR
- 의미 있는 작업 하나(스킬이나 에이전트 완성, 스크립트 배치 통과, 문서 구조 변경)가 끝나면 커밋 단위와 메시지를 제안하고 승인받아 커밋한다. 세션 마무리 때 커밋 안 된 변경이 있으면 알린다.
- 결제 확정, 계정 잠금(로그인 3회 실패) 같은 되돌릴 수 없는 동작은 하지 않고 보고한다. 단, 데모 사이트 결제 확정은 TC가 검증 대상으로 정한 테스트 코드와 `/flow-map` 흐름 탐색에서 허용한다(그 밖의 에이전트 탐색 중 확정은 금지).
- 테스트가 만든 데이터는 테스트가 끝나면 정리한다. 방법은 각 폴더 `CLAUDE.md`에 있다.
- 계정 값은 각 폴더의 `.env`에 있고, 계정별 용도는 각 폴더 `CLAUDE.md`에 있다. Slack 봇 토큰은 루트 `.env`의 `SLACK_BOT_TOKEN`이다. 값은 출력하지 않는다.

## 산출물과 위치
- TC: 테스트 종류별 구글 시트. 주소는 각 폴더 `CLAUDE.md`에 있다.
  - 테스트 하나가 TC 하나다. TC ID 접두어는 시트 탭과 같게 쓰고(현재 `UI_`, `API_`), 테스트에 시트 ID를 그대로 연결한다(pytest는 `@pytest.mark.tc("ID")`).
  - 점검용 CSV는 `https://docs.google.com/spreadsheets/d/<파일 ID>/gviz/tq?tqx=out:csv&sheet=<탭>`으로 받는다.
- 전체 실행 결과: UI와 API를 따로 실행해 `test-runs/<일시>-<ui|api>/`에 보관한다(git 제외). 요약은 Slack 채널 `C0C7590K189`에 올린다(`/test-run`). 스펙에 정확한 기대결과가 없는 TC는 `spec_undefined` 마커로 전체 실행에서 뺀다.
- 스펙 분석: `.claude/docs/spec analysis/ui|api/`. 실행 이력은 `analysis-log.md`와 Notion "Document-Analyzer 분석" DB.
- 이슈 후보: `.claude/docs/backlog/`(인덱스 `00_index.md`, 형식 `.claude/guides/backlog-format.md`)
- 리얼버그: Jira 프로젝트 `QA`, 이슈 유형 "버그"
  - 사라가 실패를 Notion "테스트 실행" DB(`collection://de613125-b2b2-40af-842a-9f1265e9376c`)와 "이슈 검수" DB(`collection://beb91aef-0900-4169-95f4-4bbbedc2d1fc`)에 올리고, "검토 결과"로 사용자가 승인했거나 real-bug로 분류 수정한 행만 Jira에 등록한 뒤 Jira 키를 적는다.
  - 제목, 본문, 등록 전 중복 확인은 `.claude/guides/jira-issue-format.md`(샘플 QA-4), 레이블, 에픽, 증거 형식은 각 폴더 `CLAUDE.md`를 따른다.
- 안건과 결과 보고서: Confluence
  - 결과 보고서는 UI는 "UI Test Results"(12222506), API는 "API Test Results"(12288047) 하위에 Iteration마다 `YYYYMMDD_<UI|API>_Iteration<N>_Test Result Report`, 사인오프용은 `YYYYMMDD_<UI|API>_Test Result Report`로 쓴다. 형식은 `.claude/guides/test-report-format.md`(템플릿 11632643의 원본)다.
- 작업 일지: Notion "QA AI Agent 업무 일지"(아래 "세션 마무리")

## 실패 분류와 가드레일
- 실패는 반드시 먼저 `test-triage` 스킬의 6분류로 분류한다. 결과 보고서에서는 4그룹으로 묶는다.
  - 리얼버그: `real-bug` / 테스트버그: `test-bug`, `selector-drift`, `spec-change` / flaky: `timing`, `env`
  - 스펙이 정한 값과 라이브가 다르면 real-bug, 스펙이 기대결과를 정하지 않았으면 안건이다(`.claude/guides/backlog-format.md` 3번). 안건 TC는 `spec_undefined` 마커로 전체 실행에서 빼고 보고서에 N/A로 쓴다.
- 리얼버그만 Jira에 올린다. 테스트버그와 flaky는 보고서에만 쓰고, 안건은 wiki 문서로 올린다.
- **`real-bug`로 분류되면 코드를 수정하지 않는다.** 근거와 함께 보고만 한다.
- 수리할 때 실패를 숨기지 않는다. 어설션 삭제·약화, `skip`, 임의 `xfail`을 금지한다. 백로그에 등록된 real-bug만 xfail로 고정할 수 있고, Jira에 등록되면 xfail을 풀고 `@pytest.mark.issue("QA-N")`로 표시해 실패로 집계한다(방법은 `script-write` 스킬의 "xfail 규칙"). 종류 전용 금지 항목은 각 폴더 `CLAUDE.md`에 있다.
- judge는 항상 **별도 세션**에서 실행한다(수리 에이전트의 대화 맥락을 물려주지 않는다).
- CI 헤드리스에서는 Confluence(MCP OAuth)를 건드리지 않는다. repo 수정과 PR까지만 한다.

## 세션 마무리
- 작업 일지 DB: Notion "QA AI Agent 업무 일지"(`collection://a4482c3b-9a5a-40f0-979c-6e8196b78770`, "AI Report" 페이지 하위).
- 세션 이름은 `session-notes.md` 목록(sara/gugu/study/qq 등) 기준이다.
- `Phase`, `상태` 속성은 기존 항목 값을 참고해 채운다.

## 코드 스타일
- 현재 코드 스타일을 따른다.
- 불필요한 대규모 리팩토링을 피한다.
- 공개 API 변경 시 문서와 테스트를 함께 갱신한다.
