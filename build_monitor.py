#!/usr/bin/env python3
"""build_monitor.py — Mode L "World Monitor" surface (TIP-MONITOR2).

A dark-cockpit, geographic monitor of the low-altitude-economy registry. Upgraded from the TIP-L1
placeholder (hand-drawn paper-cut continents + a decorative scan-line) to a REAL map with depth and
liveness that is honest end-to-end:

  · MAP IS REAL — coastlines are Natural Earth 110m (public domain), embedded as base/world-land.json
    and projected to inline SVG paths at build time (NO deck.gl/MapLibre: a WebGL map would need external tiles
    and be opaque to THEME_PURITY/verify_svg/overlap; inline SVG keeps every gate able to read the surface).
  · DEPTH — layered bloom around each point + a radial vignette; the cockpit is THEME-RESPONSIVE — every
    plate/land/graticule/vignette fill is a CSS var(--mon-*) that flips by theme (pale cockpit in light,
    dark in dark). Still SVG paint (THEME_PURITY reads DOM background, never SVG fill) so it stays gate-clean,
    but it no longer inverts against a light page. Signal points keep their stratum hue in both themes.
  · LIVE BECAUSE THE DATA IS — each point pulses at a rhythm DERIVED from its real status (incident urgent,
    sandbox/under-construction slow, operational steady); a live UTC clock ticks; "registry last updated"
    shows the real max fetched_at from the registry (deterministic → idempotent). No decorative motion.
  · EVERY POINT HAS A SOURCE — 15 located entities, each carrying provenance; nothing invented. NO arcs
    (relations are a separate refinery step, REF5); NO invented regions (emphasis is drawn only under real
    located infrastructure).
  · NOTHING HIDDEN — the 35 entities with no location (a decree sits nowhere on a map) are not dropped;
    they scroll in a sourced "registry stream" beside the map. Density without a single fabricated point.

Discipline that keeps the gates green: the map has ZERO <text> (labels are HTML); root <svg fill="none">
+ theme-token fills (var(--mon-*)); points are <circle> (unaudited); the interior is SVG paint that follows
the theme. Exposes monitor_teaser().
"""
import json, pathlib, html as _html
from header import header
from footer import footer
from seo import meta

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "content" / "lae-monitor.json"
LAND = ROOT / "base" / "world-land.json"
OUT = ROOT / "monitor.html"

W, H = 1000, 460
LAT_TOP, LAT_BOT = 84.0, -58.0   # framing crop (Antarctica already removed from the asset)

STRATUM = {
    "vietnam": ("#e0a93f", "Việt Nam", "Vietnam"),
    "world":   ("#5cc0d6", "Thế giới", "World"),
    "china":   ("#e0685f", "Trung Quốc", "China"),
}
TYPE_VN = {"infrastructure": ("Hạ tầng", "Infrastructure"), "player": ("Doanh nghiệp", "Player"),
           "use_case": ("Ứng dụng", "Use case"), "incident": ("Sự cố", "Incident"),
           "policy": ("Chính sách", "Policy"), "standard": ("Tiêu chuẩn", "Standard"),
           "market_claim": ("Thị trường", "Market")}


def _e(s):
    return _html.escape("" if s is None else str(s), quote=True)


