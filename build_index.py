#!/usr/bin/env python3
"""TIP-004 (rev) — Editorial home in the APPROVED idiom (portal-in-action.html is the
design-system-of-record). NOT a layered dashboard, NOT a hero laminated onto one.

Sequence, all in the approved idiom:
  bar -> hero .field (CTA -> reference.html) -> field-file cards fed by REAL entities
  (01/02/03, "Read the file" -> entity/<slug>.html) -> record-status masthead (re-idiom,
  solid-serif .statfig, NOT the dark-card ghost) -> "Browse all N" CTA.

Every figure is LIVE from site-data (CONSTRAINT 8). The blueprint is a geometric signature
illustration — it carries NO entity-specific claim (zero fabrication). Real, sourced data lives
in the card body and links to the entity's citable detail page. Bilingual, light/dark.
"""
import json, pathlib
from build_reference import bilingual, esc, friendly, maker_model
from footer import footer
from glyphs import glyph_svg
from nav import nav
from header import header
from seo import meta as seo_meta
from build_newsroom import load_articles, TYPE_LABEL, homepage_news_block, _weight, _kicker, _meta
from build_monitor import monitor_teaser
from graphic import feed_figure
from build_registry_cards import qualify as rc_qualify, _card as rc_card, DESK as RC_DESK, DESK_ORDER as RC_DESK_ORDER

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
OUT = ROOT / "index.html"

ARROW = ('<svg class="ar" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
         '<path d="M4.5 12H16.5M11 6.5L16.5 12L11 17.5" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

WATERMARK = ('<svg viewBox="0 0 760 400"><g class="wm-stroke">'
             '<circle cx="170" cy="110" r="92"/><circle cx="590" cy="110" r="92"/>'
             '<circle cx="170" cy="300" r="92"/><circle cx="590" cy="300" r="92"/>'
             '<rect x="320" y="160" width="120" height="90" rx="20"/>'
             '<line x1="248" y1="170" x2="332" y2="196"/><line x1="512" y1="170" x2="428" y2="196"/>'
             '<line x1="248" y1="240" x2="332" y2="214"/><line x1="512" y1="240" x2="428" y2="214"/>'
             '<circle cx="380" cy="205" r="30"/><circle cx="380" cy="205" r="13"/>'
             '<line x1="78" y1="205" x2="682" y2="205"/><line x1="380" y1="10" x2="380" y2="395"/>'
             '</g></svg>')


# TIP-UX2.1 hero blueprint — ported verbatim from home-v2-specimen.html (design-source).
# GENERIC multirotor schematic (zero entity claim, "NOT TO SCALE"). root fill="none" + class line-art
# (.l/.lf/.a/.af/.grid) flips ink<->brass by theme; leader labels sit in clear space (no overlap).
HERO_BP = '''<svg viewBox="0 0 660 580" width="100%" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bản vẽ kỹ thuật hệ thống multirotor">
<defs>
<pattern id="bpgrid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" class="grid"/></pattern>
<marker id="ar" markerWidth="10" markerHeight="10" refX="7" refY="5" orient="auto"><path d="M0 1.5 L7.5 5 L0 8.5 Z" fill="var(--bp-line)"/></marker>
<marker id="ar2" markerWidth="9" markerHeight="9" refX="6" refY="4.5" orient="auto"><path d="M0 1.2 L6.5 4.5 L0 7.8 Z" fill="var(--brass)"/></marker>
</defs>
<rect x="20" y="20" width="620" height="540" fill="url(#bpgrid)"/>
<rect x="20" y="20" width="620" height="540" class="lf"/>
<path d="M20 56V20H56 M604 20H640V56 M640 524V560H604 M56 560H20V524" class="a" stroke-width="1.4"/>
<g class="l"><line x1="290" y1="252" x2="168" y2="170"/><line x1="370" y1="252" x2="492" y2="170"/><line x1="290" y1="328" x2="168" y2="410"/><line x1="370" y1="328" x2="492" y2="410"/></g>
<rect x="278" y="246" width="104" height="88" rx="13" class="l"/>
<path d="M330 262V318 M302 290H358" class="lf"/>
<circle cx="330" cy="290" r="13" class="a"/><circle cx="330" cy="290" r="3" class="af"/>
<rect x="318" y="232" width="24" height="12" rx="3" class="l"/>
<circle cx="330" cy="346" r="9" class="l"/><circle cx="330" cy="346" r="3.5" class="lf"/>
<g transform="translate(168 170)"><circle r="58" class="lf" stroke-dasharray="1 6"/><circle r="50" class="l"/><circle r="38" class="lf"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(20)"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(200)"/><circle r="11" class="l"/><circle r="6" class="a"/><circle r="2.3" fill="var(--brass)"/><path d="M0 -50 A50 50 0 0 1 34 -36" class="a" marker-end="url(#ar2)"/></g>
<g transform="translate(492 170)"><circle r="58" class="lf" stroke-dasharray="1 6"/><circle r="50" class="l"/><circle r="38" class="lf"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(20)"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(200)"/><circle r="11" class="l"/><circle r="6" class="a"/><circle r="2.3" fill="var(--brass)"/><path d="M0 -50 A50 50 0 0 1 34 -36" class="a" marker-end="url(#ar2)"/></g>
<g transform="translate(168 410)"><circle r="58" class="lf" stroke-dasharray="1 6"/><circle r="50" class="l"/><circle r="38" class="lf"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(20)"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(200)"/><circle r="11" class="l"/><circle r="6" class="a"/><circle r="2.3" fill="var(--brass)"/><path d="M0 -50 A50 50 0 0 1 34 -36" class="a" marker-end="url(#ar2)"/></g>
<g transform="translate(492 410)"><circle r="58" class="lf" stroke-dasharray="1 6"/><circle r="50" class="l"/><circle r="38" class="lf"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(20)"/><path d="M11 -2 Q30 -8 46 -2 Q30 3 11 2 Z" class="l" transform="rotate(200)"/><circle r="11" class="l"/><circle r="6" class="a"/><circle r="2.3" fill="var(--brass)"/><path d="M0 -50 A50 50 0 0 1 34 -36" class="a" marker-end="url(#ar2)"/></g>
<g><line x1="106" y1="170" x2="106" y2="92" class="lf"/><line x1="554" y1="170" x2="554" y2="92" class="lf"/><line x1="106" y1="100" x2="554" y2="100" class="l" marker-start="url(#ar)" marker-end="url(#ar)"/><rect x="305" y="90" width="50" height="20" fill="var(--bg)"/><text x="330" y="104" text-anchor="middle" class="acc">SPAN</text></g>
<g><line x1="168" y1="232" x2="90" y2="232" class="lf"/><line x1="168" y1="472" x2="90" y2="472" class="lf"/><line x1="98" y1="232" x2="98" y2="472" class="l" marker-start="url(#ar)" marker-end="url(#ar)"/><rect x="84" y="342" width="28" height="20" fill="var(--bg)"/><text x="98" y="356" text-anchor="middle" class="acc" transform="rotate(-90 98 352)">DEPTH</text></g>
<g><path d="M330 232 V162" class="a"/><circle cx="330" cy="232" r="2.4" fill="var(--brass)"/><text x="330" y="154" text-anchor="middle" class="big">GNSS · COMPASS</text><path d="M330 356 V392" class="a"/><circle cx="330" cy="356" r="2.4" fill="var(--brass)"/><text x="330" y="406" text-anchor="middle" class="big">PAYLOAD BAY</text><path d="M382 290 H548" class="a"/><circle cx="382" cy="290" r="2.4" fill="var(--brass)"/><text x="556" y="293" class="big">FLIGHT CTRL</text><path d="M534 150 L556 130" class="a"/><circle cx="534" cy="150" r="2.4" fill="var(--brass)"/><text x="560" y="127" class="big">ROTOR · Ø</text></g>
<line x1="20" y1="512" x2="640" y2="512" class="lf"/>
<text x="32" y="536" class="acc">USR · FIELD SCHEMATIC</text>
<text x="32" y="550">GENERIC MULTIROTOR · NOT TO SCALE</text>
<g transform="translate(600 538)"><circle r="15" class="l"/><path d="M0 -15V15 M-15 0H15" class="lf"/><path d="M0 -15L4 -7H-4Z" class="af"/><text x="0" y="-19" text-anchor="middle" class="acc">N</text></g>
<text x="540" y="536" text-anchor="end">REV 02</text>
</svg>'''


def live_facts(site):
    """Real, live figures computed from site-data — never hardcoded (CONSTRAINT 8)."""
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]  # schema/2: UAV surface only
    agg = site["aggregates"]
    def count(pred): return sum(1 for e in ents if pred(e))
    def tally(getter):
        d = {}
        for e in ents:
            v = getter(e)
            if v:
                d[v] = d.get(v, 0) + 1
        return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))
    blue = count(lambda e: e["blue_uas"].get("status") == "verified" and e["blue_uas"].get("value") is True)
    ndaa = count(lambda e: e["ndaa_compliant"].get("status") == "verified" and e["ndaa_compliant"].get("value") is True)
    disputed = agg["field_status_counts"].get("disputed", 0)
    seg_rank = tally(lambda e: e["market_segment"].get("value"))
    country_rank = tally(lambda e: e["manufacturer_country"].get("value"))
    fill = agg["spec_fill_rate"]
    present = sum(d["present"] for d in fill.values())
    total = sum(d["total"] for d in fill.values())
    coverage = round(100 * present / total) if total else 0
    return {"entities": len(ents), "blue_verified": blue, "ndaa_verified": ndaa,
            "disputed_live": disputed, "segments": len(seg_rank),
            "seg_rank": seg_rank, "country_rank": country_rank, "coverage": coverage}


