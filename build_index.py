#!/usr/bin/env python3
"""TIP-HOMEPAGE — homepage in the team-approved LAYOUT (mock-homepage-v2.html) rendered with the
EXISTING design-system (font/token/dark/i18n), NOT the mock's Space Grotesk/amber. Brand-lead =
"Vietnam UAV Intelligence Platform" (masthead), publisher = Uncrewed Systems Review (K-6 deviation,
noted in ledger). Ten blocks: topbar+ticker -> masthead -> hero(1+3) -> TOOL/00 compare ->
TREND/01 -> INFO/02 signature -> REPORT/03 -> HOT/04 -> footer. Every figure LIVE from site-data
(zero-fab, recompute), every card binds a REAL slug, honest-null shown. verify_homepage gates it.
"""
import json, math, pathlib
from build_reference import bilingual, esc, friendly, maker_model
from footer import footer
from header import header
from seo import meta as seo_meta, website_ld
from build_newsroom import load_articles, TYPE_LABEL, _weight, _kicker, _meta

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
OUT = ROOT / "index.html"

ARROW = ('<svg class="ar" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
         '<path d="M4.5 12H16.5M11 6.5L16.5 12L11 17.5" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def live_facts(site):
    """Real, live figures from site-data — never hardcoded (the '13 vs 28' bug dies here)."""
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    agg = site["aggregates"]
    countries = len({(e.get("manufacturer_country") or {}).get("value") for e in ents
                     if (e.get("manufacturer_country") or {}).get("value")})
    makers = len({(e.get("manufacturer") or {}).get("value") for e in ents
                  if (e.get("manufacturer") or {}).get("value")})
    segments = len({(e.get("market_segment") or {}).get("value") for e in ents
                    if (e.get("market_segment") or {}).get("value")})
    fill = agg["spec_fill_rate"]
    present = sum(d["present"] for d in fill.values()); total = sum(d["total"] for d in fill.values())
    coverage = round(100 * present / total) if total else 0
    ndaa_true = sum(1 for e in ents if (e.get("ndaa_compliant") or {}).get("value") is True)
    ndaa_present = sum(1 for e in ents if (e.get("ndaa_compliant") or {}).get("value") is not None)
    country_rank = sorted(
        {(e.get("manufacturer_country") or {}).get("value"): 0 for e in ents}.keys(),
        key=lambda c: -sum(1 for e in ents if (e.get("manufacturer_country") or {}).get("value") == c))
    cc = {}
    for e in ents:
        c = (e.get("manufacturer_country") or {}).get("value")
        if c:
            cc[c] = cc.get(c, 0) + 1
    country_top = sorted(cc.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    # extra keys for build_bundle's record-status masthead (render_masthead) — superset, no second facts fn
    def tally(getter):
        d = {}
        for e in ents:
            v = getter(e)
            if v:
                d[v] = d.get(v, 0) + 1
        return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))
    blue_verified = sum(1 for e in ents if (e.get("blue_uas") or {}).get("status") == "verified"
                        and (e.get("blue_uas") or {}).get("value") is True)
    ndaa_verified = sum(1 for e in ents if (e.get("ndaa_compliant") or {}).get("status") == "verified"
                        and (e.get("ndaa_compliant") or {}).get("value") is True)
    return {"entities": len(ents), "companies": makers, "countries": countries, "segments": segments,
            "coverage": coverage, "ndaa_true": ndaa_true, "ndaa_present": ndaa_present,
            "country_top": country_top,
            "blue_verified": blue_verified, "ndaa_verified": ndaa_verified,
            "disputed_live": agg["field_status_counts"].get("disputed", 0),
            "seg_rank": tally(lambda e: (e.get("market_segment") or {}).get("value")),
            "country_rank": tally(lambda e: (e.get("manufacturer_country") or {}).get("value"))}


# ---- record-status masthead (used by build_bundle's offline single-file export) ----
def stat_cell(value, cap_en, cap_vn):
    s = str(value)
    return (f'<div class="stat-cell"><span class="statfig" data-countup '
            f'style="min-width:{len(s)}ch">{esc(s)}</span>'
            f'<span class="cap mono">{bilingual(cap_en, cap_vn)}</span></div>')


