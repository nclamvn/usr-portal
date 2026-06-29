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
SIG_SPECS = ["mtow_kg", "max_payload_kg", "max_range_km", "endurance_min", "max_link_km", "max_speed_ms", "service_ceiling_m"]


def fnum(x):
    return ("%g" % x).replace(".", ",") if (isinstance(x, float) and x != int(x)) else f"{int(x):,}".replace(",", ".")


def sig_block(html):
    m = re.search(r'<section class="sigwrap".*?</section>', html, re.S)
    return m.group(0) if m else ""


def _svg_bits(block):
    return "".join(re.findall(r'<svg class="sig-barsvg".*?</svg>', block, re.S))


def check_signature(html, site, fails):
    sig = sig_block(html)
    if not sig:
        fails.append("GFX_MISSING: homepage không có .sigwrap signature"); return
    sr = site["aggregates"].get("spec_range", {})
    specs = [k for k in SIG_SPECS if sr.get(k) and sr[k]["max"] > sr[k]["min"] > 0]
    for k in specs:
        for x in (sr[k]["min"], sr[k]["max"]):
            f = fnum(x)
            if not re.search(r"(?<![\d.,])" + re.escape(f) + r"(?![\d.,])", sig):
                fails.append("GFX_FIGURE_DRIFT: signature %s value %s != recompute/absent" % (k, f))
    bars = len(re.findall(r'class="sig-fill"', sig))
    if bars != len(specs):
        fails.append("GFX_NULL_FAKED: %d bar ≠ %d spec có range (vẽ ô null?)" % (bars, len(specs)))
    leak = re.findall(r"(?<!&)#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(", _svg_bits(sig))   # chỉ quét SVG bar; HTML số/mũi tên không tính
    if leak:
        fails.append("GFX_THEME_LEAK: màu hardcode trong SVG bar: %s" % leak[:3])


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