# ---- record-status masthead (re-idiom: solid-serif .statfig, hairline, brass one-beat) ----
def stat_cell(value, cap_en, cap_vn):
    # data-countup: animates 0 -> real value on load (reduced-motion safe; final value baked in DOM).
    # ch min-width = final length keeps the box stable so the count never reflows into an overlap.
    s = str(value)
    return (f'<div class="stat-cell"><span class="statfig" data-countup '
            f'style="min-width:{len(s)}ch">{esc(s)}</span>'
            f'<span class="cap mono">{bilingual(cap_en, cap_vn)}</span></div>')


def stat_ribbon(f, labels):
    """Live authority ribbon for the hero — every figure from live_facts (zero-fab). countries =
    distinct manufacturer_country values; coverage = live spec fill-rate. Brass pulse on 'live'."""
    countries = len(f["country_rank"])
    def cell(value, en, vn):
        s = str(value)
        return (f'<span class="sr-cell"><b class="sr-n" data-countup style="min-width:{len(s)}ch">{esc(s)}</b>'
                f'<span class="sr-k mono">{bilingual(en, vn)}</span></span>')
    return ('<div class="statribbon" data-audit="ribbon">'
            + cell(countries, "countries", "quốc gia")
            + cell(f'{f["coverage"]}%', "coverage", "độ phủ")
            + f'<span class="sr-cell sr-live"><span class="live-dot"></span>'
            f'<span class="sr-k mono">{bilingual("live", "trực tiếp")}</span></span>'
            + '</div>')


