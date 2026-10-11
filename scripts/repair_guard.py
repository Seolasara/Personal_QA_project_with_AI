#!/usr/bin/env python3
"""수리 diff 점검기. /test-repair가 고친 코드가 실패를 숨기지 않았는지 diff만 보고 점검한다. 네트워크와 시트는 쓰지 않는다.

사용:  git diff -U0 -- playwright-demo api-demo | python3 scripts/repair_guard.py
- 오류: 어설션 수 감소, skip/xfail 추가, 고정 대기(sleep, wait_for_timeout) 추가. 하나라도 있으면 종료 코드 1.
- 주의: 어설션의 기대값 변경, timeout 값 변경. 사람이 TC 기대결과와 대조해 확인한다.
- 규칙의 출처: 루트 CLAUDE.md 가드레일, .claude/skills/test-repair/SKILL.md
"""
import re, sys
from collections import defaultdict

ERR, WARN = "오류", "주의"
ASSERT = re.compile(r"^\s*(assert\b|expect\(|.*\.to_(have|be|contain)_)")
SKIP_XFAIL = re.compile(r"pytest\.(skip|xfail)\b|mark\.(skip|skipif|xfail)\b")
FIXED_WAIT = re.compile(r"wait_for_timeout\(|time\.sleep\(")
TIMEOUT = re.compile(r"timeout\s*=\s*[\d_.]+")
LITERAL = re.compile(r"\"[^\"]*\"|'[^']*'|\b\d+(?:\.\d+)?\b")


def parse(diff):
    files = defaultdict(lambda: {"-": [], "+": []})
    cur = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            cur = line[6:] if line.startswith("+++ b/") else None
        elif cur and line.startswith(("-", "+")) and not line.startswith(("---", "+++")):
            files[cur][line[0]].append(line[1:])
    return files


def check(files):
    out = []
    for path, d in files.items():
        if not path.endswith(".py"):
            continue
        removed = [l for l in d["-"] if ASSERT.match(l)]
        added = [l for l in d["+"] if ASSERT.match(l)]
        if len(added) < len(removed):
            out.append((ERR, f"{path}: 어설션 {len(removed)}개 삭제, {len(added)}개 추가(감소)"))
        for l in d["+"]:
            if SKIP_XFAIL.search(l):
                out.append((ERR, f"{path}: skip/xfail 추가: {l.strip()}"))
            if FIXED_WAIT.search(l):
                out.append((ERR, f"{path}: 고정 대기 추가: {l.strip()}"))
        removed_lits = {tuple(LITERAL.findall(l)) for l in removed}
        for l in added:
            lits = tuple(LITERAL.findall(l))
            if lits and removed and lits not in removed_lits:
                out.append((WARN, f"{path}: 어설션 기대값 변경 확인 필요: {l.strip()}"))
        old_t = {m.group(0) for l in d["-"] for m in TIMEOUT.finditer(l)}
        for l in d["+"]:
            for m in TIMEOUT.finditer(l):
                if m.group(0) not in old_t:
                    out.append((WARN, f"{path}: timeout 변경 확인 필요: {l.strip()}"))
    return out


def main():
    diff = sys.stdin.read()
    if not diff.strip():
        print("점검할 diff가 없습니다.")
        return 0
    out = check(parse(diff))
    for level, msg in out:
        print(f"[{level}] {msg}")
    errs = sum(1 for lv, _ in out if lv == ERR)
    warns = len(out) - errs
    print(f"\n오류 {errs}건, 주의 {warns}건")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
