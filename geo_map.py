#!/usr/bin/env python3
"""TIP-MAP — hybrid world map of the registry's manufacturer-country distribution.

A faint per-country CHOROPLETH tint (Natural Earth 110m admin-0 polygons, Public Domain,
base/world-countries.json, projected equirectangular at build time) + a proportional DOT per
country on top. Hybrid on purpose: 110m drops micro-states (Monaco, Singapore) so a pure
choropleth would lose them; the dot layer carries every counted country, so nothing drops.

Honest framing (the moat): this is distribution by MANUFACTURER COUNTRY in the USR registry,
NOT global UAV production / market share / deployment. A country with no dot = "no system in the
registry is tagged to it", not "that country has no UAV".

Discipline that keeps the gates green: token-only paint (var(--*), 0 hex) so it flips by theme;
root <svg fill="none"> + explicit fills (verify_svg); labels are HTML (bilingual via spans, not SVG
<text>); every count + bin recomputes live from site-data (verify_map drift gate); every dot carries
data-c/data-n so MAP_UNPLACED can prove sum == registry total and no country drops silently.
"""
import json, math, pathlib, html as _html

ROOT = pathlib.Path(__file__).resolve().parent
W, H = 1000, 460
LAT_TOP, LAT_BOT = 84.0, -58.0
_POLY = None

# canon country name -> (lat, lon) centroid. The DOT layer; the gate asserts every counted country
# resolves here (MAP_UNPLACED), so none drops. Extend as the registry adds countries.
CENTROID = {
    "United States": (39.8, -98.6), "China": (35.9, 104.2), "Israel": (31.3, 34.9),
    "Germany": (51.2, 10.4), "Turkey": (39.0, 35.2), "Russia": (56.0, 49.0), "Iran": (32.4, 53.7),
    "France": (46.6, 2.4), "Ukraine": (48.9, 31.2), "United Kingdom": (53.2, -2.4),
    "Australia": (-25.3, 133.8), "India": (22.5, 79.0), "Switzerland": (46.8, 8.2),
    "Netherlands": (52.2, 5.5), "Vietnam": (16.2, 106.5), "Japan": (36.5, 138.0),
    "South Korea": (36.5, 127.9), "Spain": (40.2, -3.7), "Sweden": (62.0, 15.5), "Italy": (42.8, 12.8),
    "Ireland": (53.3, -8.0), "Portugal": (39.6, -8.2), "Poland": (52.1, 19.4), "Bulgaria": (42.7, 25.5),
    "Brazil": (-10.0, -52.0), "Monaco": (43.7, 7.4), "Norway": (61.5, 9.5), "Indonesia": (-2.5, 118.0),
    "Thailand": (15.5, 101.0), "Austria": (47.6, 14.1), "Denmark": (56.0, 9.6),
    "Singapore": (1.35, 103.8), "Estonia": (58.9, 25.7),
}
# canon name -> Natural Earth ADMIN polygon name (only where they differ); micro-states absent on 110m.
POLY_ALIAS = {"United States": "United States of America"}
# canon name -> VN label (for the HTML overlay labels; EN side is the canon name)
NAME_VN = {
    "United States": "Mỹ", "China": "Trung Quốc", "Russia": "Nga", "Iran": "Iran", "India": "Ấn Độ",
    "Australia": "Úc", "Brazil": "Brazil", "Indonesia": "Indonesia", "Israel": "Israel",
    "Turkey": "Thổ Nhĩ Kỳ", "Vietnam": "Việt Nam", "Germany": "Đức", "France": "Pháp",
    "United Kingdom": "Anh", "Japan": "Nhật Bản", "South Korea": "Hàn Quốc",
}
# only label spatially-isolated countries on the map; dense clusters (Europe, E-Asia) read via hover.
LABEL_SET = {"United States", "China", "Russia", "Iran", "India", "Australia", "Brazil",
             "Indonesia", "Israel", "Turkey", "Vietnam"}


def _e(s):
    return _html.escape("" if s is None else str(s), quote=True)


