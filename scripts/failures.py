#!/usr/bin/env python3
"""실패한 테스트별로 triage/수리에 필요한 자료를 한 곳에 모은다.

repo 루트에서:  playwright-demo/.venv/bin/python scripts/failures.py [nodeid substring]

읽는 것: playwright-demo/test-results/report.json (pytest-json-report)
출력: JSON (stdout) — 실패 목록. 각 항목:
  nodeid, file, lineno, tc (마커에서 추출), longrepr,
  crash{path,lineno,message}, dom_snapshot(경로|null), artifacts[trace/screenshot 경로]

파일을 수정하지 않는다. 에이전트 triage 커맨드의 입력 생성 전용.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "playwright-demo"
REPORT = DEMO / "test-results" / "report.json"
SNAP_DIR = DEMO / "test-results" / "dom-snapshots"

TC_MARKER_RE = re.compile(r'@pytest\.mark\.tc\(\s*["\']([^"\']+)["\']\s*\)')
DEF_RE = re.compile(r"^\s*def\s+(test_\w+)\s*\(")


def tc_for(nodeid: str) -> str | None:
    """nodeid (tests/foo_test.py::test_bar[chromium]) → 함수 위 tc 마커 값."""
    m = re.match(r"([^:]+)::([A-Za-z0-9_]+)", nodeid)
    if not m:
        return None
    path = DEMO / m.group(1)
    func = m.group(2)
    if not path.exists():
        return None
    pending: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        mk = TC_MARKER_RE.search(line)
        if mk:
            pending.append(mk.group(1))
            continue
        d = DEF_RE.match(line)
        if d:
            if d.group(1) == func:
                return pending[0] if pending else None
            pending = []
    return None


def slug(nodeid: str) -> str:
    for a, b in (("/", "_"), ("::", "__"), ("[", "_"), ("]", ""), (" ", "_")):
        nodeid = nodeid.replace(a, b)
    return nodeid


def artifacts_for(nodeid: str) -> list[str]:
    base = DEMO / "test-results"
    if not base.exists():
        return []
    stem = nodeid.split("::")[-1].split("[")[0]
    hits: list[str] = []
    for p in base.rglob("*"):
        if p.is_file() and stem in p.name and p.suffix in {".zip", ".png", ".webm"}:
            hits.append(str(p.relative_to(ROOT)))
    return sorted(hits)


def main() -> int:
    if not REPORT.exists():
        print(json.dumps({"error": f"{REPORT.relative_to(ROOT)} 없음. 먼저 pytest 실행."}))
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    needle = sys.argv[1] if len(sys.argv) > 1 else ""

    out = []
    for t in data.get("tests", []):
        if t.get("outcome") not in {"failed", "error"}:
            continue
        nodeid = t["nodeid"]
        if needle and needle not in nodeid:
            continue
        call = t.get("call") or t.get("setup") or {}
        crash = call.get("crash") or {}
        snap = SNAP_DIR / f"{slug(nodeid)}.json"
        out.append(
            {
                "nodeid": nodeid,
                "file": nodeid.split("::")[0],
                "lineno": t.get("lineno"),
                "tc": tc_for(nodeid),
                "outcome": t["outcome"],
                # longrepr 에 assertion + Playwright call log + aria snapshot 이 모두 들어있음
                "longrepr": call.get("longrepr", ""),
                "crash_at": {"path": crash.get("path"), "lineno": crash.get("lineno")},
                "dom_snapshot": str(snap.relative_to(ROOT)) if snap.exists() else None,
                "artifacts": artifacts_for(nodeid),
            }
        )

    print(json.dumps({"summary": data.get("summary"), "failures": out}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
