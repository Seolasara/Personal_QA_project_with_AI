#!/usr/bin/env python3
"""TC 초안(JSON) 기계 점검기. 시트나 repo 파일은 읽지 않는다.

사용:  python3 scripts/tc_lint.py --type ui|api 초안.json      (또는 표준입력)
       python3 scripts/tc_lint.py --type api 시트내보내기.csv --only-new   (ID가 "*"로 끝나는 새 행만)
입력:  TC 객체의 JSON 배열 또는 시트 헤더가 있는 CSV 파일. 키는 시트 헤더와 같게 쓴다.
  UI : 기능, 목적, 중요도, 사전 조건, 스텝, 기대결과, Note
  API: 테스트 시나리오, 목적, 메서드, 엔드포인트, 사전 조건, 요청 바디, 기대결과, Priority, Note
규칙의 출처: .claude/skills/tc-write/SKILL.md ("5. 작성 후 점검 체크리스트" 1번)
"""
import argparse, csv, json, re, sys

ERR, WARN = "오류", "주의"


def lines(s):
    return [l for l in (s or "").split("\n") if l.strip()]


def check(tc, kind):
    out = []
    title_key = "기능" if kind == "ui" else "테스트 시나리오"
    title = tc.get(title_key, "")
    exp = tc.get("기대결과", "")
    note = tc.get("Note", "")
    purpose = tc.get("목적", "")

    # 공통
    if "·" in title:
        out.append((ERR, f"{title_key}에 \"·\" 사용"))
    if not title.strip().endswith("확인"):
        out.append((WARN, f"{title_key}가 \"~ 확인\"으로 끝나지 않음"))
    if "(확인 필요)" in exp:
        out.append((ERR, "기대결과에 \"(확인 필요)\" 사용 (Note로 옮길 것)"))
    for l in lines(note):
        if re.search(r"(UI|API)_\d+", l):
            out.append((WARN, f"Note에 다른 TC를 가리키는 문구: {l[:30]}"))
        elif "스펙 근거" in l:
            out.append((ERR, "Note에 \"스펙 근거\" 문구"))
        elif re.search(r"연속|백로그|Accept", l):
            out.append((ERR, f"Note에 실행 주의/백로그/헤더 문구: {l[:30]}"))
        elif "확인 필요" in l and not l.startswith("확인 필요:") and not l.startswith("실제 동작"):
            out.append((WARN, f"Note의 확인 필요 문구가 \"확인 필요:\"로 시작하지 않음: {l[:30]}"))
    if not purpose.strip():
        out.append((ERR, "목적 비어 있음"))
    elif not re.search(r"지 확인$", purpose.strip()):
        out.append((WARN, "목적이 \"~지 확인\"(ex: ~는지 확인)으로 끝나지 않음"))

    prio_key = "중요도" if kind == "ui" else "Priority"
    if tc.get(prio_key, "").strip() not in ("High", "Medium", "Low"):
        out.append((ERR, f"{prio_key}가 High/Medium/Low가 아님: {tc.get(prio_key, '')!r}"))

    cond_key = "사전 조건"
    cond_lines = lines(tc.get(cond_key, ""))
    if any(l.startswith("- ") for l in cond_lines):
        out.append((ERR, f"{cond_key}에 불릿(\"- \") 사용"))
    elif len(cond_lines) > 1 and any(not re.match(r"\d+\. ", l) for l in cond_lines):
        out.append((WARN, f"{cond_key}가 여러 줄인데 번호 형식 아님"))

    if kind == "ui":
        steps = tc.get("스텝", "")
        for l in lines(steps):
            if "버튼" in l and "[" not in l:
                out.append((WARN, f"스텝에 [ ] 없는 버튼 표기: {l[:30]}"))
            if not re.match(r"\d+\. ", l):
                out.append((WARN, f"스텝 번호 형식 아님: {l[:30]}"))
        for l in lines(exp):
            if not re.match(r"\d+(-\d+)?\. ", l):
                out.append((WARN, f"기대결과 번호 형식 아님: {l[:30]}"))
            if re.search(r"(제거|갱신|변경|초기화)$", l.strip()):
                out.append((WARN, f"기대결과가 동작으로 끝남 (노출되는 상태로 쓸 것): {l[:30]}"))
    else:
        el = lines(exp)
        if any(l.startswith("- ") for l in el):
            out.append((ERR, "기대결과에 불릿(\"- \") 사용"))
        elif any(not re.match(r"\d+\. ", l) for l in el if not l.startswith(("{", "}", "[", "]", '"', ",", "..."))):
            out.append((WARN, "기대결과에 번호 형식이 아닌 줄이 있음"))
        if not el or not el[0].startswith("1. HTTP status code"):
            out.append((WARN, "기대결과 1번이 \"1. HTTP status code: ...\"가 아님"))
        if not re.search(r"[{\[]|응답 바디 없음", exp):
            out.append((WARN, "기대결과에 JSON 응답 바디가 없음"))
        if "누락" in title and not re.search(r"필드|파라미터|요청|바디", title):
            out.append((WARN, "누락 TC의 이름에 \"필드\", \"파라미터\", \"요청\" 중 무엇이 누락인지 없음"))
        if "타입" in title and "응답 바디" not in title:
            out.append((WARN, "타입 확인 TC의 이름에 \"응답 바디\"가 없음"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["ui", "api"], required=True)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--only-new", action="store_true", help='ID가 "*"로 끝나는 행만 점검 (CSV)')
    a = ap.parse_args()
    if a.file and a.file.endswith(".csv"):
        data = []
        for row in csv.DictReader(open(a.file, encoding="utf-8")):
            row = {k.split(" (")[0]: v for k, v in row.items()}
            if a.only_new and not row.get("ID", "").endswith("*"):
                continue
            if row.get("ID"):
                data.append(row)
    else:
        data = json.load(open(a.file) if a.file else sys.stdin)
    errs = warns = 0
    for i, tc in enumerate(data, 1):
        key = tc.get("key") or tc.get("ID") or f"#{i}"
        for level, msg in check(tc, a.type):
            print(f"[{level}] {key}: {msg}")
            errs += level == ERR
            warns += level == WARN
    print(f"\n점검 {len(data)}건: 오류 {errs}, 주의 {warns}")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
