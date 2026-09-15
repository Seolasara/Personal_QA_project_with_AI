#!/usr/bin/env python3
"""TC(testcases/*.md) ↔ 테스트(@pytest.mark.tc) 추적성 매트릭스 생성.

repo 루트에서 실행:  python scripts/gen_traceability.py
결과: traceability.md (덮어쓰기)

의존성: pyyaml (playwright-demo/.venv 에 설치돼 있음)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TC_DIR = ROOT / "testcases"
TESTS_DIR = ROOT / "playwright-demo" / "tests"
OUT = ROOT / "traceability.md"

MARKER_RE = re.compile(r'@pytest\.mark\.tc\(\s*["\']([^"\']+)["\']\s*\)')
DEF_RE = re.compile(r"^\s*def\s+(test_\w+)\s*\(")


def load_testcases() -> dict[str, dict]:
    """id -> {title, priority, component, status, test, file}"""
    out: dict[str, dict] = {}
    for md in sorted(TC_DIR.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            print(f"  skip (no frontmatter): {md.name}", file=sys.stderr)
            continue
        fm = yaml.safe_load(text.split("---", 2)[1])
        tc_id = str(fm.get("id", md.stem))
        auto = fm.get("automation") or {}
        out[tc_id] = {
            "title": fm.get("title", ""),
            "priority": fm.get("priority", ""),
            "component": fm.get("component", ""),
            "status": auto.get("status", "unknown"),
            "test": auto.get("test", ""),
            "file": md.name,
        }
    return out


def scan_markers() -> dict[str, list[str]]:
    """tc-id -> [nodeid, ...]  (@pytest.mark.tc 바로 아래 def 를 연결)"""
    out: dict[str, list[str]] = {}
    for py in sorted(TESTS_DIR.glob("*_test.py")):
        rel = py.relative_to(ROOT).as_posix()
        pending: list[str] = []
        for line in py.read_text(encoding="utf-8").splitlines():
            m = MARKER_RE.search(line)
            if m:
                pending.append(m.group(1))
                continue
            d = DEF_RE.match(line)
            if d and pending:
                nodeid = f"{rel}::{d.group(1)}"
                for tc_id in pending:
                    out.setdefault(tc_id, []).append(nodeid)
                pending = []
    return out


def main() -> int:
    tcs = load_testcases()
    markers = scan_markers()

    lines: list[str] = []
    lines.append("# Traceability Matrix")
    lines.append("")
    lines.append("> `scripts/gen_traceability.py` 로 자동 생성. 직접 편집하지 말 것.")
    lines.append("")
    lines.append("| TC | 제목 | 우선순위 | 컴포넌트 | 연결 테스트 | 마커 | 비고 |")
    lines.append("|---|---|---|---|---|---|---|")

    problems: list[str] = []
    for tc_id, tc in tcs.items():
        marked = markers.get(tc_id, [])
        note = ""
        if tc["status"] == "automated":
            if not marked:
                note = "⚠️ 마커 없음"
                problems.append(f"- {tc_id}: automation.status=automated 인데 `@pytest.mark.tc(\"{tc_id}\")` 없음")
            elif tc["test"] and tc["test"] not in marked:
                note = "⚠️ frontmatter test 불일치"
                problems.append(
                    f"- {tc_id}: frontmatter `{tc['test']}` vs 마커 `{', '.join(marked)}`"
                )
        marker_cell = "<br>".join(marked) if marked else "—"
        lines.append(
            f"| {tc_id} | {tc['title']} | {tc['priority']} | {tc['component']} "
            f"| `{tc['test'] or '—'}` | {marker_cell} | {note} |"
        )

    # 마커는 있는데 대응 TC 파일이 없는 경우
    orphan = sorted(set(markers) - set(tcs))
    lines.append("")
    lines.append("## 고아 마커 (TC 파일 없음)")
    lines.append("")
    if orphan:
        for tc_id in orphan:
            lines.append(f"- `{tc_id}` → {', '.join(markers[tc_id])}")
            problems.append(f"- 마커 `{tc_id}` 에 대응하는 testcases/*.md 없음")
    else:
        lines.append("없음")

    lines.append("")
    lines.append("## 커버리지 요약")
    lines.append("")
    total = len(tcs)
    automated = sum(1 for t in tcs.values() if t["status"] == "automated")
    linked = sum(1 for tc_id, t in tcs.items() if markers.get(tc_id))
    lines.append(f"- 전체 TC: {total}")
    lines.append(f"- automated: {automated}")
    lines.append(f"- 마커 연결됨: {linked}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  (TC {total}, linked {linked})")

    if problems:
        print("\n불일치:", file=sys.stderr)
        for p in problems:
            print(p, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
