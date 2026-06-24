#!/usr/bin/env python3
"""TIP-UX1 — header gate. The global <header class="gbar">…</header> must be BYTE-IDENTICAL on every
surface, except the active-nav state (the .cur span vs an <a>, the only allowed per-page difference).
Extract the header from every built page, normalise active-state + relative prefix, assert one single
canonical form. Fail-loud exit 2 (HEADER_DRIFT). Usage: python3 verify_header.py [file.html]."""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent

PAGES = (["index.html", "reference.html", "search.html", "compare.html", "data.html",
          "knowledge.html", "review.html", "news.html"]
         + sorted(str(p.relative_to(ROOT)) for d in ("entity", "company", "country", "segment",
                                                      "knowledge", "news", "analysis")
                  for p in (ROOT / d).glob("*.html")))

HDR = re.compile(r'<header class="gbar">.*?</header>', re.S)


def canonical(h):
    """Strip the two allowed per-page variations: relative prefix (../) and active-state. First
    collapse each bilingual pair to a flat token (so the active span's nested children don't confuse
    non-greedy matching), then collapse each breadcrumb item — <a> link OR active <span class="cur">
    — to <I>token</I>. What remains: identical wordmark + breadcrumb item set + toggles."""
    h = h.replace('../', '')                           # normalise subdir prefix
    # 1) bilingual pair -> flat token {en|vn}
    h = re.sub(r'<span data-lang-en>(.*?)</span><span data-lang-vn>(.*?)</span>', r'{\1|\2}', h)
    # 2) each nav item (link or active span, any extra class) -> <I>token</I>
    h = re.sub(r'<a [^>]*?href="[^"]*"[^>]*>(\{[^}]*\})</a>', r'<I>\1</I>', h)
    h = re.sub(r'<span class="cur"[^>]*>(\{[^}]*\})</span>', r'<I>\1</I>', h)
    return h


def main():
    files = [pathlib.Path(sys.argv[1])] if len(sys.argv) > 1 else [ROOT / p for p in PAGES]
    forms = {}
    missing = []
    for f in files:
        m = HDR.search(f.read_text())
        if not m:
            missing.append(str(f.relative_to(ROOT) if f.is_relative_to(ROOT) else f)); continue
        forms.setdefault(canonical(m.group(0)), []).append(f.name)
    fails = []
    if missing:
        fails.append("HEADER_MISSING: %d page(s) have no .gbar header, e.g. %s" % (len(missing), missing[:3]))
    if len(forms) > 1:
        variants = sorted(forms.items(), key=lambda kv: -len(kv[1]))
        fails.append("HEADER_DRIFT: %d distinct header forms (should be 1). Outlier example: %s"
                     % (len(forms), variants[-1][1][:2]))
    print("header: %d page(s) checked · %d distinct canonical form(s)" % (len(files), len(forms)))
    if fails:
        print("\nHEADER GATE FAIL:")
        for x in fails:
            print("  -", x)
        sys.exit(2)
    print("HEADER GATE PASS: one locked global header across every surface (active-state aside).")


if __name__ == "__main__":
    main()
