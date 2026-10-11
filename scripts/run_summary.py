#!/usr/bin/env python3
"""전체 테스트 실행 결과를 Slack 메시지용 요약 텍스트로 만든다. 네트워크는 쓰지 않고 report.json만 읽는다.

사용:  python3 scripts/run_summary.py --ui <UI report.json> --api <API report.json> --title "<실행 목적 제목>"
- --title: 본문 첫 줄 제목. 실행 목적을 쓴다(ex: "Iteration1 UI 전체 테스트 결과", "UI 스크립트 작성 전체 테스트 실행 결과"). 없으면 "테스트 실행 결과".
- 출력(stdout) 첫 블록은 본문 메시지, `---THREAD---` 아래는 스레드 답글(실패 상세)이다. 실패가 없으면 스레드는 비어 있다.
- 실패 상세의 이유는 실패 메시지에서 규칙으로 뽑은 원인 후보이고, 확정 분류는 `/test-triage`가 한다.
- 근거는 실패 위치(파일:줄)와, TC ID가 백로그 인덱스(`.claude/docs/backlog/00_index.md`)에 있으면 그 번호다.
  번호에는 GitHub의 해당 항목 링크(현재 브랜치 기준)를 건다. 링크는 push된 내용만 열린다.
- 실패 메시지의 이메일, 토큰 형태 문자열은 가린다.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.parse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DEMOS, ROOT, tc_for  # noqa: E402

FAIL = ("failed", "error")
MASKS = (
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<email>"),
    (re.compile(r"(?i)bearer\s+[\w.-]+"), "Bearer <token>"),
    (re.compile(r"eyJ[\w-]{10,}\.[\w-]+\.[\w-]+"), "<token>"),
)


def mask(text: str) -> str:
    for pattern, repl in MASKS:
        text = pattern.sub(repl, text)
    return text


def crash_of(test: dict) -> dict:
    stage = test.get("call") or test.get("setup") or {}
    return stage.get("crash") or {}


def reason(test: dict) -> str:
    """실패 메시지에서 원인 후보를 명사형 한 구절로 뽑는다."""
    msg = crash_of(test).get("message", "").strip()
    first = msg.splitlines()[0] if msg else ""
    if "ValidationError" in first:
        lines = msg.splitlines()
        fields = [l.strip() for i, l in enumerate(lines[1:], 1)
                  if l and not l.startswith(" ") and i + 1 < len(lines) and lines[i + 1].startswith("  ")]
        kinds = "필드 누락" if "Field required" in msg else "미정의 필드" if "Extra inputs" in msg else "타입 불일치"
        return f"응답 스키마 불일치({kinds}: {', '.join(fields[:3])})"
    m = re.match(r"assert (\d{3}) == (\d{3})$", first)
    if m and "status_code" in msg:
        return f"상태 코드 불일치(기대 {m.group(2)}, 실제 {m.group(1)})"
    m = re.search(r"expected to have (?:Value|Text) '([^']*)'.*?Actual value: ([^\n]*)", msg, re.S)
    if m:
        return f"값 불일치(기대 {m.group(1)[:30]}, 실제 {m.group(2).strip()[:30]})"
    for key, label in (("to be visible", "요소 미노출"), ("to be hidden", "요소 노출 지속"),
                       ("to be enabled", "요소 비활성"), ("to be disabled", "요소 활성 지속"),
                       ("to be checked", "체크 상태 불일치")):
        if f"expected {key}" in msg or f"expected to {key[3:]}" in msg or key in first:
            return label
    if re.search(r"ReadTimeout|ConnectError|ConnectTimeout|5\d\d Server Error", msg):
        return "서버 응답 없음 또는 5xx(env 후보)"
    if "Timeout" in first:
        return "요소 대기 시간 초과"
    m = re.search(r"Differing items:\s*\n\s*\{'(\w+)': '([^']*)'\} != \{'\w+': '([^']*)'\}", msg)
    if m:
        return f"응답 바디 불일치({m.group(1)}: 기대 \"{m.group(3)[:40]}\", 실제 \"{m.group(2)[:40]}\")"
    if re.match(r"(AssertionError: )?assert [\[{]", first):
        return "응답 바디 불일치"
    if first.startswith("AssertionError: "):
        return first[len("AssertionError: "):][:80]
    return first.split(":")[0][:60] or "원인 불명"


def backlog_by_tc() -> dict[str, list[str]]:
    index = ROOT / ".claude" / "docs" / "backlog" / "00_index.md"
    found: dict[str, list[str]] = {}
    if index.exists():
        for line in index.read_text(encoding="utf-8").splitlines():
            m = re.match(r"- (#\d+) .*\(([^)]*)\)\s*$", line)
            if m:
                for tc in re.findall(r"[A-Z]+_\d+", m.group(2)):
                    found.setdefault(tc, []).append(m.group(1))
    return found


REPO_URL = "https://github.com/Seolasara/Personal_QA_project_with_AI"
BACKLOG_DIR = ROOT / ".claude" / "docs" / "backlog"


def gh_anchor(heading: str) -> str:
    """GitHub 마크다운 제목 앵커 규칙: 소문자, 문자·숫자·공백·하이픈·밑줄 외 제거, 공백은 하이픈."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def backlog_link(number: str, branch: str) -> str:
    """'#13' → Slack 링크 `<url|#13>`. 항목 파일을 못 찾으면 번호만 쓴다."""
    for f in sorted(BACKLOG_DIR.glob("0[1-5]_*.md")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"### {number} "):
                path = urllib.parse.quote(f"{f.relative_to(ROOT)}")
                anchor = urllib.parse.quote(gh_anchor(line[4:]))
                return f"<{REPO_URL}/blob/{branch}/{path}#{anchor}|{number}>"
    return number


