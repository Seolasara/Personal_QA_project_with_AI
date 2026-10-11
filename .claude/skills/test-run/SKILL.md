---
name: test-run
description: 전체 테스트 실행 파이프라인. 사용자가 전체 테스트 실행을 요청하거나 /test-run을 실행할 때 쓴다. UI·API pytest를 실행하고 결과를 보관한 뒤 Slack으로 요약을 보낸다.
argument-hint: "[ui|api]"
---

# /test-run
대상: `$ARGUMENTS` (`ui` 또는 `api`). UI와 API는 따로 실행하고, 실행 하나가 보관본·노션 행·Slack 메시지·결과 보고서 하나가 된다. 비어 있으면 종류를 묻는다.
메인 세션이 명령으로 실행한다. 모델 판단이 필요 없는 단계라 서브에이전트를 쓰지 않는다.

## 1. 승인 확인
- 전체 실행은 루트 "승인과 안전"의 승인 지점이다. 사용자가 `/test-run`을 직접 실행했거나 이 대화에서 실행을 승인했을 때만 진행한다.
- 결제 확정 TC가 실행될 때마다 지울 수 없는 인보이스가 생긴다. 실행은 1회만 한다.

## 2. 사전 점검
하나라도 실패하면 실행하지 않고 보고한다.
- venv: `playwright-demo/.venv/bin/pytest`, `api-demo/.venv/bin/pytest`가 있다.
- `.env`: 각 폴더 `.env.example`의 키가 `.env`에 모두 있고 값이 비어 있지 않다. 키 이름만 확인하고 값은 출력하지 않는다.
  - ex: `grep -c '^TOOLSHOP_PASSWORD=.\+' playwright-demo/.env`
- 사이트: `https://practicesoftwaretesting.com`과 `.env`의 `API_BASE_URL`이 응답한다(`curl -s -o /dev/null -w '%{http_code}'`). 5xx나 응답 없음이면 env로 보고한다.
- 커밋 안 된 변경이 있으면 결과 보고에 적는다. 리포트의 커밋 해시와 실제 코드가 다를 수 있다.

## 3. 실행
- 대상 폴더에서 해당 venv로 1회 실행한다. 스펙에 정확한 기대결과가 없는 TC(`spec_undefined` 마커)는 뺀다. Jira 등록 결함 테스트(`issue` 마커)는 빼지 않는다(Iteration 2, 3의 재검증 대상).
  - UI: `cd playwright-demo && .venv/bin/pytest -m "not spec_undefined"`
  - API: `cd api-demo && .venv/bin/pytest -m "not spec_undefined"`
- `pytest.ini`의 addopts(리포트, trace, 스크린샷)를 그대로 쓴다. `-o addopts=""`를 쓰지 않는다.
- 실패한 테스트를 다시 실행해 통과를 만들지 않는다. 코드와 TC는 수정하지 않는다.

## 4. 리포트와 보관
- 리포트: `python3 scripts/gen_test_report.py --type <ui|api>`로 그 폴더의 `test-results/test-report.md`를 만든다.
- 보관: 그 폴더의 `test-results/`를 `test-runs/<YYYY-MM-DD-HHMM>-<ui|api>/`로 복사한다. 다음 실행이 `test-results/`를 지우므로, 이후 triage와 결과 보고서는 보관본을 근거로 쓴다.
- `test-runs/`는 git에 올리지 않는다.

## 5. Slack 보고
- 요약 텍스트: `python3 scripts/run_summary.py --<ui|api> <보관본>/report.json --<ui|api>-csv <시트 CSV> --title "<실행 목적 제목>"`
  - 시트 CSV는 루트 `CLAUDE.md`의 CSV 주소로 임시 경로에 받는다. 실패 상세에 TC 기능명이 한 줄 붙는다.
  - 제목은 실행 목적을 대괄호로 구분해 쓴다. Iteration 실행이면 `Iteration<N> <UI|API> 전체 테스트 결과`, 스크립트 작성 뒤 확인 실행이면 `<UI|API> 스크립트 작성 전체 테스트 실행 결과`. 목적이 다른 실행은 그 목적을 짧게 쓴다.
  - 출력의 `---THREAD---` 위는 본문, 아래는 실패 상세(이유, 근거, 백로그 링크)다.
  - 백로그 링크는 GitHub 현재 브랜치 기준이라, 백로그를 고쳤으면 push한 뒤에 보낸다.
- 루트 `CLAUDE.md` "산출물과 위치"의 Slack 채널에 본문을 올리고, 실패 상세가 있으면 그 메시지의 스레드 답글로 올린다.
- 본문 메시지의 채널과 ts를 `test-runs/<일시>/slack.json`에 저장한다(`{"channel": "...", "ts": "..."}`). `/test-triage`와 `/issue-register`가 같은 스레드에 답글을 단다.
- HTML 리포트 첨부: 보관한 `report.html`을 같은 스레드에 올린다. 토큰은 루트 `.env`의 `SLACK_BOT_TOKEN`에서 읽고 출력하지 않는다.
  1. `T=$(grep '^SLACK_BOT_TOKEN=' .env | cut -d= -f2-)`
  2. 파일마다 `curl -s -H "Authorization: Bearer $T" "https://slack.com/api/files.getUploadURLExternal?filename=<ui|api>-report.html&length=<바이트 수>"`로 `upload_url`, `file_id`를 받고 `curl -s -F file=@<경로> "<upload_url>"`로 올린다.
  3. `curl -s -X POST -H "Authorization: Bearer $T" -H 'Content-type: application/json; charset=utf-8' https://slack.com/api/files.completeUploadExternal --data '{"files":[{"id":"<file_id>","title":"<UI|API> report"}],"channel_id":"<채널>","thread_ts":"<본문 ts>"}'`
  - 토큰이 없거나 업로드가 실패하면 첨부 없이 진행하고 결과 보고에 적는다.
- 계정, 토큰, `.env` 값은 올리지 않는다. 요약 스크립트가 실패 메시지의 이메일과 토큰 형태를 가리지만, 올리기 전에 한 번 더 확인한다.
- Slack 전송이 실패하면 채팅 보고에 그 사실을 적는다.

## 6. 노션 "테스트 실행" 행
- "테스트 실행" DB(`collection://de613125-b2b2-40af-842a-9f1265e9376c`)에 행 1개를 만든다.
  - 속성은 `.claude/guides/notion-test-record-format.md` 2번을 따른다. 실행 구분(스크립트 작성 후 전체 시범 실행 또는 Iteration N)과 종류(UI, API)를 채운다. 실행 제목은 `YYYY-MM-DD HH:MM UI <실행 구분>` 형식이고, 결과는 해당 종류 칸에 `40/45 통과, 실패 5`(xfail은 실패에 포함) 형식으로 쓴다.
  - 본문은 요약과 통과 현황까지 쓴다. 실패 현황은 `/test-triage`가 채운다.
  - 진행 상태: 실패나 xpass가 있으면 "분류 대기", 없으면 "등록 완료"(분류할 실패 없음)

## 7. 결과 보고
채팅에는 Slack 본문과 같은 요약을 쓰고 아래를 덧붙인다.
1. 사전 점검 결과(커밋 안 된 변경 포함)
2. 보관 경로, Slack 전송 결과, 노션 실행 행
3. 다음 단계: 실패나 xpass가 있으면 `/test-triage test-runs/<일시>-<ui|api>`로 분류를 시작할지 묻는다.
