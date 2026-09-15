# MCP 서버 현황

`claude mcp list` 기준 (2026-09-15).

## 이 프로젝트(`.mcp.json`)에 등록된 것

| 서버 | 연결 | 방식 | 용도 |
|---|---|---|---|
| `atlassian` | https://mcp.atlassian.com/v2/mcp | HTTP, OAuth | Confluence TC 동기화(`/tc-sync`). 최초 사용 시 `/mcp` → `atlassian` → Authenticate |

> `.agents/plugins/confluence_mcp.py`(API 토큰 방식, `confluence` 서버)는 원래 여기 같이
> 등록돼 있었으나 **제거함** — Gemini/Antigravity 전용 설정(`.agents/plugins/confluence/mcp_config.json`)과
> 스크립트/토큰을 공유하고 있어서, Claude Code 쪽 등록을 끊어 두 에이전트의 쓰기 경로를 분리했다.
> 자세한 이유는 [.agents/CLAUDE.md](.agents/CLAUDE.md) 참고.

## 사용자(계정) 레벨에 등록된 것 — 이 프로젝트 전용 아님

이 프로젝트 `.mcp.json`에는 없지만 `claude mcp list`에서 연결되는 것들. 계정 전체 어느
프로젝트에서든 뜬다.

| 서버 | 연결 | 용도 |
|---|---|---|
| `claude.ai Google Drive` | https://drivemcp.googleapis.com/mcp/v1 | Google Drive 문서 접근 |
| `notion` | https://mcp.notion.com/mcp | Notion 페이지/DB 검색·생성 |

## 갱신 방법

```bash
claude mcp list          # 현재 연결 상태 확인
claude mcp --help        # add/remove 등 관리 커맨드
```
새 MCP 서버를 추가/삭제하면 이 파일도 같이 갱신할 것.
