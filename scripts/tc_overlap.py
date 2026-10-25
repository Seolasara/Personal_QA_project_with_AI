#!/usr/bin/env python3
"""새 TC 초안과 기존 TC의 겹침 후보를 뽑는다. 시트나 네트워크는 읽지 않는다.

사용:  python3 scripts/tc_overlap.py --sheet 시트내보내기.csv 초안.json
입력:  시트 CSV(헤더 포함)와 TC 초안 JSON 배열. 초안 키는 시트 헤더와 같다(스텝, 기대결과).
출력:  새 TC마다 같은 버튼 이름([ ])이나 따옴표 문구를 스텝·기대결과에 가진 기존 TC 목록.
  후보일 뿐이다. 기존 TC 목적과 스크립트가 그 문구를 정확 일치로 확인하는지는 사람이 본다.
규칙의 출처: .claude/skills/tc-write/SKILL.md ("6. 작성 후 점검 체크리스트" 2번, 겹침 대조)
"""
import argparse, csv, json, re

TOKEN_MIN = 3  # 따옴표 문구 중 이보다 짧은 것(ex: "1")은 겹침 판단에 쓰지 않는다


def tokens(tc):
    text = (tc.get("스텝") or "") + "\n" + (tc.get("기대결과") or "")
    buttons = set(re.findall(r"\[([^\]]+)\]", text))
    quoted = {q for q in re.findall(r'[“"]([^”"]+)[”"]', text) if len(q) >= TOKEN_MIN}
    return buttons | quoted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True, help="시트 CSV 내보내기")
    ap.add_argument("draft", help="TC 초안 JSON")
    args = ap.parse_args()

    existing = {r["ID"].rstrip("*"): r for r in csv.DictReader(open(args.sheet, encoding="utf-8")) if r.get("ID")}
    draft = json.load(open(args.draft, encoding="utf-8"))
    new_ids = {t.get("ID", "").rstrip("*") for t in draft}

    for tc in draft:
        mine = tokens(tc)
        hits = []
        for tid, row in existing.items():
            if tid in new_ids:
                continue
            common = mine & tokens(row)
            if common:
                hits.append(f"{tid}({', '.join(sorted(common))})")
        print(f"{tc.get('ID', '?')} {tc.get('기능', '')}")
        print(f"  겹침 후보: {', '.join(hits) if hits else '없음'}")


if __name__ == "__main__":
    main()