def _proj(lon, lat, w=W, h=H):
    return (lon + 180) / 360 * w, (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h


def _land_paths(w=W, h=H):
    rings = json.loads(LAND.read_bytes())["rings"]
    out = []
    for ring in rings:
        pts = [_proj(lo, la, w, h) for lo, la in ring]
        d = "M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"
        out.append(d)
    # one <path> with all subpaths (even-odd handles nested) — faint fill + coastline stroke
    return ('<path d="' + "".join(out) + '" fill="var(--mon-land)" fill-opacity="0.92" '
            'stroke="var(--mon-coast)" stroke-width="0.8" stroke-linejoin="round"/>')


def _graticule(w=W, h=H):
    s = ""
    for lon in range(-150, 180, 30):
        x = (lon + 180) / 360 * w
        s += f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{h}" stroke="var(--mon-grid)" stroke-width="0.7"/>'
    lat = -30
    while lat <= 60:
        if LAT_BOT < lat < LAT_TOP:
            y = (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h
            col = "var(--mon-grid-eq)" if lat == 0 else "var(--mon-grid)"
            s += f'<line x1="0" y1="{y:.1f}" x2="{w}" y2="{y:.1f}" stroke="{col}" stroke-width="0.7"/>'
        lat += 30
    return s


def _rhythm(p):
    """Pulse cadence DERIVED from the real status field — not assigned arbitrarily."""
    if p.get("entity_type") == "incident":
        return "urgent"
    st = (p.get("status") or "").lower()
    if any(k in st for k in ("thí-điểm", "thí điểm", "sandbox", "đang-xây", "đang xây", "under-construction",
                             "khởi công", "sản xuất thử", "thử-nghiệm", "thử nghiệm", "mục tiêu", "mục-tiêu")):
        return "build"
    if any(k in st for k in ("vận-hành", "vận hành", "established", "đã thiết lập", "thương-mại",
                             "thương mại", "đã xây", "đã-vận-hành")):
        return "steady"
    return "steady"


def _region_emphasis(points, w=W, h=H):
    """A soft glow UNDER each located infrastructure point only — emphasis from real data, no invented
    province boundary (that would need province polygons we do not have; drawing one would be fabrication)."""
    s = ""
    for p in points:
        if p.get("entity_type") != "infrastructure":
            continue
        x, y = _proj(p["lon"], p["lat"], w, h)
        col = STRATUM.get(p["stratum"], ("#e0a93f",))[0]
        s += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="26" fill="{col}" fill-opacity="0.07" '
              f'filter="url(#mon-soft)"/>')
    return s


def _points_svg(points, w=W, h=H, scale=1.0, interactive=True):
    seen = {}
    out = []
    for p in points:
        x, y = _proj(p["lon"], p["lat"], w, h)
        key = (round(x, 1), round(y, 1))
        n = seen.get(key, 0)
        seen[key] = n + 1
        if n:
            x += (n * 6) * scale
            y -= (n * 6) * scale
        col = STRATUM.get(p["stratum"], ("#e0a93f",))[0]
        rc, rh = 3.4 * scale, 8.5 * scale
        data = ""
        if interactive:
            data = (f' data-name="{_e(p["name"])}" data-place="{_e(p.get("place_vn") or p.get("location"))}"'
                    f' data-type="{_e(p["entity_type"])}" data-stratum="{_e(p["stratum"])}"'
                    f' data-status="{_e(p.get("status") or "")}" data-date="{_e(p.get("date") or "")}"'
                    f' data-source="{_e(p.get("source") or "")}" data-tier="{_e(p.get("tier") or "")}"'
                    f' data-url="{_e(p.get("url") or "")}" tabindex="0" role="button"'
                    f' aria-label="{_e(p["name"])}"')
        g = (f'<g class="mon-pin mon-r-{_rhythm(p)}" data-st="{_e(p["stratum"])}" '
             f'data-ty="{_e(p["entity_type"])}"{data}>'
             f'<circle class="mon-halo" cx="{x:.1f}" cy="{y:.1f}" r="{rh:.1f}" fill="{col}" '
             f'fill-opacity="0.16" filter="url(#mon-glow)"/>'
             f'<circle class="mon-halo2" cx="{x:.1f}" cy="{y:.1f}" r="{rh*0.6:.1f}" fill="{col}" '
             f'fill-opacity="0.30" filter="url(#mon-soft)"/>'
             f'<circle class="mon-core" cx="{x:.1f}" cy="{y:.1f}" r="{rc:.1f}" fill="{col}"/>')
        if p.get("entity_type") == "incident":
            g += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rc+3:.1f}" fill="none" stroke="{col}" '
                  f'stroke-width="1" stroke-opacity="0.7"/>')
        if interactive:
            g += f'<circle class="mon-hit" cx="{x:.1f}" cy="{y:.1f}" r="{14*scale:.1f}" fill="transparent"/>'
        g += "</g>"
        out.append(g)
    return "".join(out)


def world_svg(points, w=W, h=H, scale=1.0, interactive=True, cls="mon-svg"):
    defs = (
        '<defs>'
        '<radialGradient id="mon-vig" cx="50%" cy="44%" r="78%">'
        '<stop offset="0%" stop-color="var(--mon-ocean)"/><stop offset="62%" stop-color="var(--mon-ocean-2)"/>'
        '<stop offset="100%" stop-color="var(--mon-ocean-3)"/></radialGradient>'
        '<filter id="mon-glow" x="-120%" y="-120%" width="340%" height="340%">'
        '<feGaussianBlur stdDeviation="5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="mon-soft" x="-120%" y="-120%" width="340%" height="340%">'
        '<feGaussianBlur stdDeviation="2.4"/></filter>'
        '</defs>')
    vig2 = (f'<rect x="0" y="0" width="{w}" height="{h}" fill="none" stroke="var(--mon-vignette)" '
            f'stroke-width="36" stroke-opacity="0.55"/>')  # inner edge darkening (vignette frame)
    return (
        f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="World monitor map" '
        f'preserveAspectRatio="xMidYMid meet">'
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="url(#mon-vig)"/>'
        f'{defs}{_graticule(w, h)}{_land_paths(w, h)}{_region_emphasis(points, w, h)}'
        f'{_points_svg(points, w, h, scale, interactive)}{vig2}'
        f'</svg>')


