#!/usr/bin/env python3
"""업스트림 v5.md(User Stories)를 기능별 파일과 인덱스로 나눈다. 파일 처리만 하고 네트워크는 쓰지 않는다.

사용:  python3 scripts/spec_split.py <v5.md 경로> [--out .claude/docs/specs/v5]
       python3 scripts/spec_split.py <v5.md 경로> --check   (파일을 바꾸지 않고 결과가 현재와 같은지만 확인, 다르면 종료 코드 1)
입력:  testsmith-io/practice-software-testing 레포의 docs/user-stories/v5.md ("## " 제목 하나가 기능 하나)
출력:  NN_<제목>.md (원문 그대로 + 출처 한 줄), 00_index.md (묶음, 줄 수, AC 제목, 관련 UI 분석 파일)
기능 묶음과 UI 분석 파일 연결은 아래 GROUPS, UI_ANALYSIS에 있다. 새 기능이 생기면 "기타"로 들어가니 여기를 고친다.
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS = [
    ("상품과 탐색", ["Product Overview", "Product Detail", "Rental Products", "Browse Products by Category"]),
    ("체크아웃", ["Checkout – Cart Review", "Checkout – Sign In", "Checkout – Billing Address", "Checkout – Payment (Advanced)"]),
    ("계정과 인증", ["User Registration", "User Login", "Forgot Password", "Two-Factor Authentication Setup", "Customer Profile", "Change Password"]),
    ("마이페이지", ["Favorites", "Invoices", "Messages", "Contact Form (Advanced)"]),
    ("관리자와 부가 기능", ["Admin Dashboard", "Chat Widget"]),
    ("할인과 기타", ["Geo-Location Discount", "Combination Discount", "Multi-Language Support", "Privacy Policy"]),
]
UI_ANALYSIS = {
    "Product Overview": "ui-product-browse.md", "Browse Products by Category": "ui-product-browse.md",
    "Product Detail": "ui-product-detail.md", "Checkout – Cart Review": "ui-cart.md",
    "Checkout – Payment (Advanced)": "ui-payment.md", "User Login": "ui-login-logout.md",
}


def split(src_lines):
    idx = [i for i, l in enumerate(src_lines) if l.startswith("## ")]
    sections = []
    for n, s in enumerate(idx, 1):
        e = idx[n] if n < len(idx) else len(src_lines)
        title = src_lines[s][3:].strip()
        body = src_lines[s:e]
        while body and body[-1].strip() in ("", "---"):
            body.pop()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        sections.append((n, title, f"{n:02d}_{slug}.md", body))
    return sections


def build(sections):
    files = {fn: f'출처: v5.md "{title}"\n\n' + "\n".join(body) + "\n" for _, title, fn, body in sections}
    by_title = {t: (fn, body) for _, t, fn, body in sections}
    grouped = {t for _, ts in GROUPS for t in ts}
    groups = GROUPS + ([("기타(새 기능, 묶음 지정 필요)", [t for _, t, _, _ in sections if t not in grouped])]
                       if any(t not in grouped for _, t, _, _ in sections) else [])
    L = ["# Sprint 5 User Stories 인덱스", "",
         "- 기능 요구사항(User Story, AC)이 필요하면 이 목록에서 해당 기능 파일만 골라 읽는다. 여러 파일을 한꺼번에 읽지 않는다.",
         "- 원본: testsmith-io/practice-software-testing 저장소 `docs/user-stories/v5.md`를 `## ` 기능 단위로 나눈 것이다(내용 수정 없음).",
         "- Sprint 5 개요: 서버 저장 장바구니, 고급 결제, 비밀번호 강도, 계정 잠금, 2단계 인증, 소셜 로그인, PDF 인보이스, 관리자, 채팅, 할인, 다국어, 가격 슬라이더, 개인정보 페이지.",
         "- 형식: 파일 (줄 수, AC 수) — AC 제목. `spec analysis` 칸은 같은 기능을 이미 분석한 `spec analysis/ui/` 파일.", ""]
    for gi, (g, titles) in enumerate(groups, 1):
        L.append(f"## {gi}. {g}")
        for t in titles:
            if t not in by_title:
                continue
            fn, body = by_title[t]
            acs = [re.sub(r"^#### AC\d+ – ", "", l).strip() for l in body if l.startswith("#### AC")]
            s = f"- [{t}]({fn}) ({len(body)}줄, AC {len(acs)}) — " + ", ".join(acs)
            if t in UI_ANALYSIS:
                s += f" / spec analysis: `ui/{UI_ANALYSIS[t]}`"
            L.append(s)
        L.append("")
    files["00_index.md"] = "\n".join(L)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default=str(ROOT / ".claude" / "docs" / "specs" / "v5"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    files = build(split(Path(a.src).read_text(encoding="utf-8").split("\n")))
    out = Path(a.out)
    if a.check:
        bad = [fn for fn, txt in files.items() if not (out / fn).exists() or (out / fn).read_text(encoding="utf-8") != txt]
        extra = sorted(p.name for p in out.glob("*.md") if p.name not in files)
        for fn in bad:
            print(f"다름: {fn}")
        for fn in extra:
            print(f"원본에 없는 파일: {fn}")
        print("현재와 같음" if not (bad or extra) else f"차이 {len(bad) + len(extra)}건")
        sys.exit(1 if (bad or extra) else 0)
    out.mkdir(parents=True, exist_ok=True)
    for fn, txt in files.items():
        (out / fn).write_text(txt, encoding="utf-8")
    print(f"기능 파일 {len(files) - 1}개와 00_index.md를 {out}에 만들었다")


if __name__ == "__main__":
    main()
