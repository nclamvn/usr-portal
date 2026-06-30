#!/usr/bin/env python3
"""TIP-003 — Reference layer. Static-generate reference.html from out/site-data.json.
Renders every REAL entity as a card with 5-state evidence chips. Honest-null: a field
that is unverified or absent renders "—" (the registry draft value is NEVER shown — it
is already null in site-data). Totals come from site-data.aggregates (CONSTRAINT 8),
never hardcoded. Bilingual EN/VN, light/dark via the reconciled base.
"""
import json, html, pathlib, math
from glyphs import glyph_svg
from footer import footer
from nav import nav
from header import header
from seo import meta as seo_meta

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
OUT = ROOT / "reference.html"

HEADER_FIELDS = ["manufacturer", "name", "manufacturer_country", "market_segment", "provenance_class"]
SPEC_FIELDS = ["mtow_kg", "max_payload_kg", "endurance_min", "max_range_km",
               "max_link_km", "max_speed_ms", "service_ceiling_m",
               "encryption", "blue_uas", "ndaa_compliant", "gps_denied_capable"]
NULL_STATUSES = {None, "absent", "none"}


def esc(x):
    return html.escape(str(x))


def bilingual(en, vn):
    return f'<span data-lang-en>{esc(en)}</span><span data-lang-vn>{esc(vn)}</span>'


def friendly(kind, val, labels):
    """Friendly bilingual label for an enum value (segment / klass); title-case fallback.
    NEVER renders a raw dict — guards against non-string values."""
    if val is None or isinstance(val, (dict, list)):
        return "—"
    m = labels.get(kind, {}).get(val)
    if m:
        return bilingual(m["en"], m["vn"])
    return esc(str(val).replace("_", " ").title())


def fmt_value(value, field, labels):
    """Display a real value, bilingually where the value is an enum/bool. Never invents."""
    if isinstance(value, bool):
        b = labels["bool"][str(value).lower()] if str(value).lower() in labels["bool"] else None
        if b:
            return bilingual(b["en"], b["vn"])
        return "Yes" if value else "No"
    return esc(value)


def chip(fo, labels):
    """5-state evidence chip. unverified/absent -> '—' (no draft value)."""
    status = fo.get("status")
    value = fo.get("value")
    tier = fo.get("source_tier")
    if status in NULL_STATUSES:                       # absent — no data at all
        return ('—', f'<span class="chip" data-status="absent" data-audit="chip">'
                     f'{bilingual("no data", "chưa có dữ liệu")}</span>')
    if status == "unverified":                        # tried, not proven — value stays hidden
        return ('—', f'<span class="chip" data-status="unverified" data-audit="chip">'
                     f'{bilingual("unverified", "chưa kiểm chứng")}</span>')
    if status == "disputed":                          # keep both claims, never pick one
        claims = fo.get("claims") or []
        vals = " / ".join(esc(c.get("claimed_value")) for c in claims if c.get("claimed_value") is not None) or "—"
        return (vals, f'<span class="chip" data-status="disputed" data-audit="chip">'
                      f'{bilingual("disputed", "tranh chấp")}</span>')
    if status == "derived":
        return (fmt_value(value, None, labels),
                f'<span class="chip" data-status="derived" data-audit="chip">'
                f'{bilingual("derived", "suy ra")}</span>')
    # verified
    tier_badge = f'<span class="tier">{esc(tier)}</span>' if tier else ""
    return (fmt_value(value, None, labels),
            f'<span class="chip" data-status="verified" data-audit="chip">{tier_badge}'
            f'{bilingual("verified", "đã kiểm")}</span>')


def flag1(fo):
    """'1' iff a boolean compliance field is verified-true (honest: unverified/null -> '')."""
    return "1" if (fo.get("status") == "verified" and fo.get("value") is True) else ""


def maker_model(e):
    """(maker, bare-model). The registry stores name as "<maker> <model>"; strip the duplicated
    maker prefix so titles read "ACSL · ACSL-PF2", not "ACSL ACSL ACSL-PF2"."""
    maker = e["manufacturer"].get("value") or "—"
    name = e["name"].get("value") or "—"
    model = name
    if maker != "—" and name.lower().startswith(maker.lower() + " "):
        model = name[len(maker) + 1:]
    return maker, model


def row_dataset(e):
    """The data-* facet/sort keys (raw values, NOT friendly labels) shared by index rows."""
    maker, model = maker_model(e)
    return {
        "name": f"{maker} {model}".lower(),
        "segment": e["market_segment"].get("value") or "",
        "klass": e.get("provenance_class") or "",
        "country": e["manufacturer_country"].get("value") or "",
        "blue": flag1(e["blue_uas"]),
        "ndaa": flag1(e["ndaa_compliant"]),
    }


