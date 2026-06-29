#!/usr/bin/env python3
"""Teeth cho verify_breadcrumb — chứng 4 răng CẮN. Mutate một trang thật rồi RESTORE (try/finally)."""
import subprocess, sys, re, pathlib
from seo import BASE

ROOT = pathlib.Path(__file__).resolve().parent
BC_RE = re.compile(r'<script type="application/ld\+json">(?:(?!</script>).)*?BreadcrumbList(?:(?!</script>).)*?</script>', re.S)


def run():
    r = subprocess.run([sys.executable, str(ROOT / "verify_breadcrumb.py")], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


results = []


def case(name, page, newtext, want):
    bak = page.read_text(encoding="utf-8")
    try:
        page.write_text(newtext, encoding="utf-8")
        rc, out = run()
        results.append((name, rc == 2 and want in out, rc))
    finally:
        page.write_text(bak, encoding="utf-8")


def main():
    tp = sorted((ROOT / "uav").glob("*.html"))[0]
    txt = tp.read_text(encoding="utf-8")
    bc = BC_RE.search(txt).group(0)

    rc, out = run()
    results.append(("clean control", rc == 0, rc))

    # (a) BC_MISSING — strip the BreadcrumbList block
    case("a · missing block", tp, txt.replace(bc, "", 1), "BC_MISSING")

    # (b) BC_DANGLING — point an ancestor crumb at a dead URL
    case("b · dangling crumb", tp, txt.replace(f"{BASE}/reference.html", f"{BASE}/reference-DEAD.html", 1),
         "BC_DANGLING")

    # (c) BC_POSITION — break the position sequence
    case("c · broken position", tp, txt.replace('"position": 2', '"position": 9', 1), "BC_POSITION")

    # (d) BC_NAME_FAKE — rename the leaf to something not in the title
    bc_fake = re.sub(r'("name": ")[^"]*(", "item": "[^"]*uav/[^"]*")', r'\g<1>ZZZ Fabricated\g<2>', bc, count=1)
    case("d · faked leaf name", tp, txt.replace(bc, bc_fake, 1), "BC_NAME_FAKE")

    ok = all(b for _, b, _ in results)
    for nm, b, rc in results:
        tag = "PASS" if nm == "clean control" and b else ("CẮN ✓" if b else "KHÔNG CẮN ✗")
        print(f"  {tag:8s} {nm}  (exit {rc})")
    print("BREADCRUMB TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