def ranked_list(rank, kind, labels, top_n):
    if not rank:
        return ""
    top = rank[:top_n]
    maxn = top[0][1] or 1
    rows = []
    for i, (val, n) in enumerate(top):
        lab = friendly(kind, val, labels) if kind else esc(str(val))
        w = round(100 * n / maxn)
        cls = "rank-row top" if i == 0 else "rank-row"
        rows.append(f'<div class="{cls}"><span class="rl">{lab}</span>'
                    f'<span class="rn mono">{n}</span><i class="rib" style="--w:{w}%"></i></div>')
    return "".join(rows)


def render_masthead(f, labels):
    return (
        f'<div class="masthead reg-frame" data-audit="masthead">'
        f'<span class="reg-tr"></span><span class="reg-bl"></span>'
        f'<div class="stat-strip">'
        + stat_cell(f["entities"], "systems", "hệ thống")
        + stat_cell(f["blue_verified"], "Blue UAS", "Blue UAS")
        + stat_cell(f["ndaa_verified"], "NDAA compliant", "tuân thủ NDAA")
        + stat_cell(f["disputed_live"], "disputed fields", "field tranh chấp")
        + stat_cell(f'{f["coverage"]}%', "spec coverage", "độ phủ spec")
        + '</div>'
        f'<div class="rank-cols">'
        f'<div class="rank"><div class="rank-h mono">{bilingual("By segment", "Theo phân khúc")}</div>'
        f'{ranked_list(f["seg_rank"], "segment", labels, 8)}</div>'
        f'<div class="rank"><div class="rank-h mono">{bilingual("By country", "Theo quốc gia")}</div>'
        f'{ranked_list(f["country_rank"], None, labels, 8)}</div>'
        f'</div></div>')


def _fnum(x):
    return ("%g" % x).replace(".", ",") if (isinstance(x, float) and x != int(x)) else f"{int(x):,}".replace(",", ".")


# ---- INFO/02 capability scatter (live: every system with both MTOW + range, log×log, by segment) ----
def scatter_svg(site):
    """The whole fleet in one frame: one dot per UAV that has BOTH mtow_kg and max_range_km recorded
    (honest-null: systems missing either are not plotted). Positions recompute log×log from registry;
    colour = market_segment (top-5 + other). Dots coloured via CSS token classes; root fill=none so
    verify_svg passes and verify_graphics finds no hardcoded hex. Labels/legend are HTML (overlap-safe)."""
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]

    def num(e, k):
        v = (e.get(k) or {}).get("value")
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    pts = []
    for e in uavs:
        m, r = num(e, "mtow_kg"), num(e, "max_range_km")
        if m and r and m > 0 and r > 0:
            pts.append((m, r, (e.get("market_segment") or {}).get("value")))
    if not pts:
        return ""
    ms = [m for m, _, _ in pts]
    rs = [r for _, r, _ in pts]
    xmin, xmax, ymin, ymax = min(ms), max(ms), min(rs), max(rs)
    lx0, lx1, ly0, ly1 = math.log10(xmin), math.log10(xmax), math.log10(ymin), math.log10(ymax)
    W, H, PAD = 1000, 440, 10
    pw, ph = W - 2 * PAD, H - 2 * PAD

    def px(m):
        return PAD + (math.log10(m) - lx0) / (lx1 - lx0) * pw

    def py(r):
        return PAD + ph - (math.log10(r) - ly0) / (ly1 - ly0) * ph

    from collections import Counter
    cnt = Counter(seg for _, _, seg in pts if seg)
    top = [seg for seg, _ in cnt.most_common(5)]
    segcls = {seg: f"sc{i + 1}" for i, seg in enumerate(top)}

    grid = []
    for d in range(math.ceil(lx0), math.floor(lx1) + 1):
        gx = px(10 ** d)
        grid.append(f'<line class="scat-grid" x1="{gx:.1f}" y1="{PAD}" x2="{gx:.1f}" y2="{PAD + ph}"/>')
    for d in range(math.ceil(ly0), math.floor(ly1) + 1):
        gy = py(10 ** d)
        grid.append(f'<line class="scat-grid" x1="{PAD}" y1="{gy:.1f}" x2="{PAD + pw}" y2="{gy:.1f}"/>')
    dots = [f'<circle class="dot {segcls.get(seg, "sc6")}" cx="{px(m):.1f}" cy="{py(r):.1f}" r="4.5"/>'
            for m, r, seg in pts]

    labels = site["labels"]["segment"]
    leg = ""
    for i, seg in enumerate(top):
        sl = labels.get(seg, {})
        leg += (f'<span class="scl"><i class="sw sc{i + 1}"></i>'
                f'{bilingual(sl.get("en", seg), sl.get("vn", seg))}</span>')
    leg += f'<span class="scl"><i class="sw sc6"></i>{bilingual("other", "khác")}</span>'

    return (
        '<section class="sigwrap" data-audit="sig"><div class="scat">'
        f'<div class="scat-yax mono"><span>{_fnum(ymax)}</span>'
        f'<span class="scat-axt">{bilingual("Range km", "Tầm bay km")}</span><span>{_fnum(ymin)}</span></div>'
        f'<svg class="scat-svg" viewBox="0 0 {W} {H}" fill="none" aria-hidden="true">'
        f'{"".join(grid)}{"".join(dots)}</svg></div>'
        f'<div class="scat-xax mono"><span>{_fnum(xmin)}</span>'
        f'<span class="scat-axt">MTOW kg</span><span>{_fnum(xmax)}</span></div>'
        f'<div class="scat-legend">{leg}</div>'
        f'<p class="sig-cap">{bilingual("One dot per system with both MTOW and range recorded (" + str(len(pts)) + " of " + str(len(uavs)) + "); both axes log scale.", "Mỗi chấm một hệ thống có cả MTOW và tầm bay (" + str(len(pts)) + "/" + str(len(uavs)) + "); cả hai trục thang log.")}</p></section>')