# 7 numeric specs — the "record-fullness" pip strip (TIP-P04, reuses the coverage primitive at row scale)
PIP_SPECS = ["mtow_kg", "max_payload_kg", "endurance_min", "max_range_km",
             "max_link_km", "max_speed_ms", "service_ceiling_m"]

# 3 spec columns rendered as micro-sparkbars (position of this system within the fleet's range).
# (key, data-attr, EN label, VN label). Log-scaled like the scatter axes — a declared transform, not fabrication.
SPARK_SPECS = [("mtow_kg", "mtow", "MTOW", "MTOW"),
               ("max_range_km", "range", "Range", "Tầm bay"),
               ("endurance_min", "endur", "Endurance", "Giờ bay"),
               ("max_payload_kg", "payload", "Payload", "Tải trọng")]
TIER_RANK = {"A": "3", "B": "2", "C": "1"}


def fleet_log_ranges(ents):
    """Per spec, the (log min, log max) over REAL non-null positive values. Used to place each
    sparkbar; null/absent values are NOT counted (they render as honest-null dashed rails)."""
    rng = {}
    for key, _, _, _ in SPARK_SPECS:
        vals = [e[key].get("value") for e in ents]
        vals = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0]
        rng[key] = (math.log(min(vals)), math.log(max(vals))) if len(vals) >= 2 else None
    return rng


def row_tier(e):
    """The strongest source tier across this entity's filled fields (A>B>C). None if nothing sourced.
    Provenance-forward: a single letter that says how well-sourced the record is."""
    best = None
    for k in HEADER_FIELDS + SPEC_FIELDS:
        fo = e.get(k)
        t = fo.get("source_tier") if isinstance(fo, dict) else None
        if t in ("A", "B", "C") and (best is None or t < best):
            best = t
    return best


def spark_cell(e, key, rng):
    """(html, raw_value_or_blank). Real value -> solid bar placed by log position in the fleet range
    (min visible nub so the smallest real value is not mistaken for null). Null -> dashed rail."""
    v = (e.get(key) or {}).get("value")
    if v is None or isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0 or rng.get(key) is None:
        return ('<span class="ri-spark null" aria-hidden="true"></span>', "")
    lo, hi = rng[key]
    pos = 0.0 if hi <= lo else (math.log(v) - lo) / (hi - lo)
    pct = max(6, min(100, round(pos * 100)))
    return (f'<span class="ri-spark" title="{esc(v)}"><i style="width:{pct}%"></i></span>', esc(v))


def spec_table_head():
    """Sortable column header for the spec-analytics table — reused by reference.html and the
    company fleet. No links, so no rel prefix needed."""
    def head_cell(sort, en, vn, cls):
        return (f'<button class="col-sort {cls}" type="button" data-sort="{sort}">'
                f'{bilingual(en, vn)}<span class="cs-ar" aria-hidden="true"></span></button>')
    return (
        '<div class="idx-head">'
        '<span class="ih-glyph"></span>'
        + head_cell("name", "Maker / Model", "Hãng / Mẫu", "ih-id")
        + head_cell("mtow", "MTOW", "MTOW", "ih-col")
        + head_cell("range", "Range", "Tầm bay", "ih-col")
        + head_cell("endur", "Endurance", "Giờ bay", "ih-col")
        + head_cell("payload", "Payload", "Tải trọng", "ih-col")
        + head_cell("cov", "Cov", "Độ đầy", "ih-col")
        + head_cell("tier", "Tier", "Nguồn", "ih-col")
        + '</div>')