def _bi(en, vn):
    return f'<span data-lang-en>{en}</span><span data-lang-vn>{vn}</span>'


def _legend(points):
    counts = {}
    for p in points:
        counts[p["stratum"]] = counts.get(p["stratum"], 0) + 1
    items = ""
    for st, (col, vn, en) in STRATUM.items():
        items += (f'<button class="mon-filt" data-filter="st" data-val="{st}" aria-pressed="true">'
                  f'<span class="mon-dot" style="background:{col}"></span>{_bi(en, vn)}'
                  f'<span class="mon-ct">{counts.get(st, 0)}</span></button>')
    return items


def _type_filters(points):
    types = []
    for p in points:
        if p["entity_type"] not in types:
            types.append(p["entity_type"])
    out = ""
    for t in types:
        vn, en = TYPE_VN.get(t, (t, t))
        out += (f'<button class="mon-filt mon-filt-ty" data-filter="ty" data-val="{t}" aria-pressed="true">'
                f'{_bi(en, vn)}</button>')
    return out


def _support_panel(points):
    """Supporting graphic UNDER the map (balances the column against the stream, and earns its space):
    a SIGNAL KEY that explains the pulse cadences (otherwise the multi-rhythm glow is unreadable) +
    live distribution bars. Every count is derived from the 15 located points — nothing hardcoded."""
    cad = {"urgent": 0, "build": 0, "steady": 0}
    strat = {"vietnam": 0, "world": 0, "china": 0}
    types = {}
    for p in points:
        cad[_rhythm(p)] = cad.get(_rhythm(p), 0) + 1
        strat[p["stratum"]] = strat.get(p["stratum"], 0) + 1
        types[p["entity_type"]] = types.get(p["entity_type"], 0) + 1
    CAD = [("urgent", "#e0685f", "Urgent", "Khẩn", "incident · fast", "sự cố · nhịp gấp"),
           ("build", "#d9a441", "Building", "Đang dựng", "sandbox / under-construction · slow",
            "thí-điểm / đang-xây · nhịp chậm"),
           ("steady", "#5cc0d6", "Operational", "Vận hành", "in service · steady", "đã vận-hành · đều")]
    rows = ""
    for key, col, en, vn, den, dvn in CAD:
        rows += (f'<div class="mon-cad-row"><span class="mon-cad-dot mon-r-{key}" style="--c:{col}"></span>'
                 f'<span class="mon-cad-lab">{_bi(en, vn)}</span>'
                 f'<span class="mon-cad-desc">{_bi(den, dvn)}</span>'
                 f'<span class="mon-cad-ct">{cad.get(key, 0)}</span></div>')
    n = max(1, len(points))
    seg = ""
    for st in ("vietnam", "world", "china"):
        c = strat.get(st, 0)
        if c:
            col = STRATUM[st][0]
            seg += f'<span class="mon-seg" style="width:{c/n*100:.1f}%;background:{col}" title="{c}"></span>'
    tychips = ""
    for t, c in sorted(types.items(), key=lambda kv: -kv[1]):
        vn, en = TYPE_VN.get(t, (t, t))
        tychips += (f'<span class="mon-tychip"><span class="mon-tychip-n">{c}</span>'
                    f'{_bi(en, vn)}</span>')
    return (
        '<div class="mon-support">'
        f'<div class="mon-sup-h">{_bi("Signal key", "Khoá tín hiệu")}'
        f'<span class="mon-sup-sub">{_bi("pulse cadence = real status", "nhịp đập = trạng-thái thật")}</span></div>'
        f'<div class="mon-cad">{rows}</div>'
        f'<div class="mon-sup-bars">'
        f'<div class="mon-bar-h">{_bi("Located by stratum", "Đã định-vị theo tầng")}<span>{len(points)}</span></div>'
        f'<div class="mon-bar">{seg}</div>'
        f'<div class="mon-bar-h">{_bi("By type", "Theo loại")}</div>'
        f'<div class="mon-tyrow">{tychips}</div>'
        '</div></div>')