# ---- block helpers (each binds REAL slugs + live numbers) ----
def section_label(code, en, vn):
    return (f'<div class="section-label"><span class="code">{code}</span>'
            f'<h2>{bilingual(en, vn)}</h2><span class="rule"></span></div>')


def cat_of(fm):
    en, vn = TYPE_LABEL.get(fm.get("type"), (fm.get("type", ""), fm.get("type", "")))
    return bilingual(en, vn)


def ticker(f, arts):
    lead = arts[0] if arts else None
    items = []
    if lead:
        items.append(f'<span><b>NEWSROOM</b> — {esc(lead["title"])}</span>')
    items.append(f'<span><b>DATA</b> — {bilingual("USR registry", "Bản đăng ký USR")}: '
                 f'{f["entities"]} {bilingual("systems", "hệ thống")} · {f["companies"]} '
                 f'{bilingual("manufacturers", "nhà sản xuất")} · {f["countries"]} '
                 f'{bilingual("countries", "quốc gia")}</span>')
    items.append(f'<span><b>DATA</b> — NDAA: {f["ndaa_true"]}/{f["ndaa_present"]} '
                 f'{bilingual("with data meet the standard", "có dữ liệu đạt chuẩn")}, '
                 f'{f["entities"] - f["ndaa_present"]} {bilingual("not recorded", "chưa ghi nhận")}</span>')
    return ('<div class="topbar"><div class="topbar-in"><span class="tag"><span class="livedot"></span>LIVE</span>'
            f'<div class="ticker-wrap"><div class="ticker">{"".join(items)}</div></div>'
            f'<span class="mono tb-co">{bilingual("Vietnam · HCMC", "Việt Nam · TP.HCM")}</span></div></div>')


def masthead(f):
    return (
        '<div class="hp-mast"><div class="hp-mast-in"><div class="mh-left">'
        f'<div class="mh-sub mono">{bilingual("News · Intelligence · Data · Community", "Tin · Tình báo · Dữ liệu · Cộng đồng")}</div>'
        '<h1>Vietnam UAV<br>Intelligence Platform</h1>'
        '</div>'
        '<div class="mh-right">'
        '<div class="mh-coords mono">10.7769°N · 106.7009°E</div>'
        f'<div class="mh-tag mono">{bilingual("UAV data & knowledge platform · Uncrewed Systems Review", "Nền tảng dữ liệu & tri thức UAV · Uncrewed Systems Review")}</div>'
        '</div></div></div>')


