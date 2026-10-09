#!/usr/bin/env python3
"""시트 쓰기 전후 CSV 비교기. 로컬 CSV 두 개만 읽고 시트와 네트워크는 쓰지 않는다.

사용:  python3 scripts/sheet_diff.py --type ui|api 쓰기전.csv 쓴뒤.csv
규칙:  쓰기 전 행은 ID, 내용, 상대 순서가 쓴 뒤에도 같아야 한다(ID를 바꾸거나 번호를 밀지 않는다).
       허용되는 변경은 새 행 추가뿐이다. 새 행은 ID가 "*"로 끝나고, 번호가 기존 최대 번호보다 커야 한다.
       새 행은 어느 위치에 삽입되어도 된다(유저 플로우 순서). 번호 순서는 검사하지 않는다.
       셀 변경, 행 삭제, 기존 행의 순서 변경, ID 중복이 있으면 오류로 보고하고 종료 코드 1을 돌려준다.
CSV는 gviz export(tqx=out:csv) 형식이다. 서식(배경색)은 비교하지 않는다.
"""
import argparse, csv, re, sys



def load(path):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    header = [h.split(" (")[0].strip() for h in rows[0]]
    n = len(header)
    while n and not header[n - 1]:
        n -= 1
    header = header[:n]
    data = []
    for r in rows[1:]:
        r = [c.replace("\r\n", "\n").strip() for c in (r + [""] * n)[:n]]
        if r and r[0]:
            data.append(r)
    return header, data


def key(i):
    return i.rstrip("*").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["ui", "api"], required=True)
    ap.add_argument("before")
    ap.add_argument("after")
    a = ap.parse_args()

    hb, before = load(a.before)
    ha, after = load(a.after)
    errs = []
    if hb != ha:
        errs.append(f"헤더가 달라짐: {hb} -> {ha}")

    exp_by_key = {key(r[0]): r for r in before}
    exp_keys = list(exp_by_key)

    existing, new = [], []
    for r in after:
        (existing if key(r[0]) in exp_by_key else new).append(r)

    # 새 행: ID가 "*"로 끝나고, 기존 최대 번호보다 커야 한다
    max_no = max((int(k.split("_")[1]) for k in exp_keys if re.match(r"(UI|API)_\d+$", k)), default=0)
    for r in new:
        if not r[0].endswith("*"):
            errs.append(f"새 행 {r[0]}의 ID 끝에 '*'가 없음")
        m = re.match(r"(UI|API)_(\d+)\*?$", r[0])
        if not m or int(m.group(2)) <= max_no:
            errs.append(f"새 행 {r[0]}의 번호가 기존 최대 번호(UI/API_{max_no})보다 크지 않음")

    # 기존 행: 순서와 셀이 같아야 한다
    after_keys = [key(r[0]) for r in existing]
    if after_keys != [k for k in exp_keys if k in set(after_keys)]:
        errs.append("기존 행의 순서가 바뀜")
    for k in exp_keys:
        if k not in set(after_keys):
            errs.append(f"기존 행 {k} 삭제됨 또는 ID 변경됨")
    for r in existing:
        e = exp_by_key[key(r[0])]
        for col, (x, y) in enumerate(zip(e, r)):
            if x != y:
                errs.append(f"{key(r[0])} [{ha[col]}] 셀이 바뀜: {x[:40]!r} -> {y[:40]!r}")

    # 전체 ID: 중복 없음
    ids = [key(r[0]) for r in after]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        errs.append(f"ID 중복: {dup}")

    print(f"쓰기 전 {len(before)}행, 쓴 뒤 {len(after)}행, 새 행 {len(new)}개")
    for r in new:
        print(f"  + {r[0]}")
    for e in errs:
        print(f"[오류] {e}")
    print("비교 통과" if not errs else f"\n오류 {len(errs)}건: 백업 CSV와 비교해 확인 필요")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
