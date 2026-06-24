#!/usr/bin/env python3
"""TIP-005/C — i18n completeness. Every visible string is bilingual: each data-lang-en
span must have a paired data-lang-vn (and vice-versa). Fail-loud (exit 2) on imbalance."""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
fails = []
names = ["index.html", "reference.html", "base/demo.html"]
names += sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("analysis/*.html"))
names += sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("news/*.html"))
names += sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("company/*.html"))
for name in names:
    p = ROOT / name
    if not p.exists():
        continue
    h = p.read_text()
    en = len(re.findall(r"data-lang-en", h))
    vn = len(re.findall(r"data-lang-vn", h))
    status = "OK" if (en == vn and en > 0) else "FAIL"
    print(f"  {name:22} en={en} vn={vn}  {status}")
    if en != vn or en == 0:
        fails.append(f"{name}: en={en} != vn={vn}")

if fails:
    print("\nI18N FAIL:")
    for f in fails:
        print("  -", f)
    sys.exit(2)
print("I18N PASS: every visible string has en+vn.")