def hero(arts):
    if not arts:
        return ""
    main = arts[0]
    side = arts[1:4]
    side_html = ""
    for fm in side:
        side_html += (
            f'<a class="side-story" href="news/{esc(fm["slug"])}.html">'
            f'<div class="cat mono">{cat_of(fm)}</div>'
            f'<h3>{esc(fm["title"])}</h3></a>')
    dek = esc(main.get("dek") or main.get("title"))
    return (
        '<section class="hero-grid">'
        f'<a class="hero-main" href="news/{esc(main["slug"])}.html">'
        f'<div class="eyebrow"><span class="dot"></span>{cat_of(main)}</div>'
        f'<h2>{esc(main["title"])}</h2><p class="dek">{dek}</p>'
        f'<div class="hero-meta mono"><span>{bilingual("sourced", "có nguồn dẫn")}</span>'
        f'<span>{esc(str(main.get("date", "")))}</span></div></a>'
        f'<div class="hero-side">{side_html}</div></section>')


def _fmt(v):
    if isinstance(v, float) and v != int(v):
        return ("%g" % v).replace(".", ",")
    if isinstance(v, (int, float)):
        return str(int(v))
    return esc(str(v))


def compare_preview(ents, labels):
    """3 best-documented UAVs, real specs, honest-null '-- chưa ghi nhận'. best = higher range/endurance."""
    def score(e):
        return sum(1 for k in ("max_range_km", "endurance_min", "mtow_kg", "market_segment")
                   if (e.get(k) or {}).get("value") is not None)
    picks, seen = [], set()
    for e in sorted(ents, key=lambda e: (-score(e), e["canonical_id"])):
        fam = e.get("family_id")
        if fam in seen:
            continue
        seen.add(fam); picks.append(e)
        if len(picks) == 3:
            break
    ROWS = [("max_range_km", "Range", "Tầm bay", "km", True),
            ("endurance_min", "Endurance", "Thời gian bay", bilingual("min", "phút"), True),
            ("mtow_kg", "MTOW", "MTOW", "kg", False),
            ("market_segment", "Segment", "Phân khúc", "", None)]
    head = "".join(f'<th class="drone-col">{esc(maker_model(e)[1])}</th>' for e in picks)
    body = ""
    for key, en, vn, unit, more_better in ROWS:
        vals = [(e.get(key) or {}).get("value") for e in picks]
        best_v = None
        if more_better:
            nums = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
            best_v = max(nums) if nums else None
        cells = ""
        for v in vals:
            if v is None:
                cells += f'<td class="nullv">{bilingual("not recorded", "chưa ghi nhận")}</td>'
            elif key == "market_segment":
                cells += f'<td>{friendly("segment", v, labels)}</td>'
            else:
                u = unit if isinstance(unit, str) else ""
                cls = ' class="best"' if (best_v is not None and v == best_v) else ""
                cells += f'<td{cls}>{_fmt(v)} {u}</td>' if u else f'<td{cls}>{_fmt(v)} {unit}</td>'
        body += f'<tr><td class="spec-label">{bilingual(en, vn)}</td>{cells}</tr>'
    return (
        '<div class="compare-panel">'
        '<div class="compare-head"><div>'
        f'<div class="mono ch-k">{bilingual("Quick compare", "So sánh nhanh")}</div>'
        f'<p>{bilingual("Pick up to 4 systems to compare specs. Empty cells are data not yet recorded, never invented.", "Chọn tối đa 4 hệ thống để so thông số. Ô trống là dữ liệu chưa ghi nhận, không bịa.")}</p>'
        f'</div><a class="compare-cta" href="compare.html">{bilingual("Full compare", "So sánh đầy đủ")} →</a></div>'
        f'<table class="compare-table"><tr><th>{bilingual("Spec", "Thông số")}</th>{head}</tr>{body}</table>'
        f'<div class="compare-foot mono"><span>{bilingual("Data from the USR registry · every cell has source + tier", "Dữ liệu từ bản đăng ký USR · mỗi ô có nguồn + tier")}</span></div>'
        '</div>')