def real_newsroom_block(prefix="."):
    """Home Newsroom — the REAL, published factual articles (content/newsroom), newest-first. Never
    the sample drafts in articles.json and never an opinion without a human author: the public home
    shows only published, AI-authorable factual pieces. Each links to its /news/<slug> page."""
    cards = ""
    for fm, _ in load_articles():
        kl_en, kl_vn = TYPE_LABEL.get(fm["type"], (fm["type"], fm["type"]))
        cards += (f'<a class="nr-card reveal" href="{prefix}/news/{esc(fm["slug"])}.html">'
                  f'<span class="nr-kind">{bilingual(kl_en, kl_vn)}</span>'
                  f'<span class="nr-t">{esc(fm["title"])}</span>'
                  f'<span class="nr-go">{bilingual("Read", "Đọc")}{ARROW}</span></a>')
    return f'<div class="nr-grid2">{cards}</div>'


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


# ---- field-file cards (the hero of the data: real entities in the blueprint-card idiom) ----
def blueprint_svg(callouts=False, labels=None):
    """Geometric signature illustration — the approved technical-drawing idiom (portal-in-action).
    Anatomy is decorative (zero entity claim). With callouts=True it adds the dimension arrows +
    leader-line labels (bilingual, generic category terms — not entity data) for the hero centrepiece.
    The labels describe the SCHEMATIC's anatomy, never a specific aircraft, so zero-fabrication holds."""
    L = labels or (lambda en, vn: en)
    base = (
        '<circle class="bp-disc" cx="230" cy="118" r="70" data-draw></circle>'
        '<circle class="bp-disc" cx="530" cy="118" r="70" data-draw></circle>'
        '<circle class="bp-disc" cx="230" cy="300" r="70" data-draw></circle>'
        '<circle class="bp-disc" cx="530" cy="300" r="70" data-draw></circle>'
        '<g class="bp-blade">'
        '<line x1="174" y1="118" x2="286" y2="118"></line><line x1="474" y1="118" x2="586" y2="118"></line>'
        '<line x1="174" y1="300" x2="286" y2="300"></line><line x1="474" y1="300" x2="586" y2="300"></line></g>'
        '<path class="bp-arm" d="M300 168 L230 118" data-draw></path>'
        '<path class="bp-arm" d="M460 168 L530 118" data-draw></path>'
        '<path class="bp-arm" d="M300 250 L230 300" data-draw></path>'
        '<path class="bp-arm" d="M460 250 L530 300" data-draw></path>'
        '<circle class="bp-part" cx="230" cy="118" r="13"></circle><circle class="bp-part" cx="530" cy="118" r="13"></circle>'
        '<circle class="bp-part" cx="230" cy="300" r="13"></circle><circle class="bp-part" cx="530" cy="300" r="13"></circle>'
        '<rect class="bp-body" x="315" y="166" width="130" height="86" rx="20" data-draw></rect>'
        '<line class="bp-mark" x1="372" y1="209" x2="388" y2="209"></line>'
        '<line class="bp-mark" x1="380" y1="201" x2="380" y2="217"></line>'
        '<circle class="bp-part" cx="380" cy="150" r="8"></circle>'
        '<circle class="bp-part" cx="380" cy="284" r="22"></circle>'
        '<circle class="bp-part" cx="380" cy="284" r="10"></circle>')
    if not callouts:
        return f'<div class="bp-stage"><svg viewBox="0 0 760 392" fill="none" aria-hidden="true">{base}</svg></div>'
    call = (
        '<g class="bp-fade">'
        '<line class="bp-lead" x1="380" y1="142" x2="380" y2="54"></line>'
        f'<text class="bp-callk" x="380" y="44" text-anchor="middle">{L("GNSS / RTK", "GNSS / RTK")}</text>'
        '<line class="bp-lead" x1="380" y1="306" x2="380" y2="324"></line>'
        f'<text class="bp-call" x="380" y="338" text-anchor="middle">{L("EO / IR gimbal", "Cảm biến EO / IR")}</text>'
        '<line class="bp-lead" x1="445" y1="200" x2="600" y2="200"></line>'
        f'<text class="bp-call" x="610" y="204" text-anchor="start">{L("Encrypted datalink", "Datalink mã hoá")}</text>'
        '<line class="bp-lead" x1="315" y1="200" x2="160" y2="200"></line>'
        f'<text class="bp-callk" x="150" y="204" text-anchor="end">{L("Provenance-traced", "Truy nguồn")}</text>'
        '</g>'
        '<g class="bp-fade">'
        '<line class="bp-dim" x1="160" y1="384" x2="600" y2="384"></line>'
        '<path class="bp-dim" d="M160 384 l9 -4 v8 z"></path><path class="bp-dim" d="M600 384 l-9 -4 v8 z"></path>'
        f'<text class="bp-dlabel" x="380" y="380" text-anchor="middle">{L("airframe schematic", "sơ đồ khung bay")}</text>'
        '</g>')
    return f'<div class="bp-stage bp-stage--hero"><svg viewBox="-40 0 840 400" fill="none" aria-hidden="true">{base}{call}</svg></div>'


def evidence_tier(e, groups):
    """Best citable tier present on the entity (A>B>C), or '—'. From real source tiers only."""
    abc = [e[fld].get("source_tier") for fld in groups]
    abc = [t for t in abc if t in ("A", "B", "C")]
    return min(abc) if abc else "—"


