#!/usr/bin/env python3
"""회귀 TC 목록을 만든다. 시트 CSV, 테스트 코드 마커, 백로그, 이전 실행 보관본을 읽는 로컬 처리만 한다.

사용: python3 scripts/regression_set.py --ui-csv <UI.csv> --api-csv <API.csv> [--nodeids ui|api] [--json]
선정 기준(.claude/docs/glossary.md, 노션 "회귀 테스트의 기준 브레인스토밍" 7번)
  1. smoke 마커  2. 중요도 High  3. 결함 주변  4. 실패 이력(test-runs 보관본)  5. 백로그 "회귀 대상"
  - 결함 주변: API는 known issue TC와 같은 엔드포인트 경로, UI는 같은 대분류에서 시트 순서로 앞뒤 2행
제외: spec_undefined(N/A), issue 마커(known issue). 단 백로그 "회귀 대상" TC는 known issue여도 넣는다.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DEMOS, ROOT, tc_for  # noqa: E402

DECO_RE = re.compile(r"^\s*@pytest\.mark\.(\w+)(?:\(\s*[\"']([^\"']*)[\"']\s*\))?")
DEF_RE = re.compile(r"^\s*def\s+(test_\w+)\s*\(")
BACKLOG_DIR = ROOT / ".claude" / "docs" / "backlog"
NEAR = 2  # UI 결함 주변: 시트 순서로 앞뒤 행 수


def parse_tests(kind: str) -> dict[str, dict]:
    """TC ID → {file, func, smoke, issue, spec_undefined}"""
    found: dict[str, dict] = {}
    for path in sorted((DEMOS[kind] / "tests").glob("*_test.py")):
        marks: dict[str, str | bool] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            m = DECO_RE.match(line)
            if m:
                marks[m.group(1)] = m.group(2) if m.group(2) is not None else True
                continue
            d = DEF_RE.match(line)
            if d:
                tc = marks.get("tc")
                if isinstance(tc, str):
                    found[tc] = {
                        "file": f"tests/{path.name}", "func": d.group(1),
                        "smoke": bool(marks.get("smoke")),
                        "issue": marks.get("issue") if isinstance(marks.get("issue"), str) else None,
                        "spec_undefined": bool(marks.get("spec_undefined")),
                    }
                marks = {}
    return found


def read_sheet(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            tid = (r.get("ID") or "").strip().rstrip("*")
            if tid:
                prio = (r.get("중요도") or r.get("Priority") or "").strip()
                path_ = re.sub(r"\{[^}]*\}", "{}", (r.get("엔드포인트") or "").split("?")[0].strip())
                rows.append({"id": tid, "cat": (r.get("대분류") or "").strip(), "prio": prio, "ep": path_})
    return rows


def history(kind: str) -> dict[str, list[str]]:
    """TC ID → 실패·flaky였던 실행 이름들"""
    out: dict[str, list[str]] = {}
    for d in sorted((ROOT / "test-runs").glob(f"*-{kind}")):
        rp = d / "report.json"
        if not rp.exists():
            continue
        for t in json.loads(rp.read_text(encoding="utf-8")).get("tests", []):
            if t.get("outcome") in ("failed", "error", "xfailed", "xpassed", "rerun"):
                tc = tc_for(t["nodeid"], DEMOS[kind])
                if tc:
                    out.setdefault(tc, []).append(d.name)
    return out


def regression_flagged() -> dict[str, str]:
    """백로그에서 '회귀 대상'으로 표시된 항목의 TC ID → 항목 번호"""
    flagged: dict[str, str] = {}
    for f in sorted(BACKLOG_DIR.glob("0[1-4]_*.md")):
        for sec in re.split(r"(?m)^### ", f.read_text(encoding="utf-8"))[1:]:
            num = re.match(r"(#\d+)", sec)
            state = next((l for l in sec.splitlines() if l.startswith("- 분류와 상태")), "")
            if num and "회귀 대상" in state:
                for tc in re.findall(r"\[((?:UI|API)_\d+)\]", sec):
                    flagged[tc] = num.group(1)
    return flagged


def build(kind: str, csv_path: Path, flagged: dict[str, str]) -> dict:
    tests, sheet, hist = parse_tests(kind), read_sheet(csv_path), history(kind)
    known = {r["id"] for r in sheet if tests.get(r["id"], {}).get("issue")}
    known_eps = {r["ep"] for r in sheet if r["id"] in known and r["ep"]}
    order = {r["cat"]: [] for r in sheet}
    for r in sheet:
        order[r["cat"]].append(r["id"])
    near: set[str] = set()
    if kind == "ui":
        for ids in order.values():
            for i, tid in enumerate(ids):
                if tid in known:
                    near.update(ids[max(0, i - NEAR): i + NEAR + 1])
    selected, excluded_known, excluded_na = {}, [], []
    for r in sheet:
        tid, t = r["id"], tests.get(r["id"])
        if not t:
            continue
        if t["spec_undefined"]:
            excluded_na.append(tid)
            continue
        reasons = []
        if t["smoke"]:
            reasons.append("smoke")
        if r["prio"] == "High":
            reasons.append("High")
        if kind == "api" and r["ep"] and r["ep"] in known_eps and tid not in known:
            reasons.append("결함 주변(같은 엔드포인트)")
        if kind == "ui" and tid in near and tid not in known:
            reasons.append("결함 주변(같은 대분류 앞뒤)")
        if tid in hist:
            reasons.append("실패 이력(" + ", ".join(sorted({n[:10] + n[-3:] for n in hist[tid]})) + ")")
        if tid in flagged:
            reasons.append(f"회귀 대상({flagged[tid]})")
        if t["issue"] and tid not in flagged:
            excluded_known.append(f"{tid}({t['issue']})")
            continue
        if reasons:
            selected[tid] = {"reasons": reasons, "prio": r["prio"], "cat": r["cat"], **t}
    return {"kind": kind, "total": len(sheet), "selected": selected,
            "known_issue": excluded_known, "na": excluded_na}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ui-csv", type=Path, required=True)
    ap.add_argument("--api-csv", type=Path, required=True)
    ap.add_argument("--nodeids", choices=("ui", "api"), help="pytest에 넘길 nodeid만 한 줄에 하나씩 출력")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    flagged = regression_flagged()
    res = {"ui": build("ui", a.ui_csv, flagged), "api": build("api", a.api_csv, flagged)}
    if a.nodeids:
        for tid, v in res[a.nodeids]["selected"].items():
            print(f"{v['file']}::{v['func']}")
        return 0
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    for k in ("ui", "api"):
        r = res[k]
        print(f"## {k.upper()}: 시트 {r['total']}건 → 회귀 {len(r['selected'])}건 / known issue 제외 {len(r['known_issue'])} / N/A {len(r['na'])}")
        for tid, v in sorted(r["selected"].items(), key=lambda x: int(x[0].split("_")[1])):
            print(f"- {tid} [{v['prio'] or '-'}] {v['cat']}: " + " / ".join(v["reasons"]))
        print("  known issue 제외: " + ", ".join(r["known_issue"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
