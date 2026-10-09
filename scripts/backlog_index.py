#!/usr/bin/env python3
"""백로그 인덱스 갱신기. `.claude/docs/backlog/01~05_*.md`의 항목 제목을 읽어
`00_index.md`의 "## 2. 목록"과 "다음 번호"를 다시 만든다. 파일 처리만 하고 네트워크는 쓰지 않는다.

사용:  python3 scripts/backlog_index.py          (갱신)
       python3 scripts/backlog_index.py --check  (갱신 없이 인덱스가 최신인지만 확인, 낡았으면 종료 코드 1)
항목 형식: .claude/guides/backlog-format.md
"""
import argparse, re, sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / ".claude" / "docs" / "backlog"
FILES = [
    ("01_real-bug.md", "real-bug"),
    ("02_agenda.md", "안건"),
    ("03_tech-debt-env.md", "기술부채·env·운영 메모"),
    ("04_hold.md", "판단 보류"),
    ("05_done.md", "해결·폐기"),
]


def parse(path):
    """파일의 항목을 (번호, 제목, [TC 번호...]) 목록으로 돌려준다."""
    items = []
    for blk in re.split(r"(?m)^(?=### #)", path.read_text(encoding="utf-8"))[1:]:
        m = re.match(r"### #(\d+) (.+)", blk)
        tcs = [t for t in re.findall(r"(?m)^  \d+\. \[([^\]]+)\]", blk) if t != "TC 없음"]
        items.append((int(m.group(1)), m.group(2).strip(), tcs))
    return items


def build():
    lines, nums = ["## 2. 목록"], []
    for fn, name in FILES:
        lines.append(f"### [{name}]({fn})")
        for n, title, tcs in parse(DIR / fn):
            nums.append(n)
            tc = f" ({', '.join(tcs)})" if tcs else ""
            if len(tc) > 60:
                tc = f" ({tcs[0]} 외)"
            lines.append(f"- #{n} {title}{tc}")
        lines.append("")
    return "\n".join(lines), max(nums) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    idx = DIR / "00_index.md"
    old = idx.read_text(encoding="utf-8")
    body, nxt = build()
    head = old[: old.index("## 2. 목록")]
    head = re.sub(r"현재 다음 번호 #\d+", f"현재 다음 번호 #{nxt}", head)
    new = head + body
    if a.check:
        if new.rstrip() != old.rstrip():
            print("인덱스가 최신이 아님: python3 scripts/backlog_index.py 실행 필요")
            sys.exit(1)
        print("인덱스 최신")
        return
    idx.write_text(new, encoding="utf-8")
    print(f"갱신: 항목 {sum(1 for l in body.split(chr(10)) if l.startswith('- #'))}개, 다음 번호 #{nxt}")


if __name__ == "__main__":
    main()
