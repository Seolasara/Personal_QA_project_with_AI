# 테스트 플랜

> 원본 Confluence: [QA 플랜](https://seolakim195.atlassian.net/wiki/spaces/~712020ed6696cba1a44b4683098b6834093514/pages/65702) (page 65702),
> [QA 개요 및 프로세스](https://seolakim195.atlassian.net/wiki/spaces/~712020ed6696cba1a44b4683098b6834093514/pages/65666) (page 65666).
> 이 파일이 repo 상의 사본이며, 변경은 `/tc-sync`로 양방향 동기화한다.

## 목적

경험이 부족한 신입 QA 관점에서 **QA 전반 흐름 + 테스트 자동화 + AI Agent 기반 프로세스 개선 + LLM Judge 평가**를
직접 구축하고 검증하는 자기계발 프로젝트. AI를 단순 자동화 도구가 아니라 비즈니스 리스크 식별·예방 수단으로 활용하는 것을 지향한다.

## 대상

공개 데모 사이트 <https://practicesoftwaretesting.com> (Toolshop). 앱 스펙은 고정이므로, 유지보수 상황은
결함 주입(fault injection)으로 재현한다.

## 플랜 단계

| # | 단계 | 산출물 |
|---|---|---|
| 1 | 요구사항 및 스펙 정리 | Confluence 개요/프로세스 |
| 2 | Test Case 설계 | `testcases/QA-*.md` (13건), Confluence page 360539 |
| 3 | Test Script 작성 (Python + Playwright) | `playwright-demo/` |
| 4 | TC·스크립트 보수 작업 with AI QA Agent | `.claude/skills/`, `.claude/commands/` |
| 5 | Manual + Automation 테스트 수행 | `test-results/report.json`, trace |
| 6 | 이슈 및 추적 | GitHub Issues, `traceability.md` |
| 7 | 테스트 결과 | 결과 리포트 |
| 8 | LLM Judge 결과 분석 | `eval/` judge 골든셋 + 일치율 |
| 9 | 테스트 결과 보고서 | Confluence |
| 10 | QA 회고 | Confluence |

확장 목표(SHOULD): MCP 연결 + CI/CD(GitHub Actions + Jenkins).

## 범위

- **In**: 로그인/로그아웃, 상품 조회·필터, 상품 상세, 장바구니, 결제(Cash on Delivery) 해피패스 + 로그인 음성 케이스
- **Out**: 회원가입, 관리자 기능, 카드 결제, 다국어, 성능/보안 테스트

## 테스트 유형

| 유형 | 방법 |
|---|---|
| 기능 (UI) | Playwright(pytest), `data-test` 셀렉터 우선 |
| 스모크 | `pytest -m smoke` — PR 게이트 |
| 회귀 | 전체 스위트 (Jenkins) |
| 에이전트 보수 검증 | 결함 주입 eval set + LLM judge |

## 환경

- Python 3.13, Playwright 1.62 (버전 핀 고정), Chromium
- 로컬: `playwright-demo/.venv`
- CI: GitHub Actions(스모크) + Jenkins(전체)

## 종료 조건

- P1 TC 100% 자동화 및 통과
- 결함 주입 eval에서 에이전트 분류(triage) 정확도 및 수리 판정(judge) 일치율 측정치 확보
- `real-bug` 케이스에서 에이전트가 코드를 수정하지 않고 리포트만 하는지 확인
