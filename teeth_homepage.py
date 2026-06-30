#!/usr/bin/env python3
"""Teeth cho verify_homepage — chứng 6 răng CẮN. Mutate index.html thật rồi RESTORE (try/finally)."""
import subprocess, sys, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
HOME = ROOT / "index.html"


def run():
    r = subprocess.run([sys.executable, str(ROOT / "verify_homepage.py")], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


results = []


def case(name, newtext, want):
    bak = HOME.read_text(encoding="utf-8")
    try:
        HOME.write_text(newtext, encoding="utf-8")
        rc, out = run()
        results.append((name, rc == 2 and want in out, rc))
    finally:
        HOME.write_text(bak, encoding="utf-8")


def main():
    txt = HOME.read_text(encoding="utf-8")

    rc, out = run()
    results.append(("clean control", rc == 0, rc))

    # (a) FIGURE_DRIFT — swap the live country stat (count appears in masthead + footer strip;
    # derive it from site-data so the tooth survives registry growth, no hardcoded number)
    import json as _json
    _cc = str(len({(e.get("manufacturer_country") or {}).get("value")
                   for e in _json.loads((ROOT / "out" / "site-data.json").read_text())["entities"]
                   if e.get("entity_type") == "uav" and (e.get("manufacturer_country") or {}).get("value")}))
    drift = txt.replace(">" + _cc + "<", ">13<")
    case("a · figure drift (countries->13)", drift, "HP_FIGURE_DRIFT")

    # (b) DANGLING — point a card at a ghost slug
    dang = re.sub(r'href="news/[a-z0-9-]+\.html"', 'href="news/zzz-ghost-xyz.html"', txt, count=1)
    case("b · dangling link", dang, "HP_DANGLING")

    # (c) NULL_FAKED — inject a stray null-marker inside the compare table
    nf = txt.replace("</table>", "<tr><td>x</td><td>not recorded</td></tr></table>", 1)
    case("c · faked null cell", nf, "HP_NULL_FAKED")

    # (d) THEME_LEAK — hardcoded color in <style>
    leak = txt.replace("</style>", "  .x{color:#ff0000}\n</style>", 1)
    case("d · hardcoded color", leak, "HP_THEME_LEAK")

    # (e) I18N — drop one vn span
    i18 = txt.replace("data-lang-vn", "data-lang-zz", 1)
    case("e · i18n imbalance", i18, "HP_I18N")

    # (f) MOTION — remove the reduced-motion guard block
    mot = re.sub(r"@media \(prefers-reduced-motion: reduce\)\{.*?\}\s*\}", "", txt, count=1, flags=re.S)
    case("f · motion unguarded", mot, "HP_MOTION")

    ok = all(b for _, b, _ in results)
    for nm, b, rc in results:
        tag = "PASS" if nm == "clean control" and b else ("CẮN ✓" if b else "KHÔNG CẮN ✗")
        print(f"  {tag:8s} {nm}  (exit {rc})")
    print("HOMEPAGE TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