def _stream(non_located):
    """STEP 5 — the un-mappable but real: 35 sourced entities scrolling beside the map. Each carries
    tier + the provenance most apt for its type (scope for market_claim, issuer/doc_id for policy/standard)."""
    rows = ""
    for p in non_located:
        col = STRATUM.get(p["stratum"], ("#7f8c98",))[0]
        vn, en = TYPE_VN.get(p["entity_type"], (p["entity_type"], p["entity_type"]))
        prov = p.get("scope") or p.get("issuer") or p.get("doc_id") or ""
        prov_html = f'<span class="mon-strm-prov">{_e(prov)}</span>' if prov else ""
        src = p.get("source") or ""
        tier = p.get("tier") or "?"
        link_open = f'<a href="{_e(p["url"])}" target="_blank" rel="noopener">' if p.get("url") else "<span>"
        link_close = "</a>" if p.get("url") else "</span>"
        rows += (
            f'<li class="mon-strm-row" data-st="{_e(p["stratum"])}">'
            f'<span class="mon-strm-bar" style="background:{col}"></span>'
            f'<div class="mon-strm-main">'
            f'<div class="mon-strm-top"><span class="mon-strm-ty">{_bi(en, vn)}</span>'
            f'<span class="mon-strm-tier" data-t="{_e(tier)}">{_e(tier)}</span></div>'
            f'{link_open}<span class="mon-strm-nm">{_e(p["name"])}</span>{link_close}'
            f'<div class="mon-strm-meta">{prov_html}<span class="mon-strm-src">{_e(src)}</span></div>'
            f'</div></li>')
    return rows