def render_row(e, labels, rng, rel=""):
    """A light INDEX row linking to its detail page — NOT the rich detail card (that lives in
    build_detail). A spec-analytics table row: maker/model + country/segment/class, three
    log-placed spec sparkbars (MTOW/range/endurance), a record-fullness N/7 column and a
    source-tier badge. Sparse specs render as honest-null dashed rails, never zero bars.
    Carries data-* (incl. numeric sort keys) so client facet/search/sort works on rows."""
    maker, model = maker_model(e)
    country = e["manufacturer_country"].get("value") or "—"
    seg = friendly("segment", e["market_segment"].get("value"), labels)
    pclass = friendly("klass", e.get("provenance_class"), labels)
    d = row_dataset(e)
    flags = ""
    if d["blue"]:
        flags += '<span class="chip" data-status="verified" data-audit="chip">Blue UAS</span>'
    if d["ndaa"]:
        flags += '<span class="chip" data-status="verified" data-audit="chip">NDAA</span>'
    present = sum(1 for k in PIP_SPECS if e[k].get("value") is not None)
    # three spec sparkbars + their raw values for the data-* sort keys (blank = honest-null, sorts last)
    sparks, svals = [], {}
    for key, attr, _, _ in SPARK_SPECS:
        cell, raw = spark_cell(e, key, rng)
        sparks.append(f'<span class="ri-col" data-c="{attr}">{cell}</span>')
        svals[attr] = raw
    cov_html = (f'<span class="ri-col ri-covcol"><span class="ri-cov" title="{present}/7 spec" '
                f'aria-label="{present}/7 spec có số">{present}<span class="ri-cov-d">/7</span></span></span>')
    tier = row_tier(e)
    tier_html = (f'<span class="ri-tier" data-t="{tier}">{tier}</span>' if tier
                 else '<span class="ri-tier-null" aria-hidden="true">—</span>')
    tier_col = f'<span class="ri-col ri-tiercol">{tier_html}{flags}</span>'
    return (
        f'<a class="row-item ri-spec reveal" href="{rel}uav/{esc(e["slug"])}.html" data-audit="row" '
        f'data-name="{esc(d["name"])}" data-segment="{esc(d["segment"])}" data-klass="{esc(d["klass"])}" '
        f'data-country="{esc(d["country"])}" data-blue="{d["blue"]}" data-ndaa="{d["ndaa"]}" '
        f'data-mtow="{svals["mtow"]}" data-range="{svals["range"]}" data-endur="{svals["endur"]}" '
        f'data-payload="{svals["payload"]}" data-cov="{present}" data-tier="{TIER_RANK.get(tier, "")}">'
        f'<span class="ri-glyph">{glyph_svg(e.get("frame_glyph", "unknown"))}</span>'
        f'<span class="ri-id"><span class="ri-name"><b>{esc(maker)}</b> '
        f'<span class="ri-model">{esc(model)}</span></span>'
        f'<span class="ri-meta mono">{esc(country)} · {seg} · {pclass}</span></span>'
        f'{"".join(sparks)}{cov_html}{tier_col}</a>')


