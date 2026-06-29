#!/usr/bin/env python3
"""Teeth cho verify_graphics — chứng 3 răng CẮN. Tiêm lỗi vào signature SVG sạch → kỳ-vọng đúng gate."""
import json, re, sys, pathlib
import verify_graphics as V

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    site = json.loads((ROOT / "out" / "site-data.json").read_bytes())
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    sig = V.sig_block(html)
    ok = True

    def run(name, mutated_html, want):
        nonlocal ok
        fails = []
        V.check_signature(mutated_html, site, fails)
        bit = any(f.startswith(want) for f in fails)
        ok = ok and bit
        print(f"{name:20s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ' + str(fails[:1])}")

    # clean positive control
    fc = []; V.check_signature(html, site, fc)
    print(f"{'CLEAN':20s} : {'PASS' if not fc else '!! ' + str(fc[:1])}"); ok = ok and not fc

    # (a) FIGURE_DRIFT — đổi một số trong sig-val
    drift = re.sub(r'(<span class="sig-val">)[^<]*', r'\g<1>9.999 zz', sig, count=1)
    run("GFX_FIGURE_DRIFT", html.replace(sig, drift), "GFX_FIGURE_DRIFT")

    # (b) NULL_FAKED — thêm một sig-fill giả
    faked = sig.replace('<div class="sigrows">', '<div class="sigrows"><svg><line class="sig-fill"/></svg>', 1)
    run("GFX_NULL_FAKED", html.replace(sig, faked), "GFX_NULL_FAKED")

    # (c) THEME_LEAK — tiêm màu hardcode vào SVG bar
    leak = sig.replace('class="sig-fill"', 'class="sig-fill" stroke="#ff0000"', 1)
    run("GFX_THEME_LEAK", html.replace(sig, leak), "GFX_THEME_LEAK")

    # --- donut (data.html) ---
    dhtml = (ROOT / "data.html").read_text(encoding="utf-8")
    fd = []; V.check_donut(dhtml, site, fd)
    print(f"{'DONUT CLEAN':20s} : {'PASS' if not fd else '!! ' + str(fd[:1])}"); ok = ok and not fd

    def rund(name, mutated, want):
        nonlocal ok
        f = []; V.check_donut(mutated, site, f)
        bit = any(x.startswith(want) for x in f); ok = ok and bit
        print(f"{name:20s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ' + str(f[:1])}")

    rund("GFX_FIGURE_DRIFT(d)", re.sub(r'<b>\d+</b>', '<b>99999</b>', dhtml, count=1), "GFX_FIGURE_DRIFT")
    rund("GFX_NULL_FAKED(d)", dhtml.replace('class="cl unk"', 'class="cl gone"'), "GFX_NULL_FAKED")
    rund("GFX_THEME_LEAK(d)", dhtml.replace('class="dk-yes"', 'class="dk-yes" stroke="#ff0000"', 1), "GFX_THEME_LEAK")

    print("-" * 48)
    print("GRAPHICS TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