def field_file_card(e, n, labels, groups, big):
    maker, model = maker_model(e)
    country = e["manufacturer_country"].get("value") or "—"
    seg_v = e["market_segment"].get("value")
    seg = friendly("segment", seg_v, labels)
    sl = labels["segment"].get(seg_v) if seg_v else None
    seg_en = sl["en"] if sl else "Uncrewed"
    seg_vn = sl["vn"] if sl else "Không người lái"
    n_ver = sum(1 for fld in groups if e[fld].get("status") == "verified")
    tier = evidence_tier(e, groups)
    desc_en = f"{seg_en} system, {country}. {n_ver} fields verified to source."
    desc_vn = f"Hệ {seg_vn.lower()}, {country}. {n_ver} field đã kiểm tới nguồn."
    return (
        f'<article class="card reveal" data-audit="ffcard">'
        f'<span class="reg tl"></span><span class="reg tr"></span>'
        f'<span class="reg bl"></span><span class="reg br"></span>'
        + (blueprint_svg() if big else "")
        + f'<div class="card-body">'
          f'<span class="ghost">{n:02d}</span>'
          f'<div class="keb">{seg}</div>'
          f'<div class="ff-cfg">{glyph_svg(e.get("frame_glyph", "unknown"), "glyph-sm")}'
          f'<span>{bilingual("config", "cấu hình")} · {esc(e["airframe_type"].get("value") or "—")}</span></div>'
          f'<h3 data-audit="ff-title">{esc(maker)} <span class="ffmodel">{esc(model)}</span></h3>'
          f'<p>{bilingual(desc_en, desc_vn)}</p>'
          f'<div class="foot">'
          f'<span class="meta">{bilingual("Evidence", "Bằng chứng")} · <b>{esc(tier)}</b></span>'
          f'<a class="readmore" href="entity/{esc(e["slug"])}.html" data-audit="ff-read">'
          f'{bilingual("Read the file", "Đọc hồ sơ")}<span class="ico">{ARROW}</span></a>'
          f'</div></div></article>')


def featured_systems(ents, groups, labels):
    """02 · Browse — a real preview of the registry: the best-documented, diverse systems (one per
    family) as compact cards linking into their detail file. Concrete devices (not aggregates), so it
    differs from the record-status masthead and makes the 'browse' promise tangible."""
    cards = ""
    for e in pick_featured(ents, groups, 6):
        maker, model = maker_model(e)
        seg_v = e["market_segment"].get("value")
        seg = friendly("segment", seg_v, labels) if seg_v else bilingual("Uncrewed", "Không người lái")
        country = e["manufacturer_country"].get("value") or "—"
        tier = evidence_tier(e, groups)
        badge = ""
        if (e.get("blue_uas") or {}).get("value") is True:
            badge = '<span class="fsys-b">Blue UAS</span>'
        elif (e.get("ndaa_compliant") or {}).get("value") is True:
            badge = '<span class="fsys-b">NDAA</span>'
        cards += (
            f'<a class="fsys reveal" href="entity/{esc(e["slug"])}.html" data-audit="fsys">'
            f'<div class="fsys-top"><span class="fsys-g">{glyph_svg(e.get("frame_glyph", "unknown"), "glyph-sm")}</span>'
            f'<span class="fsys-kb">{seg}</span></div>'
            f'<b class="fsys-nm"><span class="fsys-mk">{esc(maker)}</span>{esc(model)}</b>'
            f'<div class="fsys-ft"><span class="fsys-mt">{esc(country)} · {bilingual("Evidence", "Bằng chứng")} <b class="fsys-tier">{esc(tier)}</b></span>'
            f'{badge}<span class="fsys-go">{ARROW}</span></div></a>')
    return f'<div class="fsys-grid">{cards}</div>'


def coverage_matrix(site):
    """Real per-cell coverage (11 specs × N entities). Filled = field has a value; sparse is shown,
    not hidden — rigor as evidence. % per row is the live aggregate (== auditor coverage)."""
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]  # schema/2: UAV surface only
    spec = site["field_groups"]["spec"]
    total = len(ents)
    rows = ""
    for fkey in spec:
        cells = "".join('<i class="on"></i>' if e[fkey].get("value") is not None else '<i></i>' for e in ents)
        present = sum(1 for e in ents if e[fkey].get("value") is not None)
        lab = site["labels"]["field"].get(fkey, {"en": fkey, "vn": fkey})
        rows += (f'<div class="cov-row"><span class="cl">{bilingual(lab["en"], lab["vn"])}</span>'
                 f'<span class="cov-cells">{cells}</span>'
                 f'<span class="cn">{round(100*present/total)}% · {present}/{total}</span></div>')
    return f'<div class="cov" data-audit="cov">{rows}</div>'


def pick_featured(ents, groups, k=3):
    """Deterministic: best-documented entities (most populated fields), tie-break canonical_id.
    At most one per family_id so the showcase is diverse (not two sibling variants)."""
    def score(e): return sum(1 for fld in groups if e[fld].get("value") is not None)
    ordered = sorted(ents, key=lambda e: (-score(e), e["canonical_id"]))
    seen, out = set(), []
    for e in ordered:
        fam = e.get("family_id")
        if fam in seen:
            continue
        seen.add(fam); out.append(e)
        if len(out) == k:
            break
    return out