def page(doc):
    points = doc["points"]
    non_located = doc.get("non_located", [])
    last_cap = (doc.get("last_capture") or "")[:10]
    title = "World Monitor — USR"
    head = meta(title, "Bản đồ trực địa kinh tế tầm thấp — mỗi điểm là một thực thể có nguồn trong registry.",
                "monitor.html")
    stage = world_svg(points, interactive=True)
    body = f"""{header("", "monitor")}
<main class="mon-wrap">
  <header class="mon-head">
    <span class="mon-eyebrow">{_bi("Mode L · Live registry map", "Mode L · Bản đồ registry")}</span>
    <h1 class="mon-title">{_bi("World Monitor", "Bản đồ trực địa")}</h1>
    <p class="mon-lede">{_bi(
        "Every point is a real entity in the low-altitude-economy registry, plotted at its true location and "
        "carrying its source. Nothing is invented; entities without a known location appear in the stream, "
        "never as a point.",
        "Mỗi điểm là một thực thể có thật trong registry kinh tế tầm thấp, đặt đúng vị trí và mang theo nguồn. "
        "Không có gì bịa; thực thể chưa rõ vị trí nằm ở dòng dữ liệu, không thành điểm.")}</p>
  </header>

  <div class="mon-statusbar">
    <span class="mon-stat"><span class="mon-stat-k">{_bi("Watching", "Đang theo dõi")}</span>
      <span class="mon-stat-v" id="mon-watch">{len(points)}</span></span>
    <span class="mon-stat"><span class="mon-stat-k">{_bi("Stream", "Dòng dữ liệu")}</span>
      <span class="mon-stat-v">{len(non_located)}</span></span>
    <span class="mon-stat"><span class="mon-stat-k">{_bi("Registry updated", "Registry cập nhật")}</span>
      <span class="mon-stat-v" id="mon-updated">{_e(last_cap)}</span></span>
    <span class="mon-stat mon-stat-clock"><span class="mon-stat-k">UTC</span>
      <span class="mon-stat-v" id="mon-utc">--:--:--</span></span>
  </div>

  <div class="mon-controls">
    <div class="mon-filtrow" role="group" aria-label="Stratum filter">{_legend(points)}</div>
    <div class="mon-filtrow mon-filtrow-ty" role="group" aria-label="Type filter">{_type_filters(points)}</div>
  </div>

  <div class="mon-layout">
   <div class="mon-col-l">
    <div class="mon-stage" id="mon-stage">
      {stage}
      <div class="mon-readout" id="mon-readout" hidden></div>
      <aside class="mon-panel" id="mon-panel" aria-live="polite" hidden>
        <button class="mon-x" id="mon-x" aria-label="Close">×</button>
        <div class="mon-p-type" id="mp-type"></div>
        <h2 class="mon-p-name" id="mp-name"></h2>
        <dl class="mon-p-dl">
          <div><dt>{_bi("Location","Vị trí")}</dt><dd id="mp-place"></dd></div>
          <div><dt>{_bi("Status","Trạng thái")}</dt><dd id="mp-status"></dd></div>
          <div><dt>{_bi("Date","Mốc")}</dt><dd id="mp-date"></dd></div>
          <div><dt>{_bi("Source","Nguồn")}</dt><dd id="mp-source"></dd></div>
        </dl>
        <a class="mon-p-link" id="mp-link" href="#" target="_blank" rel="noopener">{_bi("Open source","Mở nguồn")} ↗</a>
      </aside>
      <p class="mon-hint" id="mon-hint">{_bi("Hover for a readout, tap for the source.","Rê để xem nhanh, chạm để mở nguồn.")}</p>
    </div>
    {_support_panel(points)}
   </div>

    <aside class="mon-stream" aria-label="Registry stream (non-located)">
     <div class="mon-stream-inner">
      <div class="mon-stream-h">{_bi("Registry stream", "Dòng registry")}
        <span class="mon-stream-sub">{_bi("real · sourced · no map position", "có thật · có nguồn · không vị trí bản đồ")}</span></div>
      <ul class="mon-stream-list">{_stream(non_located)}</ul>
     </div>
    </aside>
  </div>

  <p class="mon-foot">{_bi(
      "Phase 1: a static map derived from the registry. Connection arcs await a sourced relation layer "
      "(refinery REF5); live air-traffic and event overlays (clearly labelled, delayed, unverified) are a "
      "later phase. The registry never reads back from the map.",
      "Giai đoạn 1: bản đồ tĩnh dựng từ registry. Cung nối chờ lớp quan hệ có nguồn (refinery REF5); lớp "
      "không-lưu trực tiếp và sự kiện (gắn nhãn rõ, có độ trễ, chưa kiểm chứng) thuộc giai đoạn sau. "
      "Registry không bao giờ nhận ngược từ bản đồ.")}</p>
</main>
{footer("")}
<script src="base/base.js"></script>
<script>{MON_JS}</script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>"""
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{head}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
</head>
<body>
{body}
</body>
</html>
"""


def monitor_teaser(prefix=""):
    """Compact, non-interactive preview for the homepage — same real-coastline cockpit, smaller, no
    panel/stream/clock; one overlay link into the surface. Self-contained (dark in SVG only)."""
    doc = json.loads(DATA.read_bytes())
    points = doc["points"]
    svg = world_svg(points, scale=1.0, interactive=False, cls="mon-svg mon-svg-mini")
    n = len(points)
    return f"""<section class="mteaser reveal">
  <div class="mteaser-in">
    <div class="mteaser-txt">
      <span class="mteaser-eye">{_bi("Mode L · Live registry map","Mode L · Bản đồ registry")}</span>
      <h2 class="mteaser-h">{_bi("The world, on the record","Thế giới, có hồ sơ")}</h2>
      <p class="mteaser-p">{_bi(
          f"{n} located entities from the low-altitude-economy registry, each plotted at its true position "
          "and carrying its source. Open the monitor to inspect any point.",
          f"{n} thực thể đã định vị từ registry kinh tế tầm thấp, mỗi điểm đặt đúng vị trí và mang theo nguồn. "
          "Mở bản đồ để soi từng điểm.")}</p>
      <a class="mteaser-cta" href="{prefix}monitor.html">{_bi("Open World Monitor","Mở Bản đồ trực địa")} →</a>
    </div>
    <a class="mteaser-map" href="{prefix}monitor.html" aria-label="Open World Monitor">{svg}</a>
  </div>