def facet_options(ents, getter):
    """Distinct non-null values present, ranked by frequency then name (deterministic)."""
    counts = {}
    for e in ents:
        v = getter(e)
        if v:
            counts[v] = counts.get(v, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def facet_row(label_en, label_vn, group, kind, options, labels):
    """One toggle-group row. brass-active styling lives in .tg; here we only emit aria-pressed=false."""
    btns = "".join(
        f'<button class="tg" type="button" data-facet="{group}" data-value="{esc(v)}" '
        f'aria-pressed="false">{friendly(kind, v, labels) if kind else esc(str(v))}'
        f' <span class="tg-n">{n}</span></button>'
        for v, n in options)
    return (f'<div class="facet-row"><span class="lbl">{bilingual(label_en, label_vn)}</span>'
            f'{btns}</div>')


def render_facets(ents, labels):
    seg = facet_options(ents, lambda e: e["market_segment"].get("value"))
    klass = facet_options(ents, lambda e: e.get("provenance_class"))
    country = facet_options(ents, lambda e: e["manufacturer_country"].get("value"))
    n = len(ents)
    flag_row = (
        f'<div class="facet-row"><span class="lbl">{bilingual("Compliance", "Tuân thủ")}</span>'
        f'<button class="tg" type="button" data-facet="flag" data-value="blue" aria-pressed="false">Blue UAS</button>'
        f'<button class="tg" type="button" data-facet="flag" data-value="ndaa" aria-pressed="false">NDAA</button>'
        f'</div>')
    # Always-visible QUICK SEARCH box (replaces the empty collapsed-details rectangle): a real input the
    # eye reads as interactive. Same #reg-search id → the existing client filter logic keeps working.
    quick = (
        f'<div class="reg-quick">'
        f'<svg class="qicon" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
        f'<circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.6"/>'
        f'<path d="M16.5 16.5L21 21" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
        f'<input id="reg-search" class="reg-search" type="search" autocomplete="off" '
        f'aria-label="Search manufacturer or model" placeholder="maker / model…">'
        f'<span class="reg-count" aria-live="polite">{bilingual("Showing", "Hiển thị")} '
        f'<b id="reg-count-n">{n}</b> / {n}</span>'
        f'<button class="tg" id="reg-sort" type="button" aria-label="Change sort order"></button>'
        f'</div>')
    return (
        quick
        + f'<details class="facets" data-audit="facets">'
        f'<summary>{bilingual("Filters", "Bộ lọc")}</summary>'
        + facet_row("Segment", "Phân khúc", "segment", "segment", seg, labels)
        + facet_row("Class", "Lớp", "klass", "klass", klass, labels)
        + facet_row("Country", "Quốc gia", "country", None, country, labels)
        + flag_row + '</details>')


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]  # schema/2: UAV surface only
    agg = site["aggregates"]                       # totals read LIVE — never hardcoded
    facets = render_facets(ents, labels)
    rng = fleet_log_ranges(ents)
    rows = "\n".join(render_row(e, labels, rng) for e in ents)
    idx_head = spec_table_head()
    fsc = agg["field_status_counts"]
    # friendly, trust-ordered status breakdown — NEVER raw status keys (e.g. "None" -> honest-null)
    SLAB = {"verified": ("verified", "đã kiểm"), "derived": ("derived", "suy ra"),
            "disputed": ("disputed", "tranh chấp"), "unverified": ("unverified", "chưa kiểm"),
            "None": ("honest-null", "null trung thực")}
    summary = "".join(
        f'<span class="sc"><b>{fsc[k]:,}</b> {bilingual(*SLAB[k])}</span>'
        for k in ("verified", "derived", "disputed", "unverified", "None") if fsc.get(k))
    doc = f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>USR — Reference</title>
{seo_meta("USR — Reference", "Every UAV in the registry, with sources and tiers. Sparse fields shown as honest-null.", "reference.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>
  .wrap{{max-width:var(--w-wide);margin:0 auto;padding:2.2rem 1.4rem}}
  .topline{{display:flex;justify-content:space-between;align-items:flex-start;gap:1.4rem 2.5rem;flex-wrap:wrap;border-bottom:1px solid var(--hair);padding-bottom:1.3rem;margin-bottom:1.6rem}}
  .tl-left{{flex:1 1 320px}}
  .tl-left h1{{margin:0 0 .35rem}}
  .lead{{color:var(--muted);margin:0;max-width:56ch;font-size:.9rem;line-height:1.5}}
  .tl-right{{display:flex;flex-direction:column;align-items:flex-end;gap:.6rem;text-align:right}}
  .count{{font-family:var(--font-mono);color:var(--brass);font-weight:600;font-size:1.05rem}}
  .stat{{font-family:var(--font-mono);font-size:.72rem;color:var(--muted);display:flex;flex-wrap:wrap;justify-content:flex-end;gap:.2rem .7rem;max-width:30ch}}
  .stat .sc b{{color:var(--ink-soft);font-weight:600}}
  .actions{{font-family:var(--font-mono);font-size:.78rem}}
  .actions a{{color:var(--brass);text-decoration:none}}
  .actions a:hover{{text-decoration:underline}}
  /* spec-analytics row/header (.row-item.ri-spec / .idx-head / .ri-spark / .col-sort) live in the
     shared design system so the bundled snapshot reuses them too */
</style>
</head>
<body>
{header("", "reference")}
<main class="wrap">
  <div class="topline">
    <div class="tl-left">
      <h1>{bilingual("Reference", "Tham chiếu")}</h1>
      <p class="lead">{bilingual(
        "Every value traces to its source. Sparse spec fields are expected — null is honest, never invented.",
        "Mọi giá trị truy về nguồn. Field spec thưa là bình thường — null là trung thực, không bịa.")}</p>
    </div>
    <div class="tl-right">
      <div class="count" data-audit="count">{len(ents)} {bilingual("entities", "thực thể")}</div>
      <div class="stat">{summary}</div>
      <div class="actions"><a href="search.html">{bilingual("Search →", "Tìm kiếm →")}</a> · <a href="compare.html">{bilingual("Compare 2–4 →", "So sánh 2–4 →")}</a></div>
    </div>
  </div>
  <div class="regdiv"><b class="lab">{bilingual("Index · " + str(len(ents)), "Mục lục · " + str(len(ents)))}</b><span class="ln"></span></div>
  {facets}
  {idx_head}
  <div class="index-list">
{rows}
  </div>
</main>
{footer("")}
<script src="base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.mountArrows(); USRBase.initReveal();
  USRBase.initRegistry({{ grid: ".index-list", item: ".row-item" }});
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""
    OUT.write_text(doc)
    print(f"reference.html: {len(ents)} rows | totals from aggregates: {len(ents)} entities, status {fsc}")


if __name__ == "__main__":
    main()