def evidence(test: dict, tc: str, backlog: dict[str, list[str]], branch: str) -> str:
    crash = crash_of(test)
    parts = []
    if crash.get("path"):
        parts.append(f"`{Path(crash['path']).name}:{crash.get('lineno', '')}`")
    if tc in backlog:
        parts.append("백로그 " + ", ".join(backlog_link(n, branch) for n in backlog[tc]))
    return ", ".join(parts) or "위치 정보 없음"


def load(kind: str, path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    demo = DEMOS[kind]  # nodeid 기준 폴더. 보관본(test-runs/)을 읽어도 마커는 현재 테스트 코드에서 찾는다
    tests = data.get("tests", [])
    summary = data.get("summary", {})
    rows = []
    for t in tests:
        tc = tc_for(t["nodeid"], demo) or "—"
        rows.append((tc, t.get("outcome", "?"), t["nodeid"].split("::")[-1], t))
    rows.sort(key=lambda r: (r[0] == "—", r[0]))
    return {
        "kind": kind,
        "total": summary.get("total", len(tests)),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0) + summary.get("error", 0),
        "xfailed": summary.get("xfailed", 0),
        "xpassed": summary.get("xpassed", 0),
        "skipped": summary.get("skipped", 0),
        "duration": data.get("duration", 0),
        "created": data.get("created"),
        "fails": [r for r in rows if r[1] in FAIL],
        "xpasses": [r for r in rows if r[1] == "xpassed"],
    }


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return "?"


def count_line(r: dict) -> str:
    parts = [f"{r['passed']}/{r['total']} 통과"]
    for key, label in (("failed", "실패"), ("xfailed", "xfail"), ("xpassed", "xpass"), ("skipped", "skip")):
        if r[key]:
            parts.append(f"{label} {r[key]}")
    return f"*{r['kind'].upper()}*: " + ", ".join(parts) + f" ({r['duration'] / 60:.1f}분)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ui", type=Path)
    ap.add_argument("--api", type=Path)
    ap.add_argument("--title", default="테스트 실행 결과", help="실행 목적 제목. ex: 'Iteration1 UI 전체 테스트 결과'")
    args = ap.parse_args()

    results = [load(k, p) for k, p in (("ui", args.ui), ("api", args.api)) if p]
    if not results:
        ap.error("--ui 또는 --api 중 하나는 필요하다")

    created = max((r["created"] or 0) for r in results)
    when = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M") if created else "알 수 없음"
    total_fail = sum(r["failed"] for r in results)
    total_xpass = sum(r["xpassed"] for r in results)
    verdict = "실패 없음" if not total_fail else f"실패 {total_fail}건, 원인 분류 필요"

    body = [
        f"*[{args.title}]* ({when}, `{git('rev-parse', '--abbrev-ref', 'HEAD')}` / `{git('rev-parse', '--short', 'HEAD')}`)",
        *[f"• {count_line(r)}" for r in results],
        f"• 판정: {verdict}",
    ]
    if total_xpass:
        body.append(f"• xpass {total_xpass}건: 백로그 갱신 대상(버그 수정 신호)")

    backlog = backlog_by_tc()
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    thread = []
    for r in results:
        for tc, _, name, t in r["fails"]:
            thread.append(f"• [{r['kind'].upper()}] {tc} `{name}`")
            thread.append(f"    ◦ 이유: {mask(reason(t))}")
            thread.append(f"    ◦ 근거: {evidence(t, tc, backlog, branch)}")
        for tc, _, name, _t in r["xpasses"]:
            thread.append(f"• [{r['kind'].upper()}] {tc} `{name}`")
            thread.append("    ◦ 이유: XPASS(고정한 버그의 수정 신호)")
            thread.append(f"    ◦ 근거: 백로그 {', '.join(backlog_link(n, branch) for n in backlog.get(tc, ['미등록']))}")

    print("\n".join(body))
    print("---THREAD---")
    if thread:
        print("*실패 상세*")
        print("\n".join(thread))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