def trending(arts):
    cards = ""
    for i, fm in enumerate(arts[:5], 1):
        acc = " accent" if i == 1 else ""
        cards += (
            f'<a class="trend-card{acc}" href="news/{esc(fm["slug"])}.html">'
            f'<span class="rank">{i:02d}</span>'
            f'<span class="cat mono">{cat_of(fm)}</span>'
            f'<h3>{esc(fm["title"])}</h3>'
            f'<span class="tmeta mono">{esc(str(fm.get("date", "")))}</span></a>')
    return f'<div class="trending">{cards}</div>'


def reports(arts):
    rep = [fm for fm in arts if fm.get("type") in ("data-report", "data-note", "explainer")][:4]
    if len(rep) < 4:
        rep = (rep + [fm for fm in arts if fm not in rep])[:4]
    cards = ""
    for fm in rep:
        en, vn = TYPE_LABEL.get(fm.get("type"), ("Report", "Báo cáo"))
        cards += (
            f'<a class="report-card" href="news/{esc(fm["slug"])}.html">'
            f'<div class="rtag mono">{bilingual(en, vn)}</div>'
            f'<h3>{esc(fm["title"])}</h3>'
            f'<div class="rmeta mono"><span>{esc(str(fm.get("date", "")))}</span>'
            f'<span>{bilingual("Read", "Đọc")} →</span></div></a>')
    return f'<div class="reports">{cards}</div>'


def hotnews(arts):
    hot = sorted(arts, key=lambda fm: str(fm.get("date", "")), reverse=True)[:5]
    rows = ""
    for i, fm in enumerate(hot, 1):
        rows += (
            f'<a class="hot-row" href="news/{esc(fm["slug"])}.html">'
            f'<div class="hrank">{i:02d}</div>'
            f'<div class="htitle"><span class="hcat mono">{cat_of(fm)}</span>{esc(fm["title"])}</div>'
            f'<div class="hdate mono">{esc(str(fm.get("date", "")))}</div></a>')
    return f'<div class="hotnews">{rows}</div>'