def _slug(s):
    import re
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def _proj(lon, lat):
    return (lon + 180) / 360 * W, (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * H


def _polys():
    global _POLY
    if _POLY is None:
        data = json.loads((ROOT / "base" / "world-countries.json").read_bytes())["countries"]
        _POLY = {c["name"]: c["rings"] for c in data}
    return _POLY


def _path(rings):
    out = []
    for ring in rings:
        pts = [_proj(lo, la) for lo, la in ring]
        out.append("M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(out)


def _bin(n):
    return 0 if n >= 30 else 1 if n >= 10 else 2 if n >= 5 else 3 if n >= 2 else 4


# bin -> (dot fill-opacity, faint choropleth tint-opacity); brass token, theme-safe
DOT_OP = [0.92, 0.74, 0.56, 0.42, 0.28]
TINT_OP = [0.20, 0.15, 0.11, 0.08, 0.06]
BIN_EN = ["≥ 30", "10 – 29", "5 – 9", "2 – 4", "1"]


def world_map(counts, total, *, rel="", interactive=True, mini=False, highlight=None):
    """counts: {canon_country: n} (live from site-data). total: registry total (for MAP_UNPLACED).
    rel: link prefix to country pages ("" from root, "../" from a subdir). highlight: a country to
    emphasise (country mini-map). Returns the full HTML block (svg geometry + HTML labels + legend)."""
    polys = _polys()
    # backdrop: every country faint (so absent countries read as 'not in registry', neutral)
    backdrop = "".join(f'<path d="{_path(r)}"/>' for r in polys.values())
    tint, dots, labels, placed = [], [], [], 0
    for c, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if not n:
            continue
        b = _bin(n)
        cen = CENTROID.get(c)
        href = f'{rel}country/{_slug(c)}.html'
        # choropleth tint on the country polygon (faint) when geometry exists
        pname = POLY_ALIAS.get(c, c)
        if pname in polys:
            op = TINT_OP[b] if highlight is None else (0.30 if c == highlight else 0.05)
            tint.append(f'<path d="{_path(polys[pname])}" fill="var(--brass)" fill-opacity="{op}"/>')
        # proportional dot (carries every country incl. micro-states without a polygon)
        if cen:
            placed += n
            x, y = _proj(cen[1], cen[0])
            r = max(3.0, 2.0 + math.sqrt(n) * 1.7) * (0.7 if mini else 1.0)
            op = DOT_OP[b] if highlight is None else (0.92 if c == highlight else 0.30)
            dot = (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="var(--brass)" '
                   f'fill-opacity="{op}" stroke="var(--brass)" stroke-width="0.8" '
                   f'data-c="{_e(c)}" data-n="{n}"><title>{_e(c)} · {n}</title></circle>')
            dots.append(f'<a href="{_e(href)}">{dot}</a>' if interactive else dot)
            if (not mini) and c in LABEL_SET:
                lx, ly = x / W * 100, (y + r + 11) / H * 100
                vn = NAME_VN.get(c, c)
                labels.append(
                    f'<span class="wm-lab" style="left:{lx:.2f}%;top:{ly:.2f}%">'
                    f'<span data-lang-en>{_e(c)}</span><span data-lang-vn>{_e(vn)}</span>'
                    f' <span class="wm-n">{n}</span></span>')
    legend = "".join(
        f'<span class="wm-lg"><i style="opacity:{DOT_OP[i]}"></i>{BIN_EN[i]}</span>' for i in range(5))
    legend += ('<span class="wm-lg wm-lg-none"><i></i>'
               '<span data-lang-en>not in registry</span><span data-lang-vn>chưa có trong bản đăng ký</span></span>')
    cls = "wmap" + (" wmap-mini" if mini else "")
    return (
        f'<div class="{cls}" data-placed="{placed}" data-total="{total}" data-audit="wmap">'
        f'<svg class="wm-svg" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
        f'<g class="wm-base">{backdrop}</g><g class="wm-tint">{"".join(tint)}</g>'
        f'<g class="wm-dots">{"".join(dots)}</g></svg>'
        f'<div class="wm-labels">{"".join(labels)}</div>'
        + ("" if mini else f'<div class="wm-legend">{legend}</div>')
        + '</div>')
