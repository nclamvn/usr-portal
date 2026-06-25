#!/usr/bin/env python3
"""TIP-UX2.1 STEP 0 — SVG-fill auditor (STATIC, engine-free).

Phòng lỗi "rotor/glyph đổ fill đen" TẠI GỐC, không cần browser:
  một <svg> an-toàn khi nó KHÔNG để shape rơi về fill mặc-định (đen). Cụ-thể, mỗi
  fillable shape phải có fill tường-minh, HOẶC <svg> gốc đặt fill (none/currentColor/màu)
  để cascade phủ toàn cây. Shape dựa CSS-class cho fill (không attr, root không fill) =
  pattern dễ vỡ trên WebKit/<use>+shadow-tree → exit 2 (SVG_FILL_IMPLICIT).

Engine-parametrized theo PATCH AC: đây là lớp chặn CHÍNH (static). Render 2-engine
(ENGINE_DRIFT) là follow-up TIP-UX2.5, kích-hoạt khi env có Playwright/WebKit.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
FILLABLE = ("path", "rect", "circle", "ellipse", "polygon", "polyline")
SVG_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.DOTALL | re.IGNORECASE)
ROOT_TAG_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)
SHAPE_RE = re.compile(r"<(" + "|".join(FILLABLE) + r")\b([^>]*)>", re.IGNORECASE)
USE_RE = re.compile(r"<use\b([^>]*)>", re.IGNORECASE)
FILL_ATTR = re.compile(r"\bfill\s*=\s*[\"'][^\"']*[\"']", re.IGNORECASE)

# public built surfaces (skip design-source specimens + offline notes)
SKIP_NAMES = {"home-v2-specimen.html"}


def html_files():
    for p in sorted(ROOT.rglob("*.html")):
        if "node_modules" in p.parts:
            continue
        if p.name in SKIP_NAMES or p.name.endswith("-specimen.html"):
            continue
        yield p


def root_governs_fill(root_tag):
    """True if the <svg> root sets fill explicitly -> children cannot fall to default black."""
    return bool(FILL_ATTR.search(root_tag))


def audit_svg(svg, root_tag):
    """Return list of implicit-fill offenders inside one <svg> (empty if safe)."""
    if root_governs_fill(root_tag):
        return []                                   # root fill cascades -> subtree safe
    bad = []
    for m in SHAPE_RE.finditer(svg):
        tag, attrs = m.group(1), m.group(2)
        if not FILL_ATTR.search(attrs):
            bad.append(f"<{tag}> relies on CSS-class/default fill (no fill attr, root has no fill)")
    for m in USE_RE.finditer(svg):
        if not FILL_ATTR.search(m.group(1)):
            bad.append("<use> relies on CSS-class fill in shadow-tree (no fill attr, root has no fill)")
    return bad


def main():
    files = list(html_files())
    offenders = {}          # signature -> count   (dedupe the ~1000 repeated glyphs)
    files_hit = set()
    n_svg = 0
    for p in files:
        html = p.read_text(encoding="utf-8")
        for svg in SVG_RE.findall(html):
            n_svg += 1
            root_tag = ROOT_TAG_RE.match(svg).group(0)
            bad = audit_svg(svg, root_tag)
            if bad:
                files_hit.add(p.name)
                # signature = root class hint + the distinct offenders, so 1000 clones collapse to 1 line
                cls = re.search(r'class\s*=\s*"([^"]*)"', root_tag)
                sig = (cls.group(1).strip() if cls else "(no class)", tuple(sorted(set(bad))))
                offenders[sig] = offenders.get(sig, 0) + 1

    print("svg-fill: scanned %d <svg> across %d page(s)" % (n_svg, len(files)))
    if offenders:
        print("\nSVG GATE FAIL — SVG_FILL_IMPLICIT:")
        for (cls, bad), cnt in sorted(offenders.items(), key=lambda x: -x[1]):
            print("  - svg.%s  x%d instance(s)" % (cls or "(no class)", cnt))
            for b in bad:
                print("      · " + b)
        print("\n  files: " + ", ".join(sorted(files_hit)))
        print("  fix: add fill=\"none\" on the <svg> root (line-art) or explicit fill= on filled shapes.")
        sys.exit(2)
    print("SVG GATE PASS: every <svg> governs fill explicitly (root fill or per-shape) — no default-black risk.")


if __name__ == "__main__":
    main()
