#!/usr/bin/env python3
"""테스트 스크립트 기계 점검기. Script-Writer가 쓴 파일을 점검한다. 네트워크와 시트는 쓰지 않는다.

사용:  python3 scripts/script_lint.py playwright-demo/tests/foo_test.py api-demo/tests/bar_test.py
- 경로에 playwright-demo가 있으면 UI 규칙(마커 UI_NN), api-demo가 있으면 API 규칙(마커 API_NN)을 적용한다.
- 규칙의 출처: 루트 CLAUDE.md 가드레일, playwright-demo/CLAUDE.md, api-demo/CLAUDE.md, .claude/agents/Script-Writer.md
"""
import ast, re, sys
from pathlib import Path

ERR, WARN = "오류", "주의"


def _num(tc_id):
    m = re.search(r"(\d+)$", str(tc_id))
    return int(m.group(1)) if m else -1


def marker_ids(fn):
    ids = []
    for d in fn.decorator_list:
        if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "tc" and d.args:
            if isinstance(d.args[0], ast.Constant):
                ids.append(d.args[0].value)
    return ids


def decorators_text(fn, src):
    return "\n".join(ast.get_source_segment(src, d) or "" for d in fn.decorator_list)


def check_file(path, seen):
    out = []
    src = Path(path).read_text(encoding="utf-8")
    kind = "ui" if "playwright-demo" in str(path) else "api" if "api-demo" in str(path) else None
    if kind is None:
        return [(ERR, f"{path}: playwright-demo 또는 api-demo 아래 파일이 아님")]
    tree = ast.parse(src)
    prefix = "UI_" if kind == "ui" else "API_"

    # 파일 전체 규칙
    lines = src.splitlines()
    for no, line in enumerate(lines, 1):
        code = line.split("#")[0]
        if "wait_for_timeout(" in code or "time.sleep(" in code:
            out.append((ERR, f"{path}:{no} wait_for_timeout/time.sleep 사용"))
        if re.search(r"pass123|welcome01", code):
            out.append((ERR, f"{path}:{no} 계정 비밀번호가 코드에 있음 (config/.env 사용)"))
        elif re.search(r"[\w.]+@practicesoftwaretesting\.com", code):
            out.append((WARN, f"{path}:{no} 이메일이 코드에 있음 (계정이면 config/.env 사용)"))
        if "pytest.skip(" in code or "mark.skip" in code:
            out.append((ERR, f"{path}:{no} skip 사용 금지"))
        if kind == "ui" and (re.search(r"xpath=|locator\(\s*[\"']//", code) or ".nth(" in code):
            out.append((ERR, f"{path}:{no} XPath 또는 nth 셀렉터 사용 금지"))
        if kind == "api" and "/tests/" in str(path) and re.search(r"^\s*(import httpx|from httpx|import requests)", code):
            out.append((ERR, f"{path}:{no} 테스트에서 httpx/requests 직접 사용 (client와 fixture 사용)"))
        if "pytest.xfail(" in code and not re.search(r"백로그|#\d", "\n".join(lines[no - 1:no + 3])):
            out.append((ERR, f"{path}:{no} pytest.xfail은 사유에 백로그 번호가 있어야 함"))
        if "print(" in code:
            out.append((WARN, f"{path}:{no} print 사용"))

    # 테스트 함수 규칙
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and kind == "api":
            out.append((ERR, f"{path}:{node.lineno} async 사용 금지 (sync httpx만 사용)"))
        if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
            continue
        where = f"{path}:{node.lineno} {node.name}"
        ids = marker_ids(node)
        if not ids:
            out.append((ERR, f"{where}: @pytest.mark.tc 마커 없음"))
        for i in ids:
            if not re.fullmatch(prefix + r"\d{2,3}", str(i)):
                out.append((ERR, f"{where}: 마커 {i} 형식이 {prefix}NN이 아님"))
            if i in seen:
                out.append((ERR, f"{where}: 마커 {i}가 {seen[i]}와 중복"))
            seen[i] = f"{path}:{node.lineno}"
        body = ast.get_source_segment(src, node) or ""
        if not re.search(r"\bassert\b|expect\(", body):
            out.append((ERR, f"{where}: 어설션 없음"))
        if kind == "api" and "status_code" not in body:
            out.append((WARN, f"{where}: 상태코드 확인 없음"))
        if kind == "ui" and re.search(r"page\.(locator|get_by_\w+)\(", body):
            out.append((WARN, f"{where}: 테스트 본문에 셀렉터 사용 (Page Object로 옮길 것)"))
        dec = decorators_text(node, src)
        if "xfail" in dec and not ("strict=True" in dec and re.search(r"백로그|#\d", dec)):
            out.append((ERR, f"{where}: xfail은 strict=True와 백로그 번호가 있어야 함"))
    order = [(i, n.lineno) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_") for i in marker_ids(n)[:1]]
    for (prev, _), (cur, ln) in zip(order, order[1:]):
        if _num(cur) < _num(prev):
            out.append((WARN, f"{path}:{ln} TC 번호 순서가 어긋남 ({prev} 다음에 {cur})"))
    return out


def main():
    files = sys.argv[1:]
    if not files:
        sys.exit(__doc__)
    seen, errs, warns = {}, 0, 0
    for f in files:
        for level, msg in check_file(f, seen):
            print(f"[{level}] {msg}")
            errs += level == ERR
            warns += level == WARN
    print(f"\n점검 {len(files)}개 파일: 오류 {errs}, 주의 {warns}")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
