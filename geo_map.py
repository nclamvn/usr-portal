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
# Tier-3 HQ pins: exact hq_city string -> (lat, lon). Public-domain city coordinates (well-known
# settlement points). Keyed by the verbatim hq_city VALUE so there is no lossy normalisation: a pin
# is placed only when the company's recorded city resolves here, else honest-null (no pin). The gate
# (verify_map MAP_PIN_FAKED) proves every pin traces to a real company.hq_city and none is invented.
CITY_COORD = {
    "Ankara": (39.93, 32.86), "Arlington, Virginia": (38.88, -77.10), "Beijing": (39.90, 116.40),
    "Berlin": (52.52, 13.40), "Bingen, Washington": (45.74, -121.46), "Chengdu, Sichuan": (30.66, 104.07),
    "Costa Mesa, California": (33.64, -117.92), "Emek Hefer": (32.36, 34.90),
    "Falls Church, Virginia": (38.88, -77.17), "Gilching": (48.11, 11.30),
    "Guangzhou, Guangdong": (23.13, 113.26), "Haifa": (32.79, 34.99), "Ho Chi Minh City": (10.82, 106.63),
    "Hunt Valley, Maryland": (39.49, -76.66), "Ismaning, Bavaria": (48.22, 11.67), "Istanbul": (41.01, 28.98),
    "Izhevsk": (56.85, 53.20), "Kahramankazan, Ankara": (40.20, 32.68), "Kunshan, Jiangsu": (31.39, 120.98),
    "Kyiv": (50.45, 30.52), "Lod": (31.95, 34.89), "Paris La Défense": (48.89, 2.24),
    "Penzberg, Bavaria": (47.75, 11.38), "Pierrelatte": (44.38, 4.69), "Poway, California": (32.96, -117.04),
    "Saint Petersburg": (59.94, 30.31), "San Diego, California": (32.72, -117.16),
    "San Luis Obispo, California": (35.28, -120.66), "San Mateo, California": (37.56, -122.32),
    "Seattle, Washington": (47.61, -122.33), "Shahin Shahr, Isfahan": (32.86, 51.55),
    "Shanghai": (31.23, 121.47), "Shenzhen (Nanshan), Guangdong": (22.53, 113.93),
    "Shenzhen, Guangdong": (22.54, 114.06), "Taufkirchen, Bavaria": (48.05, 11.62), "Uden": (51.66, 5.62),
    "Wichita, Kansas": (37.69, -97.34), "Wilsonville, Oregon": (45.30, -122.77), "Yavne": (31.88, 34.74),
    # top 42-102 makers (rank expansion to ~80% of systems)
    "Ahmedabad": (23.02, 72.57), "Alameda, California": (37.77, -122.28), "Amsterdam": (52.37, 4.90),
    "Bellevue, Washington": (47.61, -122.20), "Bethesda, Maryland": (38.98, -77.10), "Bristol": (51.45, -2.59),
    "Bruchsal": (49.12, 8.60), "Chengdu": (30.66, 104.07), "Dublin": (53.35, -6.26),
    "Guangzhou": (23.13, 113.26), "Hangzhou": (30.27, 120.15), "Hanoi": (21.03, 105.85),
    "Huizhou, Guangdong": (23.11, 114.42), "Kadima-Zoran": (32.28, 34.93), "Kazan": (55.79, 49.12),
    "Lindon, Utah": (40.34, -111.72), "Lisbon": (38.72, -9.14), "London": (51.51, -0.13),
    "Madison, Alabama": (34.70, -86.75), "Maidenhead, England": (51.52, -0.72),
    "Norristown, Pennsylvania": (40.12, -75.34), "Ożarów Mazowiecki": (52.21, 20.81),
    "Palo Alto, California": (37.44, -122.14), "Paris": (48.86, 2.35), "Paudex, Vaud": (46.51, 6.67),
    "Port Melbourne, Victoria": (-37.84, 144.94), "Providence, Rhode Island": (41.82, -71.41),
    "Richmond, Texas": (29.58, -95.76), "Rome": (41.90, 12.50), "Salt Lake City, Utah": (40.76, -111.89),
    "San Jose, California": (37.34, -121.89), "San Sebastián de los Reyes, Madrid": (40.55, -3.63),
    "Seoul": (37.57, 126.98), "Shenzhen": (22.54, 114.06), "Siegen": (50.88, 8.02),
    "South Burlington, Vermont": (44.47, -73.17), "South San Francisco, California": (37.65, -122.41),
    "Sydney": (-33.87, 151.21), "Tehran": (35.69, 51.39), "Tokyo": (35.68, 139.69),
    "Torrance, California": (33.84, -118.34), "Toulouse": (43.60, 1.44),
    "Wilmington, Massachusetts": (42.55, -71.17), "Woodinville, Washington": (47.75, -122.16),
    "Yekaterinburg": (56.84, 60.61),
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


_COAST = None


def _coast():
    """Lightweight coastline backdrop (Natural Earth 110m land, ~55KB) — used by the country locator
    so a per-country page does not inline the full 138KB choropleth geometry."""
    global _COAST
    if _COAST is None:
        rings = json.loads((ROOT / "base" / "world-land.json").read_bytes())["rings"]
        _COAST = "".join("M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in (_proj(lo, la) for lo, la in r)) + "Z"
                         for r in rings)
    return _COAST


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


def subset_map(counts, mappable, subset_n, *, rel="", fkey="", cap_en="", cap_vn=""):
    """Tier-2 FILTER map for a /segment, /airframe or /compliance term page: the manufacturer-country
    distribution OF THAT SUBSET (coastline backdrop + a proportional dot per country in the subset).
    counts: {canon_country: n} restricted to the subset. mappable: systems-with-a-country (== sum,
    == placed). subset_n: full group size (for the honest caption). fkey: 'segment:fpv' etc, so
    verify_map can recompute the subset distribution and prove every dot (MAP_FILTER_DRIFT).
    Light (coastline only, no 138KB choropleth); returns '' for an empty/uncoverable subset."""
    placed, dots = 0, []
    for c, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if not n:
            continue
        cen = CENTROID.get(c)
        if not cen:
            continue   # no centroid -> no fabricated marker (honest)
        placed += n
        x, y = _proj(cen[1], cen[0])
        r = max(3.0, 2.0 + math.sqrt(n) * 1.7) * 0.85
        op = DOT_OP[_bin(n)]
        dots.append(
            f'<a href="{_e(rel)}country/{_slug(c)}.html"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
            f'fill="var(--brass)" fill-opacity="{op}" stroke="var(--brass)" stroke-width="0.8" '
            f'data-c="{_e(c)}" data-n="{n}"><title>{_e(c)} · {n}</title></circle></a>')
    if not dots:
        return ""   # nothing to place (subset has no recorded manufacturer country)
    cap = (f'<div class="wm-cap"><span data-lang-en>{_e(cap_en)}</span>'
           f'<span data-lang-vn>{_e(cap_vn)}</span></div>') if cap_en else ""
    return (
        f'<div class="wmap wmap-mini" data-placed="{placed}" data-total="{mappable}" '
        f'data-filter="{_e(fkey)}" data-audit="wmap">'
        f'<svg class="wm-svg" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
        f'<g class="wm-base"><path d="{_coast()}"/></g>'
        f'<g class="wm-dots">{"".join(dots)}</g></svg>{cap}</div>')


def hq_map(companies, total_with_hq, *, rel="", cap_en="", cap_vn=""):
    """Tier-3 manufacturer-HQ map: a diamond PIN at each company's headquarters city. companies is a
    list of {slug, hq_city, count}. A pin is drawn only when hq_city resolves in CITY_COORD; an
    unresolved city is honest-null (no pin). Pins are visually distinct from the round country dots
    (diamond marker). data-pins == drawn pins; verify_map (MAP_PIN_FAKED) proves each pin traces to a
    real company.hq_city, none invented, and none with a resolvable HQ silently dropped."""
    pins, placed = [], 0
    for co in sorted(companies, key=lambda c: -c["count"]):
        coord = CITY_COORD.get(co["hq_city"])
        if not coord:
            continue
        placed += 1
        x, y = _proj(coord[1], coord[0])
        r = max(3.2, 2.4 + math.sqrt(co["count"]) * 1.5)
        # diamond marker (distinct from country circles); token brass
        d = f'M {x:.1f} {y-r:.1f} L {x+r:.1f} {y:.1f} L {x:.1f} {y+r:.1f} L {x-r:.1f} {y:.1f} Z'
        pins.append(
            f'<a href="{_e(rel)}company/{_e(co["slug"])}.html"><path d="{d}" fill="var(--brass)" '
            f'fill-opacity="0.85" stroke="var(--brass)" stroke-width="0.8" data-co="{_e(co["slug"])}" '
            f'data-city="{_e(co["hq_city"])}" data-n="{co["count"]}">'
            f'<title>{_e(co["hq_city"])} · {co["count"]} systems</title></path></a>')
    if not pins:
        return ""
    cap = (f'<div class="wm-cap"><span data-lang-en>{_e(cap_en)}</span>'
           f'<span data-lang-vn>{_e(cap_vn)}</span></div>') if cap_en else ""
    return (
        f'<div class="hqmap" data-pins="{placed}" data-total="{total_with_hq}" data-audit="hqmap">'
        f'<svg class="wm-svg" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
        f'<g class="wm-base"><path d="{_coast()}"/></g>'
        f'<g class="wm-dots hq-pins">{"".join(pins)}</g></svg>{cap}</div>')


def country_map(country, n, *, rel=""):
    """Locator mini-map for a /country/<slug> page: coastline backdrop + a single highlighted dot for
    THIS country, sized by its system count, linking to the full map. Light (coastline only).
    data-placed == data-total == n so verify_map's invariant holds uniformly."""
    cen = CENTROID.get(country)
    if not cen:
        return ""   # no centroid -> no fabricated marker (honest); gate sees no wmap block
    x, y = _proj(cen[1], cen[0])
    r = max(5.0, 3.0 + math.sqrt(n) * 1.7)
    dot = (f'<a href="{_e(rel)}data.html"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="var(--brass)" '
           f'fill-opacity="0.9" stroke="var(--brass)" stroke-width="1" data-c="{_e(country)}" data-n="{n}">'
           f'<title>{_e(country)} · {n}</title></circle>'
           f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+5:.1f}" fill="none" stroke="var(--brass)" '
           f'stroke-width="0.8" stroke-opacity="0.5"/></a>')
    return (
        f'<div class="wmap wmap-mini" data-placed="{n}" data-total="{n}" data-audit="wmap">'
        f'<svg class="wm-svg" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
        f'<g class="wm-base"><path d="{_coast()}"/></g><g class="wm-dots">{dot}</g></svg></div>')