CSS = """
  .wrap{max-width:var(--w-wide);margin:0 auto;padding:0 1.4rem}
  body{background:var(--bg)}
  /* topbar + ticker (thin, theme-token; <120px tall so THEME_PURITY-exempt, but kept light) */
  /* topbar = full-width bar (border edge-to-edge like .gbar); inner content aligned to the 1180 column */
  .topbar{background:var(--ink)}  /* dark LIVE strip (thin -> THEME_PURITY-exempt; tokens only) */
  .topbar-in{margin:0 auto;display:flex;align-items:center;gap:18px;
    padding:9px 1.8rem;font-family:var(--font-mono);font-size:11px;color:var(--bg)}
  .topbar .tag{color:var(--brass-bright);font-weight:600;display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
  .livedot{width:6px;height:6px;border-radius:50%;background:var(--brass);animation:hp-blink 1.6s ease-in-out infinite}
  .ticker-wrap{overflow:hidden;flex:1;white-space:nowrap}
  .ticker{display:inline-block;padding-left:100%;animation:hp-scroll 34s linear infinite}
  .ticker span{margin-right:46px;color:var(--bg);opacity:.72}
  .ticker span b{color:var(--brass-bright);opacity:1;font-weight:600}
  .tb-co{white-space:nowrap;color:var(--bg);opacity:.66}
  @keyframes hp-scroll{0%{transform:translateX(0)}100%{transform:translateX(-100%)}}
  @keyframes hp-blink{0%,100%{opacity:1}50%{opacity:.25}}
  /* masthead — VUIP lead, USR publisher; .hp-mast (NOT .masthead — avoids design-system card frame).
     FULL-WIDTH bar + full-width content (edge 1.8rem), matching the header. */
  .hp-mast{border-bottom:2px solid var(--ink)}
  .hp-mast-in{margin:0 auto;padding:26px 1.8rem 20px;
    display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap}
  .mh-sub{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--brass);font-weight:500;margin-bottom:8px}
  .hp-mast h1{font-family:var(--font-head);font-weight:600;font-size:clamp(30px,4.4vw,52px);line-height:1.0;letter-spacing:-.02em;margin:0;color:var(--ink)}
  .mh-right{display:flex;flex-direction:column;align-items:flex-end;justify-content:flex-end;gap:7px;text-align:right}
  .mh-coords{font-size:12px;color:var(--ink);letter-spacing:.04em;font-variant-numeric:tabular-nums}
  .mh-tag{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);max-width:34ch;line-height:1.5}
  /* hero 1+3 */
  .hero-grid{max-width:var(--w-wide);margin:0 auto;padding:0 1.4rem;display:grid;grid-template-columns:1.7fr 1fr;border-bottom:1px solid var(--hair)}
  .hero-main{padding:30px 30px 30px 0;border-right:1px solid var(--hair);text-decoration:none;color:inherit;display:block}
  .eyebrow{display:inline-flex;align-items:center;gap:8px;font-family:var(--font-mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--brass);font-weight:600;margin-bottom:13px}
  .eyebrow .dot{width:6px;height:6px;border-radius:50%;background:var(--brass);animation:hp-blink 1.6s ease-in-out infinite}
  .hero-main h2{font-family:var(--font-head);font-size:clamp(25px,3.3vw,40px);line-height:1.1;margin:0 0 15px;font-weight:600;color:var(--ink)}
  .hero-main:hover h2{color:var(--brass)}
  .hero-main p.dek{font-size:16.5px;line-height:1.6;color:var(--ink-soft);margin:0 0 16px;max-width:60ch}
  .hero-meta{font-size:11px;color:var(--muted);display:flex;gap:16px;flex-wrap:wrap;text-transform:uppercase;letter-spacing:.06em}
  .hero-side{padding:30px 0 30px 30px;display:flex;flex-direction:column;gap:20px}
  .side-story{padding-bottom:18px;border-bottom:1px solid var(--hair);text-decoration:none;color:inherit;display:block}
  .side-story:last-child{border-bottom:none;padding-bottom:0}
  .side-story .cat{font-size:10px;color:var(--brass);letter-spacing:.08em;font-weight:600;text-transform:uppercase}
  .side-story h3{font-family:var(--font-head);font-size:16.5px;margin:7px 0 0;line-height:1.3;font-weight:600;color:var(--ink)}
  .side-story:hover h3{color:var(--brass)}
  /* section label */
  .section-label{max-width:var(--w-wide);margin:0 auto;display:flex;align-items:baseline;gap:14px;padding:44px 1.4rem 20px}
  .section-label .code{font-family:var(--font-mono);font-size:12px;color:var(--brass);font-weight:700}
  .section-label h2{font-family:var(--font-head);font-size:23px;margin:0;font-weight:600;color:var(--ink)}
  .section-label .rule{flex:1;border-top:1px solid var(--hair)}
  /* compare */
  .compare-panel{max-width:var(--w-wide);margin:0 auto;padding:0 1.4rem}
  .compare-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;border:1px solid var(--hair);border-bottom:none;padding:16px 18px;background:var(--bg-2)}
  .ch-k{font-size:11px;color:var(--brass);font-weight:600;letter-spacing:.06em}
  .compare-head p{font-size:13px;color:var(--muted);margin:5px 0 0;max-width:560px}
  .compare-cta{font-family:var(--font-mono);font-size:12px;border:1px solid var(--ink);color:var(--ink);padding:9px 16px;white-space:nowrap;text-decoration:none}
  .compare-cta:hover{background:var(--brass);border-color:var(--brass);color:var(--bg)}
  .compare-table{width:100%;border-collapse:collapse}
  .compare-table th,.compare-table td{padding:13px 18px;border:1px solid var(--hair);text-align:left;font-size:13.5px;color:var(--ink)}
  .compare-table th{font-family:var(--font-mono);font-size:11px;color:var(--muted);letter-spacing:.04em;font-weight:600;background:var(--bg-2)}
  .compare-table th.drone-col{color:var(--ink);font-size:13.5px}
  .compare-table td.spec-label{font-family:var(--font-mono);font-size:11px;color:var(--muted)}
  .compare-table td.best{color:var(--brass);font-weight:600}
  .compare-table td.nullv{color:var(--faint);font-style:italic}
  .compare-foot{border:1px solid var(--hair);border-top:none;padding:14px 18px;font-size:11px;color:var(--muted)}
  /* trending (accent = brass, NOT inverted dark -> THEME_PURITY safe) */
  .trending{max-width:var(--w-wide);margin:0 auto;display:grid;grid-template-columns:repeat(5,1fr);border:1px solid var(--hair)}
  .trend-card{padding:20px 16px 22px;border-right:1px solid var(--hair);text-decoration:none;color:inherit;display:block}
  .trend-card:last-child{border-right:none}
  .trend-card:hover{background:var(--bg-2)}
  .trend-card.accent{background:var(--bg-2);box-shadow:inset 3px 0 0 var(--brass)}
  .trend-card .rank{font-family:var(--font-head);font-size:28px;font-weight:600;color:var(--hair-strong);display:block;margin-bottom:10px}
  .trend-card.accent .rank{color:var(--brass)}
  .trend-card .cat{font-size:10px;color:var(--brass);letter-spacing:.06em;font-weight:600;margin-bottom:8px;display:block;text-transform:uppercase}
  .trend-card h3{font-family:var(--font-head);font-size:15px;margin:0 0 10px;font-weight:600;line-height:1.3;color:var(--ink)}
  .trend-card:hover h3{color:var(--brass)}
  .trend-card .tmeta{font-size:10.5px;color:var(--muted)}
  /* INFO/02 signature (token paint; verify_graphics) */
  .sigwrap{max-width:var(--w-wide);margin:0 auto;padding:0 1.4rem}
  /* capability scatter — dots coloured via token classes; root svg fill=none (verify_svg safe) */
  .scat{display:grid;grid-template-columns:58px 1fr;gap:10px;align-items:stretch;margin-top:4px}
  .scat-yax{display:flex;flex-direction:column;justify-content:space-between;align-items:flex-end;
    font-family:var(--font-mono);font-size:10px;color:var(--muted);text-align:right}
  .scat-yax .scat-axt{writing-mode:vertical-rl;transform:rotate(180deg);color:var(--ink-soft);
    letter-spacing:.1em;text-transform:uppercase;font-size:9px;margin:auto -2px}
  .scat-svg{width:100%;height:auto;display:block;border-left:1px solid var(--hair-strong);border-bottom:1px solid var(--hair-strong)}
  .scat-grid{stroke:var(--hair);stroke-width:1;opacity:.55}
  .dot{opacity:.8}
  .dot.sc1{fill:var(--sc1)} .dot.sc2{fill:var(--sc2)} .dot.sc3{fill:var(--sc3)}
  .dot.sc4{fill:var(--sc4)} .dot.sc5{fill:var(--sc5)} .dot.sc6{fill:var(--sc6)}
  .scat-xax{display:flex;justify-content:space-between;align-items:center;margin:7px 0 0 68px;
    font-family:var(--font-mono);font-size:10px;color:var(--muted)}
  .scat-xax .scat-axt{color:var(--ink-soft);letter-spacing:.1em;text-transform:uppercase;font-size:9px}
  .scat-legend{display:flex;flex-wrap:wrap;gap:7px 16px;margin:14px 0 0 68px;
    font-family:var(--font-mono);font-size:11px;color:var(--ink-soft)}
  .scat-legend .scl{display:inline-flex;align-items:center;gap:6px}
  .sw{width:9px;height:9px;border-radius:50%;display:inline-block;flex:0 0 9px}
  .sw.sc1{background:var(--sc1)} .sw.sc2{background:var(--sc2)} .sw.sc3{background:var(--sc3)}
  .sw.sc4{background:var(--sc4)} .sw.sc5{background:var(--sc5)} .sw.sc6{background:var(--sc6)}
  .sig-cap{font-size:12px;color:var(--muted);max-width:64ch;margin:14px 0 0 68px;line-height:1.55}
  /* reports */
  .reports{max-width:var(--w-wide);margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--hair);border:1px solid var(--hair)}
  .report-card{background:var(--bg);padding:20px 18px;min-height:158px;display:flex;flex-direction:column;justify-content:space-between;text-decoration:none;color:inherit}
  .report-card:hover{background:var(--bg-2)}
  .report-card .rtag{color:var(--brass);font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase}
  .report-card h3{font-family:var(--font-head);font-size:15px;font-weight:600;margin:10px 0;line-height:1.34;color:var(--ink)}
  .report-card:hover h3{color:var(--brass)}
  .report-card .rmeta{font-size:10.5px;color:var(--muted);display:flex;justify-content:space-between}
  /* hotnews */
  .hotnews{max-width:var(--w-wide);margin:0 auto;border:1px solid var(--hair);border-top:none}
  .hot-row{display:grid;grid-template-columns:58px 1fr 92px;border-top:1px solid var(--hair);align-items:center;text-decoration:none;color:inherit}
  .hot-row:hover{background:var(--bg-2)}
  .hot-row>div{padding:14px 18px}
  .hot-row .hrank{font-family:var(--font-head);font-size:17px;font-weight:600;color:var(--brass);border-right:1px solid var(--hair)}
  .hot-row .htitle{border-right:1px solid var(--hair);font-size:14px;color:var(--ink)}
  .hot-row:hover .htitle{color:var(--brass)}
  .hot-row .htitle .hcat{display:block;font-size:10px;color:var(--brass);margin-bottom:3px;text-transform:uppercase;letter-spacing:.06em}
  .hot-row .hdate{font-size:11px;color:var(--muted);text-align:right}
  .block-gap{height:54px}
  @media (max-width:900px){
    .hero-grid{grid-template-columns:1fr}
    .hero-main{border-right:none;border-bottom:1px solid var(--hair);padding:24px 0}
    .hero-side{padding:24px 0}
    .trending{grid-template-columns:repeat(2,1fr)}
    .reports{grid-template-columns:repeat(2,1fr)}
    .mh-right{gap:18px}
  }
  @media (prefers-reduced-motion: reduce){
    .ticker{animation:none;padding-left:0}
    .livedot,.eyebrow .dot{animation:none}
  }
"""


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    f = live_facts(site)
    arts = [fm for fm, _ in sorted(load_articles(), key=_weight, reverse=True)]
    n, countries, coverage = f["entities"], f["countries"], f["coverage"]

    doc = f"""<!DOCTYPE html>
<html lang="vi" data-theme="light" data-lang="vn">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vietnam UAV Intelligence Platform — Uncrewed Systems Review</title>
{seo_meta("Vietnam UAV Intelligence Platform", "Entity-centric UAV intelligence: " + str(n) + " systems with cited sources, tiers and honest-null. Published by Uncrewed Systems Review.", "index.html")}
{website_ld()}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{CSS}</style>
</head>
<body>

{ticker(f, arts)}
{masthead(f)}
{header("", "home")}

{hero(arts)}

{section_label("TOOL/00", "Drone compare", "Công cụ so sánh drone")}
{compare_preview(ents, labels)}

{section_label("TREND/01", "Notable", "Đáng chú ý")}
{trending(arts)}

{section_label("INFO/02", "Infographics", "Đồ hoạ dữ liệu")}
{scatter_svg(site)}

{section_label("REPORT/03", "Reports & data", "Báo cáo & dữ liệu")}
{reports(arts)}

{section_label("HOT/04", "Hot news", "Tin nóng")}
{hotnews(arts)}

<div class="block-gap"></div>
{footer("")}
<script src="base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.initReveal();
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""
    OUT.write_text(doc)
    print(f"index.html | VUIP layout | {n} systems · {countries} countries · {coverage}% coverage · "
          f"{len(arts)} articles bound")


if __name__ == "__main__":
    main()