def frontpage_desks():
    """TIP-FP2 tier T2 — registry desks. D event-cards grouped by desk, DEDUPED against the E articles
    via the explicit sidecar map (an entity with an E article is shown as E, its D-card hidden), and
    DESK_HONEST: a desk with >=N cards renders a strip; a thin desk collapses to an honest 'building'
    line (never a padded empty block); an empty desk is skipped."""
    N = 4
    reg = json.loads((ROOT / "content" / "lae-registry.json").read_bytes())["entities"]
    artmap = json.loads((ROOT / "content" / "article_entity_map.json").read_bytes())["map"]
    articled = {v for v in artmap.values() if v}
    shown = [e for e in reg if rc_qualify(e) == "event" and e["entity"] not in articled]
    by = {}
    for e in shown:
        by.setdefault(RC_DESK.get(e["entity_type"], (None, "—"))[1], []).append(e)
    out = ""
    for d in RC_DESK_ORDER:
        cs = sorted(by.get(d, []), key=lambda e: (e.get("stratum") or "", e["entity"]))
        if not cs:
            continue
        if len(cs) >= N:
            cards = "".join(rc_card(e) for e in cs[:6])
            out += (f'<section class="fp-desk" data-mode="strip" data-n="{len(cs)}">'
                    f'<div class="rdesk-h"><h2>{esc(d)}</h2><span class="rdesk-n">{len(cs)}</span></div>'
                    f'<div class="rgrid">{cards}</div></section>')
        else:
            out += (f'<a class="fp-deskline" data-mode="line" data-n="{len(cs)}" href="registry.html">'
                    f'<span class="fp-dl-d">{esc(d)}</span>'
                    f'<span class="fp-dl-n">{len(cs)} {bilingual("record", "hồ sơ")}</span>'
                    f'<span class="fp-dl-tag">{bilingual("building", "đang xây")}</span>'
                    f'<span class="ico">{ARROW}</span></a>')
    return out


