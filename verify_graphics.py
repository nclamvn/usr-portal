#!/usr/bin/env python3
"""TIP-GRAPHICS gate — đồ hoạ vẫn zero-fab. Mọi số trong viz SVG phải recompute từ aggregate sống;
honest-null không được vẽ thành giá-trị; màu phải qua token (THEME_PURITY). Fail-loud exit 2.
  · GFX_FIGURE_DRIFT — số nhúng trong SVG ≠ recompute từ aggregates.
  · GFX_NULL_FAKED   — viz vẽ thanh/lát cho ô registry null (số bar ≠ số spec có range).
  · GFX_THEME_LEAK   — màu hardcode (#hex / rgb()) trong SVG thay vì var(--*).
Hiện canh homepage signature (.sigviz); mở rộng cho donut/heat khi nhịp 2b land.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
def fnum(x):
    return ("%g" % x).replace(".", ",") if (isinstance(x, float) and x != int(x)) else f"{int(x):,}".replace(",", ".")


def sig_block(html):
    m = re.search(r'<section class="sigwrap".*?</section>', html, re.S)
    return m.group(0) if m else ""


def _svg_bits(block):
    return "".join(re.findall(r'<svg class="scat-svg".*?</svg>', block, re.S))


def check_signature(html, site, fails):
    """INFO/02 = capability scatter (MTOW × range, log×log). Every dot recomputes from the registry;
    only systems with BOTH specs are plotted (honest-null); colour via token class (no hardcoded hex)."""
    sig = sig_block(html)
    if not sig:
        fails.append("GFX_MISSING: homepage không có .sigwrap scatter"); return
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]

    def num(e, k):
        v = (e.get(k) or {}).get("value")
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    pts = [(num(e, "mtow_kg"), num(e, "max_range_km")) for e in uavs]
    pts = [(m, r) for m, r in pts if m and r and m > 0 and r > 0]
    n, total = len(pts), len(uavs)

    # FIGURE_DRIFT — one dot per system-with-both (recompute), no more no fewer
    dots = len(re.findall(r'class="dot ', sig))
    if dots != n:
        fails.append("GFX_FIGURE_DRIFT: scatter %d dots != %d systems with both mtow+range" % (dots, n))
    # FIGURE_DRIFT — the four axis extremes equal the plotted fleet's min/max
    ms = [m for m, _ in pts]
    rs = [r for _, r in pts]
    for x in (min(ms), max(ms), min(rs), max(rs)):
        f = fnum(x)
        if not re.search(r"(?<![\d.,])" + re.escape(f) + r"(?![\d.,])", sig):
            fails.append("GFX_FIGURE_DRIFT: scatter axis extreme %s absent/!=recompute" % f)
    # NULL_FAKED — honest-null disclosed: caption shows 'n of total' with the real total, n < total
    if n >= total or str(total) not in sig:
        fails.append("GFX_NULL_FAKED: scatter must disclose %d of %d (honest-null not exposed)" % (n, total))
    # THEME_LEAK — scatter SVG must carry no hardcoded colour (dots use token classes)
    leak = re.findall(r"(?<!&)#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(", _svg_bits(sig))
    if leak:
        fails.append("GFX_THEME_LEAK: màu hardcode trong scatter SVG: %s" % leak[:3])


def check_donut(html, site, fails):
    if 'class="cdcard"' not in html:
        fails.append("GFX_MISSING: data page không có compliance donut"); return
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    total = len(uavs)
    for key in ("blue_uas", "ndaa_compliant"):
        yes = sum(1 for e in uavs if (e.get(key) or {}).get("value") is True)
        present = sum(1 for e in uavs if (e.get(key) or {}).get("value") is not None)
        no, unk = present - yes, total - present
        for lbl, val in (("compliant", yes), ("not", no), ("unverified", unk)):
            if not re.search(r"<b>" + str(val) + r"</b>", html):   # legend số = recompute
                fails.append("GFX_FIGURE_DRIFT: donut %s %s=%d không thấy" % (key, lbl, val))
    # honest-null: lát 'chưa rõ' phải là legend riêng (KHÔNG gộp vào 'không tuân thủ')
    if len(re.findall(r'class="cl unk"', html)) < 2:
        fails.append("GFX_NULL_FAKED: lát 'chưa rõ' bị gộp/thiếu (legend unk < 2)")
    svgs = "".join(re.findall(r'<svg class="cdonut-svg".*?</svg>', html, re.S))
    leak = re.findall(r"(?<!&)#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(", svgs)
    if leak:
        fails.append("GFX_THEME_LEAK: màu hardcode trong donut SVG: %s" % leak[:3])


def main():
    site = json.loads(SITE.read_bytes())
    fails = []
    check_signature((ROOT / "index.html").read_text(encoding="utf-8"), site, fails)
    check_donut((ROOT / "data.html").read_text(encoding="utf-8"), site, fails)
    if fails:
        print("\nGRAPHICS GATE FAIL (%d):" % len(fails))
        for x in fails[:20]:
            print("  -", x)
        sys.exit(2)
    print("GRAPHICS GATE PASS: signature numbers recompute · 0 honest-null faked · token-only paint.")


if __name__ == "__main__":
    main()
