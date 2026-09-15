"""여러 스크립트가 공유하는 최소 헬퍼. (report.json 파싱, TC 마커 역추적 등)

이 파일 자체는 아무것도 출력하지 않는다.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "playwright-demo"
REPORT = DEMO / "test-results" / "report.json"
SNAP_DIR = DEMO / "test-results" / "dom-snapshots"
TESTCASES_DIR = ROOT / "testcases"

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
