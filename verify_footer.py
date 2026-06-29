#!/usr/bin/env python3
"""Footer gate — the global <footer class="sfoot"> must be present on every surface and BYTE-IDENTICAL
(only the relative ../ prefix differs). Extract + normalise + assert one canonical form. Fail-loud
exit 2 (FOOTER_DRIFT / FOOTER_MISSING). Usage: python3 verify_footer.py [file.html]."""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent

PAGES = (["index.html", "reference.html", "search.html", "compare.html", "data.html",
          "knowledge.html", "review.html", "news.html"]
         + sorted(str(p.relative_to(ROOT)) for d in ("uav", "company", "country", "segment",
                                                      "airframe", "propulsion", "weight", "flight-time", "compliance",
                                                      "knowledge", "news", "analysis")
                  for p in (ROOT / d).glob("*.html")))

FT = re.compile(r'<footer class="sfoot.*?</footer>', re.S)


def canonical(h):
    """The only allowed per-page variation is the relative prefix (../) on links/logo src."""
    return h.replace('../', '')


def main():
    files = [pathlib.Path(sys.argv[1])] if len(sys.argv) > 1 else [ROOT / p for p in PAGES]
    forms, missing = {}, []
    for f in files:
        m = FT.search(f.read_text())
        if not m:
            missing.append(str(f.relative_to(ROOT) if f.is_relative_to(ROOT) else f)); continue
        forms.setdefault(canonical(m.group(0)), []).append(f.name)
    fails = []
    if missing:
        fails.append("FOOTER_MISSING: %d page(s) have no .sfoot footer, e.g. %s" % (len(missing), missing[:3]))
    if len(forms) > 1:
        variants = sorted(forms.items(), key=lambda kv: -len(kv[1]))
        fails.append("FOOTER_DRIFT: %d distinct footer forms (should be 1). Outlier: %s"
                     % (len(forms), variants[-1][1][:2]))
    print("footer: %d page(s) checked · %d distinct canonical form(s)" % (len(files), len(forms)))
    if fails:
        print("\nFOOTER GATE FAIL:")
        for x in fails:
            print("  -", x)
        sys.exit(2)
    print("FOOTER GATE PASS: one global footer present on every surface.")


if __name__ == "__main__":
    main()
