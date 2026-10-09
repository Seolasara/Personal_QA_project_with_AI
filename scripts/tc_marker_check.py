#!/usr/bin/env python3
"""pytest TC 마커와 시트 ID가 맞는지 확인한다. 시트는 직접 읽지 않고 넘겨받은 CSV 파일만 읽는다.

사용:  python3 scripts/tc_marker_check.py --ui UI-TC.csv --api API-TC.csv
- 시트 CSV는 시트의 탭을 CSV로 내려받은 파일이다 (첫 열이 ID).
- 점검 항목: 시트에 없는 마커, 같은 마커가 여러 테스트에 붙은 경우, 테스트가 없는 TC(커버리지).
"""
import argparse, csv, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERN = re.compile(r'@pytest\.mark\.tc\(\s*["\']([A-Z]+_\d+)["\']\s*\)')


def sheet_ids(path):
    return [r["ID"].strip() for r in csv.DictReader(open(path, encoding="utf-8")) if r.get("ID", "").strip()]


def markers(tests_dir):
    found = defaultdict(list)
    for f in sorted(Path(tests_dir).glob("*.py")):
        for no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in PATTERN.finditer(line):
                found[m.group(1)].append(f"{f.relative_to(ROOT)}:{no}")
    return found


def check(label, csv_path, tests_dir):
    ids = sheet_ids(csv_path)
    found = markers(tests_dir)
    bad = errors = 0
    print(f"[{label}] 시트 TC {len(ids)}개, 마커 {len(found)}종")
    for mid, locs in found.items():
        if mid not in ids:
            print(f"  [오류] 시트에 없는 마커 {mid}: {', '.join(locs)}")
            errors += 1
        elif len(locs) > 1:
            print(f"  [오류] 마커 {mid}가 {len(locs)}곳에 중복: {', '.join(locs)}")
            errors += 1
    uncovered = [i for i in ids if i not in found]
    print(f"  테스트 있음 {len(ids) - len(uncovered)}개, 테스트 없음 {len(uncovered)}개")
    if uncovered:
        print("  테스트 없는 TC: " + ", ".join(uncovered))
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ui")
    ap.add_argument("--api")
    a = ap.parse_args()
    errors = 0
    if a.ui:
        errors += check("UI", a.ui, ROOT / "playwright-demo" / "tests")
    if a.api:
        errors += check("API", a.api, ROOT / "api-demo" / "tests")
    print(f"\n오류 {errors}건")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
