#!/usr/bin/env python3
"""사람이 읽는 테스트 실행 결과 리포트를 만든다 (테스트플랜의 "Test 결과" 단계).

repo 루트에서:  python3 scripts/gen_test_report.py [--type ui|api]   (기본 ui, 표준 라이브러리만 사용)

읽는 것: <playwright-demo|api-demo>/test-results/report.json (pytest-json-report)
출력: 같은 폴더의 test-results/test-report.md (덮어쓰기)

pytest.ini 의 --html=test-results/report.html 은 이 리포트의 자매품 —
report.html 은 CI 아티팩트로 보기 좋은 원본, 이 md는 TC 단위로 재구성한 요약.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DEMOS, ROOT, tc_for  # noqa: E402

OUTCOME_LABEL = {
    "passed": "✅ pass",
    "failed": "❌ fail",
    "error": "🟥 error",
    "skipped": "⏭️ skip",
    "xfailed": "🟡 xfail",
    "xpassed": "🟡 xpass",
}


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--type", choices=sorted(DEMOS), default="ui")
    kind = ap.parse_args().type
    demo = DEMOS[kind]
    results = demo / "test-results"
    report = results / "report.json"
    out = results / "test-report.md"

    if not report.exists():
        print(f"{report.relative_to(ROOT)} 없음. 먼저 pytest 실행.", file=sys.stderr)
        return 1

    data = json.loads(report.read_text(encoding="utf-8"))
    tests = data.get("tests", [])
    summary = data.get("summary", {})

    created = data.get("created")
    run_time = (
        datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%d")
        if created
        else "알 수 없음"
    )
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    commit = git("rev-parse", "--short", "HEAD") or "?"

    total = summary.get("total", len(tests))
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0) + summary.get("error", 0)
    skipped = summary.get("skipped", 0)
    xfailed = summary.get("xfailed", 0)
    duration = data.get("duration", 0)

    lines: list[str] = []
    lines.append(f"# 테스트 실행 결과 ({kind.upper()})")
    lines.append("")
    lines.append("> `scripts/gen_test_report.py` 로 자동 생성. 직접 편집하지 말 것.")
    lines.append("")
    lines.append(f"- **실행 시각**: {run_time}")
    lines.append(f"- **브랜치 / 커밋**: `{branch}` / `{commit}`")
    lines.append(f"- **소요 시간**: {duration:.1f}s")
    lines.append(f"- **결과**: {passed}/{total} pass" + (f", {failed} fail" if failed else "") + (f", {skipped} skip" if skipped else "") + (f", {xfailed} xfail" if xfailed else ""))
    lines.append("")

    lines.append("## TC 별 결과")
    lines.append("")
    lines.append("| TC | 결과 | 소요(s) | 테스트 |")
    lines.append("|---|---|---|---|")

    rows = []
    for t in tests:
        nodeid = t["nodeid"]
        tc_id = tc_for(nodeid, demo) or "—"
        outcome = t.get("outcome", "?")
        call = t.get("call") or {}
        dur = call.get("duration", t.get("setup", {}).get("duration", 0)) or 0
        rows.append((tc_id, outcome, dur, nodeid))

    # TC 순서(API_01, API_02 ...) 로 정렬, TC 없는 건 뒤로
    rows.sort(key=lambda r: (r[0] == "—", r[0]))

    for tc_id, outcome, dur, nodeid in rows:
        label = OUTCOME_LABEL.get(outcome, outcome)
        lines.append(f"| {tc_id} | {label} | {dur:.2f} | `{nodeid}` |")

    fails = [r for r in rows if r[1] in ("failed", "error")]
    lines.append("")
    lines.append("## 실패 상세")
    lines.append("")
    if not fails:
        lines.append("없음 — 전부 통과.")
        lines.append("")
    else:
        for t in tests:
            nodeid = t["nodeid"]
            if t.get("outcome") not in ("failed", "error"):
                continue
            call = t.get("call") or t.get("setup") or {}
            crash = call.get("crash") or {}
            tc_id = tc_for(nodeid, demo) or "—"
            lines.append(f"### {nodeid} ({tc_id})")
            lines.append("")
            lines.append(f"- 위치: `{crash.get('path', '')}:{crash.get('lineno', '')}`")
            lines.append(f"- 메시지: `{crash.get('message', '').splitlines()[0] if crash.get('message') else ''}`")
            lines.append("")

    lines.append("## 산출물")
    lines.append("")
    rel = demo.relative_to(ROOT)
    lines.append(f"- HTML: `{rel}/test-results/report.html`")
    lines.append(f"- JSON: `{rel}/test-results/report.json`")
    if kind == "ui":
        lines.append(f"- 실패 DOM 스냅샷: `{rel}/test-results/dom-snapshots/`")
        lines.append("- triage 입력: `python scripts/failures.py`")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({passed}/{total} pass, {failed} fail, {skipped} skip)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