def live_hero(site, f, labels):
    """TIP-HERO-LIVE — a live featured rotator that replaces the static hero. Slide 0 keeps the
    positioning manifesto (statement + brand blueprint); slides 1..N are the strongest featured
    articles, each carrying source+tier and a figure GENERATED FROM DATA (feed_figure honest-null,
    never a borrowed image). Inactive slides are display:none at REST (overlap-safe); the brand row +
    live stats + footer are the fixed anchors. Auto-rotates (pause on hover, dots, reduced-motion off)."""
    ranked = sorted(load_articles(), key=_weight, reverse=True)
    feats = [fm for fm, _ in ranked[:4]]
    n, countries, coverage = f["entities"], len(f["country_rank"]), f["coverage"]
    slides = [
        '<article class="lhero-slide active show" data-i="0">'
        '<div class="lhero-text">'
        f'<div class="s-kicker">{bilingual("Field Intelligence", "Trên thực địa")}</div>'
        f'<h1 class="s-title lead-h">{bilingual("Uncrewed systems, seen clearly.", "Hệ thống không người lái, nhìn cho rõ.")}</h1>'
        f'<p class="s-dek">{bilingual("How verified data changes a real decision — explained plainly, for the people who have to make the call.", "Dữ liệu kiểm chứng thay đổi một quyết định thật ra sao, giải thích rõ ràng cho người phải ra quyết định.")}</p>'
        f'<a class="s-cta" href="reference.html">{bilingual("All field files", "Tất cả hồ sơ")} →</a>'
        '</div>'
        f'<div class="lhero-fig"><div class="lhero-plate">{blueprint_svg()}'
        f'<span class="plate-lbl">{bilingual("USR · field schematic", "USR · sơ đồ trường")}</span></div></div>'
        '</article>']
    for k, fm in enumerate(feats, 1):
        dek = f'<p class="s-dek">{esc(fm.get("dek"))}</p>' if fm.get("dek") else ""
        slides.append(
            f'<article class="lhero-slide" data-i="{k}">'
            '<div class="lhero-text">'
            f'<div class="s-kicker">{_kicker(fm)}</div>'
            f'<h1 class="s-title"><a href="news/{esc(fm["slug"])}.html">{esc(fm["title"])}</a></h1>'
            f'{dek}<div class="s-meta">{_meta(fm)}</div>'
            '</div>'
            f'<div class="lhero-fig"><div class="lhero-plate">{feed_figure(fm, "lead")}'
            f'<span class="plate-lbl">{bilingual("USR · generated from data", "USR · sinh từ dữ liệu")}</span></div></div>'
            '</article>')
    dots = "".join(f'<button class="lhero-dot{" on" if k == 0 else ""}" data-dot="{k}" '
                   f'type="button" aria-label="Slide {k+1}"></button>' for k in range(len(slides)))
    stats = (
        '<div class="lhero-stats">'
        f'<div class="lhero-stat"><div class="n" data-countup style="min-width:{len(str(n))}ch">{n}</div>'
        f'<div class="l">{bilingual("Verified systems", "Hệ thống đã kiểm")}</div></div>'
        f'<div class="lhero-stat"><div class="n" data-countup style="min-width:{len(str(countries))}ch">{countries}</div>'
        f'<div class="l">{bilingual("Countries", "Quốc gia")}</div></div>'
        f'<div class="lhero-stat"><div class="n">{coverage}%</div>'
        f'<div class="l">{bilingual("Spec coverage", "Độ phủ spec")}</div></div>'
        '</div>')
    return (
        '<section class="lhero" data-audit="hero" id="lhero">'
        '<div class="lhero-brand">'
        f'<div class="lhero-bk"><span class="bar"></span>{bilingual("Field Intelligence · Featured", "Trên thực địa · Nổi bật")}</div>'
        '<div class="lhero-auto">'
        f'<span class="lhero-autolbl"><span class="pulse">●</span> {bilingual("Auto · hover to pause", "Tự cuộn · rê để dừng")}</span>'
        f'<div class="lhero-dots">{dots}</div></div></div>'
        f'<div class="lhero-stage">{"".join(slides)}</div>'
        f'<div class="lhero-bot">{stats}'
        f'<a class="lhero-foot" href="reference.html">{bilingual("All records", "Toàn bộ hồ sơ")} <span class="arr">{ARROW}</span></a>'
        '</div></section>')


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]  # schema/2: UAV surface only
    groups = site["field_groups"]["display"] + site["field_groups"]["spec"]
    f = live_facts(site)
    n = f["entities"]
    countries = len(f["country_rank"])               # distinct manufacturer_country (live)
    coverage = f["coverage"]                          # live spec fill-rate %
    hero_blueprint = HERO_BP                           # specimen ink/brass schematic (TIP-UX2.1)
    feat = pick_featured(ents, groups, 1)[0]                          # one REAL record anchors the hero
    feat_mk, feat_md = maker_model(feat)
    hero_caption = (f'<a class="readmore hero-cap" href="entity/{esc(feat["slug"])}.html" data-audit="herofile">'
                    f'<b>{bilingual("Featured field file", "Hồ sơ tiêu biểu")}</b> · {esc(feat_mk)} {esc(feat_md)} →</a>')
    # live hero stats (heatm) — every figure from live_facts; matches verify_home figure-drift gate
    heatm = (
        '<div class="heatm">'
        f'<div class="s"><b class="v" data-countup style="min-width:{len(str(n))}ch">{n}</b>'
        f'<span class="k">{bilingual("Verified systems", "Hệ thống đã kiểm")}</span></div>'
        f'<div class="s"><b class="v" data-countup style="min-width:{len(str(countries))}ch">{countries}</b>'
        f'<span class="k">{bilingual("Countries", "Quốc gia")}</span></div>'
        f'<div class="s"><b class="v">{coverage}%</b>'
        f'<span class="k">{bilingual("Spec coverage", "Độ phủ spec")}</span></div>'
        '</div>')
    newsroom_block = homepage_news_block("")         # compact editorial frame (TIP-NEWSROOM.1), not card-grid
    live_hero_html = live_hero(site, f, labels)       # TIP-HERO-LIVE — live featured rotator
    desks_html = frontpage_desks()                     # TIP-FP2 T2 — registry desks (deduped, honest)
    masthead = render_masthead(f, labels)
    featured_html = featured_systems(ents, groups, labels)   # 02 · Browse — real systems preview

    doc = f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Uncrewed Systems Review</title>
{seo_meta("Uncrewed Systems Review", "Entity-centric UAV intelligence: 302 systems with cited sources, tiers and honest-null.", "index.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<link rel="stylesheet" href="base/newsroom.css">
<style>
  /* home layout in the approved idiom (components reuse the shared design system) */
  .wrap{{max-width:var(--w-wide);margin:0 auto;padding:0 1.4rem}}
  .bar{{border-bottom:1px solid var(--hair)}}
  .bar .wrap{{display:flex;align-items:center;height:64px;gap:20px}}
  .wm-name{{font-family:var(--font-head);font-weight:600;font-size:18px;letter-spacing:-.01em}}
  .wm-name small{{display:block;font-family:var(--font-mono);font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;margin-top:2px;font-weight:400}}
  .ctl{{margin-left:auto;display:flex;gap:8px}}
  :root[data-lang="en"] .tg .s-en{{opacity:1;color:var(--brass)}}
  :root[data-lang="vn"] .tg .s-vn{{opacity:1;color:var(--brass)}}
  /* faint blueprint grid (graph-paper) behind cream sections — premium hi-tech texture */
  body{{background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:30px 30px;background-position:center top}}
  .sec.plate{{background-image:none}}
  /* HERO — pure-value two-column: text+stats left · ink/brass blueprint right (TIP-UX2.1 specimen) */
  .field.hero-pure{{position:relative;overflow:hidden}}
  .field.hero-pure .wrap.hero-grid{{display:grid;grid-template-columns:.92fr 1.08fr;gap:54px;align-items:center;padding:58px 1.4rem 56px}}
  @media (max-width:940px){{.field.hero-pure .wrap.hero-grid{{grid-template-columns:1fr;gap:34px;padding:40px 1.4rem}}}}
  .hero-col-l{{max-width:52ch}}
  .eyebrow{{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--brass);font-weight:500;display:inline-flex;align-items:center;gap:10px}}
  .eyebrow::before{{content:"";width:22px;height:1px;background:var(--brass-bright)}}
  .lead-h{{font-family:var(--font-head);font-weight:600;font-size:clamp(40px,5.6vw,68px);line-height:1.0;letter-spacing:-.022em;margin:20px 0 0;color:var(--ink)}}
  .lead-p{{font-size:16px;color:var(--muted);max-width:46ch;margin-top:20px;line-height:1.62}}
  /* live hero stats — verified count + countries + coverage (zero-fab, count-up) */
  .heatm{{display:flex;gap:34px;margin-top:34px;padding-top:26px;border-top:1px solid var(--hair);flex-wrap:wrap}}
  .heatm .s .v{{font-family:var(--font-head);font-weight:600;font-size:34px;line-height:1;letter-spacing:-.02em;color:var(--ink);font-variant-numeric:tabular-nums;display:inline-block}}
  .heatm .s .k{{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-top:8px;display:block}}
  .cta{{margin-top:32px;display:inline-flex;align-items:center;gap:13px;font-family:var(--font-mono);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink);font-weight:500}}
  .cta .arw{{width:38px;height:38px;border:1.5px solid var(--brass);border-radius:50%;display:grid;place-items:center;color:var(--brass);transition:background .2s,color .2s}}
  .cta:hover .arw{{background:var(--brass);color:var(--bg)}}
  .cta .ar{{width:15px;height:15px;display:block}}
  /* right column — ink/brass blueprint on the page (no plate); line-art flips by theme */
  .bpframe{{position:relative}}
  .bpframe svg{{width:100%;max-height:480px;display:block}}
  .bpframe svg .l{{stroke:var(--bp-line);fill:none;stroke-width:1.2}}
  .bpframe svg .lf{{stroke:var(--bp-soft);fill:none;stroke-width:1}}
  .bpframe svg .a{{stroke:var(--brass);fill:none;stroke-width:1.3}}
  .bpframe svg .af{{fill:var(--brass)}}
  .bpframe svg .grid{{stroke:var(--bp-grid);stroke-width:1;fill:none}}
  .bpframe svg text{{font-family:var(--font-mono);fill:var(--muted);font-size:9px;letter-spacing:.08em}}
  .bpframe svg text.acc{{fill:var(--brass)}}
  .bpframe svg text.big{{fill:var(--ink-soft);font-size:10px}}
  .bpcap{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-top:14px;font-family:var(--font-mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);flex-wrap:wrap}}
  .bpcap .hero-cap{{color:var(--faint);transition:color .2s}}
  .bpcap .hero-cap b{{color:var(--brass);font-weight:500}}
  .bpcap .hero-cap:hover{{color:var(--ink)}}
  /* field-file card (dark blueprint card) */
  .card{{position:relative;background:var(--card-bg);color:var(--card-ink);border-radius:14px;overflow:hidden;box-shadow:0 30px 60px -28px rgba(0,0,0,.45)}}
  [data-theme="dark"] .card{{border:1px solid var(--card-hair)}}
  .card .reg{{position:absolute;width:16px;height:16px;border:1.5px solid var(--bp);opacity:.55;z-index:3}}
  .card .reg.tl{{top:14px;left:14px;border-right:none;border-bottom:none}}
  .card .reg.tr{{top:14px;right:14px;border-left:none;border-bottom:none}}
  .card .reg.bl{{bottom:14px;left:14px;border-right:none;border-top:none}}
  .card .reg.br{{bottom:14px;right:14px;border-left:none;border-top:none}}
  .bp-stage{{position:relative;padding:26px 26px 8px;background:radial-gradient(120% 90% at 70% 10%,rgba(216,162,74,.06),transparent 60%)}}
  .bp-stage svg{{width:100%;height:auto;display:block}}
  .bp-disc{{fill:none;stroke:var(--bp);stroke-width:1;opacity:.28}}
  .bp-blade line{{stroke:var(--bp);stroke-width:1;opacity:.22}}
  .bp-arm{{fill:none;stroke:var(--bp);stroke-width:2.4;stroke-linecap:round}}
  .bp-body{{fill:rgba(216,162,74,.05);stroke:var(--bp);stroke-width:1.6}}
  .bp-part{{fill:none;stroke:var(--bp);stroke-width:1.4}}
  .bp-mark{{stroke:var(--bp-soft);stroke-width:1}}
  .card-body{{padding:6px 34px 34px;position:relative}}
  .card .ghost{{font-family:var(--font-head);font-weight:400;font-size:74px;line-height:.8;color:transparent;-webkit-text-stroke:1px var(--card-faint);letter-spacing:-.02em;display:block;margin-bottom:6px}}
  .card .keb{{font-family:var(--font-mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--bp);margin-bottom:12px}}
  .card h3{{font-family:var(--font-head);font-weight:600;font-size:clamp(22px,2.5vw,28px);line-height:1.14;letter-spacing:-.012em;color:var(--card-ink);margin:0}}
  .card .ffmodel{{color:var(--bp)}}
  .card .ff-cfg{{display:flex;align-items:center;gap:9px;font-family:var(--font-mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--card-faint);margin:4px 0 10px}}
  .card p{{font-size:15.5px;color:var(--card-soft);max-width:52ch;margin-top:14px}}
  .card .foot{{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-top:24px;padding-top:18px;border-top:1px solid var(--card-hair)}}
  .card .meta{{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.06em;color:var(--card-faint);text-transform:uppercase}}
  .card .meta b{{color:var(--bp);font-weight:500}}
  .readmore{{display:inline-flex;align-items:center;gap:11px;font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--card-ink)}}
  .readmore .ico{{width:28px;height:28px;border-radius:50%;border:1px solid var(--bp);color:var(--bp);display:grid;place-items:center;transition:transform .25s}}
  .readmore .ar{{width:14px;height:14px;display:block}}
  .readmore:hover .ico{{transform:translateX(4px)}}
  /* content sections below the hero */
  .section-h{{font-family:var(--font-mono);font-size:.72rem;letter-spacing:.08em;color:var(--muted);text-transform:uppercase;margin:0 0 1.1rem;display:flex;gap:.6rem;align-items:center}}
  .section-h::after{{content:"";flex:1;height:1px;background:var(--hair)}}
  .block{{margin:46px 0}}
  /* home newsroom — real factual article cards */
  .nr-grid2{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}
  .nr-card{{display:flex;flex-direction:column;gap:.5rem;border:1px solid var(--hair);border-radius:12px;padding:1.2rem 1.3rem;text-decoration:none;color:inherit;transition:border-color .2s var(--ease),transform .2s var(--ease)}}
  .nr-card:hover{{border-color:var(--brass);transform:translateY(-2px)}}
  .nr-kind{{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--brass)}}
  .nr-t{{font-family:var(--font-head);font-weight:600;font-size:1.08rem;line-height:1.25;color:var(--ink)}}
  .nr-go{{margin-top:auto;font-family:var(--font-mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);display:inline-flex;align-items:center;gap:8px}}
  .nr-go .ar{{width:13px;height:13px}}
  @media (max-width:760px){{.nr-grid2{{grid-template-columns:1fr}}}}
  /* 02 · Browse — featured real systems (pure-value cards, hairline grid) */
  .browse-lead{{font-family:var(--font-head);font-size:1.05rem;color:var(--muted);max-width:54ch;margin:14px 0 0}}
  .fsys-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0 14px;border-top:1px solid var(--hair-strong);margin-top:22px}}
  @media (max-width:860px){{.fsys-grid{{grid-template-columns:repeat(2,1fr)}}}}
  @media (max-width:560px){{.fsys-grid{{grid-template-columns:1fr}}}}
  .fsys{{display:flex;flex-direction:column;gap:11px;padding:22px 18px 20px;border-bottom:1px solid var(--hair);text-decoration:none;color:inherit;min-height:150px;transition:background .15s var(--ease)}}
  .fsys:hover{{background:var(--bg-2)}}
  /* top row grouped LEFT (glyph + category together) so the card reads as one column, not scattered corners */
  .fsys-top{{display:flex;align-items:center;gap:9px}}
  .fsys-g,.fsys-g svg{{width:26px;height:26px;display:block;flex:0 0 26px}}
  .fsys-g .bp-line{{stroke:var(--muted)}}
  .fsys-kb{{font-family:var(--font-mono);font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--brass)}}
  .fsys-nm{{font-family:var(--font-head);font-weight:600;font-size:18px;line-height:1.18;color:var(--ink)}}
  .fsys-mk{{display:block;font-family:var(--font-mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);font-weight:500;margin-bottom:3px}}
  .fsys:hover .fsys-nm{{color:var(--brass)}}
  .fsys:hover .fsys-go{{transform:translateX(4px)}}
  .fsys-ft{{margin-top:auto;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
  .fsys-mt{{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.02em;color:var(--muted)}}
  .fsys-tier{{color:var(--ink-soft);font-weight:600}}
  .fsys-b{{font-family:var(--font-mono);font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--brass);border:1px solid var(--brass);border-radius:3px;padding:1px 6px}}
  .fsys-go{{margin-left:auto;color:var(--brass);transition:transform .2s var(--ease)}}
  .fsys-go .ar{{width:15px;height:15px;display:block}}
  @media (max-width:900px){{
    .field{{padding:48px 0 48px}}
    .hero-foot{{align-items:flex-start;gap:20px}}
    .statribbon{{gap:24px}}
    .wrap{{padding:0 20px}}
  }}
</style>
</head>
<body>

{header("", "home")}

{live_hero_html}

<main class="wrap">
  <div class="regdiv"><b class="lab">{bilingual("01 · Newsroom", "01 · Bài viết")}</b><span class="ln"></span>
    <a class="ncta" href="news.html"><span>{bilingual("All articles", "Tất cả bài")}</span><span class="ico">{ARROW}</span></a></div>
  <div class="block">
{newsroom_block}
  </div>
</main>

<main class="wrap">
  <div class="regdiv"><b class="lab">{bilingual("02 · Registry", "02 · Hồ sơ")}</b><span class="ln"></span>
    <a class="ncta" href="registry.html" data-audit="fpdesk">{bilingual("All registry records", "Toàn bộ hồ sơ")}<span class="ico">{ARROW}</span></a></div>
  <p class="browse-lead">{bilingual(
    "Records straight from the registry, by desk — events the editorial desk has not written up appear here, field-rendered, never duplicated.",
    "Hồ sơ thẳng từ registry, theo desk — sự kiện ban biên tập chưa viết thì hiện ở đây, render từ field, không trùng bài.")}</p>
  {desks_html}
</main>

<!-- light/dark rhythm — record-status as a full-bleed dark plate band (TIP-P01) -->
<section class="sec plate" data-audit="plate"><div class="wrap">
  <span class="eyebrow">{bilingual("Record", "Hồ sơ")}</span>
  <h2 class="h2">{bilingual("Record status", "Tình trạng bản ghi")}</h2>
  <p class="sub">{bilingual(
    f"Every figure computed live from {n} entities — nothing hand-typed.",
    f"Mọi con số tính sống từ {n} thực thể — không gõ tay.")}</p>
  {masthead}
  <div class="regdiv"><b class="lab">{bilingual("Spec coverage · per cell", "Độ phủ spec · từng ô")}</b><span class="ln"></span></div>
  {coverage_matrix(site)}
</div></section>

<main class="wrap">
  {monitor_teaser("")}
</main>

<main class="wrap">
  <div class="regdiv"><b class="lab">{bilingual("03 · Browse", "03 · Tra cứu")}</b><span class="ln"></span>
    <a class="ncta" href="reference.html" data-audit="browse">{bilingual(
      f"Browse & filter all {n} systems", f"Duyệt & lọc toàn bộ {n} hệ thống")}<span class="ico">{ARROW}</span></a></div>
  <p class="browse-lead">{bilingual(
    "Six of the best-documented systems, a way into the full record.",
    "Sáu hồ sơ được dẫn chứng đầy nhất, lối vào toàn bộ bản ghi.")}</p>
  {featured_html}
</main>

{footer("")}
<script src="base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.initDraw();
  USRBase.initReveal();
  USRBase.initCountup();
  USRBase.initLiveHero();
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""
    OUT.write_text(doc)
    print(f"index.html | hero=blueprint+ribbon | facts={f['entities']} entities · "
          f"{len(f['country_rank'])} countries · {f['coverage']}% coverage")


if __name__ == "__main__":
    main()