</section>"""


MON_JS = r"""
(function(){
  var stage=document.getElementById('mon-stage'); if(!stage) return;
  var panel=document.getElementById('mon-panel'), hint=document.getElementById('mon-hint');
  var readout=document.getElementById('mon-readout');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var TY={infrastructure:['Hạ tầng','Infrastructure'],player:['Doanh nghiệp','Player'],
          use_case:['Ứng dụng','Use case'],incident:['Sự cố','Incident'],
          policy:['Chính sách','Policy'],standard:['Tiêu chuẩn','Standard'],market_claim:['Thị trường','Market']};
  function lang(){return document.documentElement.getAttribute('data-lang')==='vn'?1:0;}

  // live UTC clock — ticks only when motion is allowed; else a static label (no fake liveness)
  var utc=document.getElementById('mon-utc');
  function tick(){ if(!utc) return; var d=new Date();
    utc.textContent=d.toISOString().slice(11,19); }
  if(utc){ if(reduce){ utc.textContent='— motion off'; } else { tick(); setInterval(tick,1000); } }

  function open(g){
    var d=g.dataset;
    document.getElementById('mp-name').textContent=d.name;
    var ty=document.getElementById('mp-type'); var tt=TY[d.type]||[d.type,d.type];
    ty.textContent=tt[lang()]; ty.setAttribute('data-st',d.stratum);
    document.getElementById('mp-place').textContent=d.place||'—';
    document.getElementById('mp-status').textContent=d.status||'—';
    document.getElementById('mp-date').textContent=d.date||'—';
    var src=document.getElementById('mp-source');
    src.textContent=(d.source||'—')+(d.tier?(' · '+(lang()?'hạng ':'tier ')+d.tier):'');
    var lk=document.getElementById('mp-link');
    if(d.url){lk.href=d.url; lk.style.display='';} else {lk.style.display='none';}
    panel.hidden=false; if(hint) hint.style.display='none';
    stage.querySelectorAll('.mon-pin.sel').forEach(function(e){e.classList.remove('sel');});
    g.classList.add('sel');
  }
  // hover → mini readout (HTML, not SVG text → overlap-clean); positioned at the pin
  function showReadout(g){
    if(!readout) return; var d=g.dataset;
    readout.innerHTML='<b>'+d.name+'</b><span>'+(d.tier?('tier '+d.tier):'')
      +(d.date?(' · '+d.date):'')+'</span>';
    var sr=stage.getBoundingClientRect(), gr=g.getBoundingClientRect();
    readout.hidden=false;
    var left=gr.left-sr.left+gr.width/2, top=gr.top-sr.top;
    readout.style.left=left+'px'; readout.style.top=(top-10)+'px';
  }
  function hideReadout(){ if(readout) readout.hidden=true; }

  stage.querySelectorAll('.mon-pin').forEach(function(g){
    g.addEventListener('click',function(){open(g);});
    g.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();open(g);}});
    g.addEventListener('mouseenter',function(){showReadout(g);});
    g.addEventListener('mouseleave',hideReadout);
    g.addEventListener('focus',function(){showReadout(g);});
    g.addEventListener('blur',hideReadout);
  });
  var x=document.getElementById('mon-x');
  if(x) x.addEventListener('click',function(){panel.hidden=true;
    stage.querySelectorAll('.mon-pin.sel').forEach(function(e){e.classList.remove('sel');});
    if(hint) hint.style.display='';});

  // filters: a pin shows only if BOTH its stratum and type are active; "watching" counts live
  var stOn={}, tyOn={}, watch=document.getElementById('mon-watch');
  document.querySelectorAll('.mon-filt').forEach(function(b){
    var f=b.dataset.filter, v=b.dataset.val; (f==='st'?stOn:tyOn)[v]=true;
    b.addEventListener('click',function(){
      var on=b.getAttribute('aria-pressed')==='true'; b.setAttribute('aria-pressed',(!on).toString());
      (f==='st'?stOn:tyOn)[v]=!on; apply();
    });
  });
  function apply(){
    var shown=0;
    stage.querySelectorAll('.mon-pin').forEach(function(g){
      var ok=stOn[g.dataset.st]!==false && tyOn[g.dataset.ty]!==false;
      g.style.display=ok?'':'none'; if(ok) shown++;
    });
    // stream rows follow the stratum filter too (type filter is map-only)
    document.querySelectorAll('.mon-strm-row').forEach(function(r){
      r.style.display = stOn[r.dataset.st]!==false ? '' : 'none';
    });
    if(watch) watch.textContent=shown;
  }
  // (column heights are balanced in pure CSS — the stream stretches to the left column via grid; no JS layout)
})();
"""


def main():
    doc = json.loads(DATA.read_bytes())
    OUT.write_text(page(doc))
    pts = doc["points"]
    print(f"monitor.html: {len(pts)} points + {len(doc.get('non_located', []))} stream "
          f"({sum(1 for p in pts if p['stratum']=='vietnam')} vn · "
          f"{sum(1 for p in pts if p['stratum']=='world')} world · "
          f"{sum(1 for p in pts if p['stratum']=='china')} china) · "
          f"land rings={len(json.loads(LAND.read_bytes())['rings'])}")


if __name__ == "__main__":
    main()
