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
from glyphs import glyph_svg
from build_news import news_front
from build_analysis import analysis_feature

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


def live_facts(site):
    """Real, live figures computed from site-data — never hardcoded (CONSTRAINT 8)."""
    ents = site["entities"]
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
    return (f'<div class="stat-cell"><span class="statfig">{esc(value)}</span>'
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


# ---- field-file cards (the hero of the data: real entities in the blueprint-card idiom) ----
def blueprint_svg():
    """Geometric signature illustration ONLY — no text callouts, no fabricated dimension.
    The aircraft anatomy is decorative idiom; entity claims live in the card body, sourced."""
    return ('<div class="bp-stage"><svg viewBox="0 0 760 392" aria-hidden="true">'
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
            '<circle class="bp-part" cx="380" cy="284" r="10"></circle>'
            '</svg></div>')


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


def coverage_matrix(site):
    """Real per-cell coverage (11 specs × N entities). Filled = field has a value; sparse is shown,
    not hidden — rigor as evidence. % per row is the live aggregate (== auditor coverage)."""
    ents = site["entities"]
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


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    ents = site["entities"]
    groups = site["field_groups"]["display"] + site["field_groups"]["spec"]
    f = live_facts(site)
    n = f["entities"]
    feat = pick_featured(ents, groups, 1)
    hero_card = field_file_card(feat[0], 1, labels, groups, big=True)
    arts = json.loads(ARTS.read_bytes())["articles"]
    news_html = news_front(arts, base=".")          # Part A — newsroom front
    feat_html = analysis_feature(arts, site)         # Part B — analysis feature teaser
    masthead = render_masthead(f, labels)

    doc = f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Uncrewed Systems Review</title>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<link rel="stylesheet" href="base/newsroom.css">
<style>
  /* home layout in the approved idiom (components reuse the shared design system) */
  .wrap{{max-width:1200px;margin:0 auto;padding:0 32px}}
  .bar{{border-bottom:1px solid var(--hair)}}
  .bar .wrap{{display:flex;align-items:center;height:64px;gap:20px}}
  .wm-name{{font-family:var(--font-head);font-weight:600;font-size:18px;letter-spacing:-.01em}}
  .wm-name small{{display:block;font-family:var(--font-mono);font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;margin-top:2px;font-weight:400}}
  .ctl{{margin-left:auto;display:flex;gap:8px}}
  :root[data-lang="en"] .tg .s-en{{opacity:1;color:var(--brass)}}
  :root[data-lang="vn"] .tg .s-vn{{opacity:1;color:var(--brass)}}
  /* hero */
  .field{{position:relative;padding:84px 0 90px;overflow:hidden}}
  .field .wrap{{position:relative;z-index:2;display:grid;grid-template-columns:.92fr 1.18fr;gap:60px;align-items:center}}
  .watermark{{position:absolute;left:-180px;bottom:-160px;width:920px;z-index:1;pointer-events:none}}
  .watermark svg{{width:100%;height:auto;display:block}}
  .wm-stroke{{fill:none;stroke:var(--wm,rgba(26,26,28,.045));stroke-width:1.4}}
  .eyebrow{{font-family:var(--font-mono);font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:var(--brass);font-weight:500;display:inline-flex;align-items:center;gap:10px}}
  .eyebrow::before{{content:"";width:22px;height:1px;background:var(--brass-bright)}}
  .lead-h{{font-family:var(--font-head);font-weight:600;font-size:clamp(34px,4.4vw,52px);line-height:1.04;letter-spacing:-.018em;margin:20px 0 0}}
  .lead-p{{font-size:17px;color:var(--ink-soft);max-width:42ch;margin-top:20px}}
  .cta{{display:inline-flex;align-items:center;gap:14px;margin-top:30px;font-family:var(--font-mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink);border:1px solid var(--hair-strong);border-radius:999px;padding:11px 12px 11px 22px;transition:border-color .25s,gap .25s}}
  .cta:hover{{border-color:var(--brass-bright);gap:18px}}
  .cta .ico{{position:relative;width:30px;height:30px;border-radius:50%;background:var(--brass);color:#fff;display:grid;place-items:center;flex:0 0 auto}}
  .cta .ar{{width:15px;height:15px;display:block}}
  [data-theme="dark"] .cta .ico{{color:#15171B}}
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
  .field-files{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
  @media (max-width:900px){{
    .field .wrap{{grid-template-columns:1fr;gap:40px}}
    .watermark{{width:680px;left:-220px;bottom:-120px;opacity:.7}}
    .field-files{{grid-template-columns:1fr}}
    .wrap{{padding:0 20px}}
  }}
</style>
</head>
<body>

<header class="bar">
  <div class="wrap">
    <span class="wm-name">Uncrewed Systems Review<small>{bilingual("In the field", "Trên thực địa")}</small></span>
    <div class="ctl">
      <button class="tg" id="lang" aria-label="Language"><span class="s s-en">EN</span><span aria-hidden="true">/</span><span class="s s-vn">VN</span></button>
      <button class="tg" id="theme" aria-label="Theme"><span data-lang-en>Dark</span><span data-lang-vn>Tối</span></button>
    </div>
  </div>
</header>

<section class="field" data-audit="hero">
  <div class="watermark" aria-hidden="true">{WATERMARK}</div>
  <div class="wrap">
    <div class="reveal is-in">
      <span class="eyebrow" data-audit="eyebrow">{bilingual("In the field", "Trên thực địa")}</span>
      <h1 class="lead-h" data-audit="lead">{bilingual("Uncrewed systems, seen clearly.", "Hệ thống không người lái, nhìn cho rõ.")}</h1>
      <p class="lead-p">{bilingual(
        "How verified data changes a real decision — explained plainly, for the people who have to make the call, not only the engineers who build the aircraft.",
        "Dữ liệu kiểm chứng thay đổi một quyết định thật ra sao, giải thích bằng lời rõ ràng, cho người phải ra quyết định chứ không chỉ cho kỹ sư làm ra máy bay.")}</p>
      <a class="cta" href="reference.html" data-audit="cta">{bilingual("All field files", "Tất cả hồ sơ")}<span class="ico">{ARROW}</span></a>
    </div>
    {hero_card}
  </div>
</section>

<main class="wrap">
  <div class="regdiv"><b class="lab">{bilingual("01 · Newsroom", "01 · Tin tức")}</b><span class="ln"></span></div>
  <div class="block">
{news_html}
  </div>

  <div class="regdiv"><b class="lab">{bilingual("02 · Analysis", "02 · Phân tích")}</b><span class="ln"></span></div>
  <div class="block">
    <div class="sechead"><div><span class="eyebrow">{bilingual("Analysis", "Phân tích")}</span>
      <h2 class="h2">{bilingual("In depth — long-form", "Chuyên sâu — đọc dạng long-form")}</h2></div>
      <a class="ncta" href="analysis/{esc(arts[0]["slug"])}.html"><span>{bilingual("All analysis", "Tất cả phân tích")}</span><span class="ico">{ARROW}</span></a></div>
{feat_html}
  </div>
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
  <div class="regdiv"><b class="lab">{bilingual("03 · Browse", "03 · Tra cứu")}</b><span class="ln"></span></div>
  <div class="block">
    <a class="cta" href="reference.html" data-audit="browse">{bilingual(
      f"Browse & filter all {n} systems", f"Duyệt & lọc toàn bộ {n} hệ thống")}<span class="ico">{ARROW}</span></a>
  </div>
</main>

<script src="base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.initDraw();
  USRBase.initReveal();
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""
    OUT.write_text(doc)
    print(f"index.html | hero={maker_model(feat[0])[0]} {maker_model(feat[0])[1]} | "
          f"featured={[e['slug'] for e in feat]} | facts={f['entities']} entities")


if __name__ == "__main__":
    main()
