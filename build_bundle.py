#!/usr/bin/env python3
"""TIP-008 — single-file BUNDLE export (bundle.html). One self-contained file (inline CSS+JS, all
markup pre-rendered) that runs from disk / email with no server — to teach "the method" on the REAL
registry, not a sample.

Reuses the GATES-PROVEN renderers verbatim (rows from build_reference, detail from build_detail,
masthead from build_index, long-form from build_analysis), so the bundle cannot drift from the live
site or weaken honest-null / tier / disputed. Detail is pre-rendered into hidden fragments revealed
on row-click — no embedded JSON, no client re-render, no fabrication surface.

Zero-fabrication: registry data is the REAL 200 (totals computed live at build); editorial prose is
the marked sample (banner states both plainly).
"""
import json, pathlib, re
from build_reference import render_row, render_facets, esc, fleet_log_ranges
from build_index import live_facts, render_masthead
from build_detail import detail_fragment, DETAIL_CSS
from build_analysis import four_questions, render_body, related_rail, sources_apparatus, SECTION

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
GLOSS = ROOT / "content" / "glossary.json"
OUT = ROOT / "bundle.html"


def inline_links(h):
    """Rewrite multi-file hrefs to in-bundle anchors: entity -> detail overlay, others -> sections."""
    h = re.sub(r'href="(?:\.\./)?uav/([a-z0-9-]+)\.html"', r'href="#d-\1"', h)
    h = re.sub(r'href="(?:\./|\.\./)?reference\.html"', 'href="#reference"', h)
    h = re.sub(r'href="(?:\./|\.\./)?index\.html(?:#[a-z-]+)?"', 'href="#top"', h)
    h = re.sub(r'href="(?:\./|\.\./)?news/[a-z0-9-]+\.html"', 'href="#reference"', h)
    h = re.sub(r'href="(?:\./|\.\./)?analysis/[a-z0-9-]+\.html"', 'href="#analysis"', h)
    return h


def long_form(a, site, glossary):
    au = a.get("author", {})
    dtag = '<span class="dtag">▦ Dữ liệu</span>' if a.get("figures") else ""
    head_chips = "".join(
        f'<span class="echip"><i>CN</i> {esc(t["label"])}</span>'
        for t in a.get("entity_tags", []) if t.get("type") == "technology")
    return (
        '<header class="lf-head">'
        f'<div class="kicker"><span>Phân tích · {esc(SECTION.get(a["section"],""))}</span>{dtag}</div>'
        f'<h1 class="lf-h1">{esc(a["title"])}</h1>'
        f'<p class="lf-stand">{esc(a["dek"])}</p>'
        '<div class="lf-meta"><div class="au"><span class="av"></span>'
        f'<span class="nm">{esc(au.get("name",""))}<small>{esc(au.get("role",""))}</small></span></div>'
        f'<span class="dot"></span><span class="mi">{esc(a.get("date",""))}</span>'
        f'<span class="dot"></span><span class="mi">{a.get("reading_min","")} phút đọc</span>'
        f'<span class="dot"></span><span class="chips" style="display:inline-flex">{head_chips}</span></div>'
        '</header>'
        f'{four_questions(a["four_questions"])}'
        '<div class="lf-grid"><article class="lf-body">'
        f'{render_body(a, site, glossary)}</article>'
        f'<aside class="lf-aside">{related_rail(a, glossary)}</aside></div>'
        f'{sources_apparatus(a)}')


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]  # schema/2: UAV surface only
    arts = json.loads(ARTS.read_bytes())["articles"]
    glossary = json.loads(GLOSS.read_bytes())
    f = live_facts(site)

    newsroom_css = (ROOT / "base" / "newsroom.css").read_text()
    css = (ROOT / "base" / "design-system.css").read_text() + "\n" \
        + newsroom_css + "\n" + DETAIL_CSS
    # TEETH: the bundle inlines newsroom.css next to the detail spec rows / micro-tracks. If
    # newsroom reuses a DETAIL-OWNED class name, its rule bleeds onto those elements in the bundle
    # (two regressions on 2026-06-24: `.spec` hatch covered rows; `.rail` border/padding shifted
    # tracks). Detail owns these class names — newsroom must never name them. Fail loud.
    DETAIL_OWNED = ("spec", "track", "vt", "drow", "drows")   # trk/tick/rng removed: detail now uses the shared .ri-spark
    nr_nocomments = re.sub(r"/\*.*?\*/", "", newsroom_css, flags=re.S)  # ignore explanatory comments
    leaked = [c for c in DETAIL_OWNED if re.search(rf"\.{c}\b", nr_nocomments)]
    if leaked:
        raise SystemExit(f"BUNDLE GATE: newsroom.css names detail-owned class(es) {leaked} — in the "
                         f"bundle they collide with spec rows/micro-tracks. Rename the newsroom rule.")
    js = (ROOT / "base" / "base.js").read_text()

    facets = inline_links(render_facets(ents, labels))
    _rng = fleet_log_ranges(ents)
    rows = inline_links("\n".join(render_row(e, labels, _rng) for e in ents))
    masthead = render_masthead(f, labels)
    ranges = site["aggregates"].get("spec_range", {})
    frags = "\n".join(
        f'<div id="d-{esc(e["slug"])}">{inline_links(detail_fragment(e, labels, ranges))}</div>'
        for e in ents)
    analysis = next((a for a in arts if a["type"] == "analysis"), None)
    lf = inline_links(long_form(analysis, site, glossary)) if analysis else ""

    bundle_css = """
  .bwrap{max-width:var(--w-wide);margin:0 auto;padding:0 1.4rem}
  .bsec{padding:44px 0;border-top:1px solid var(--hair)}
  .bsec > h2{font-family:var(--serif);font-weight:600;font-size:clamp(22px,2.6vw,30px);letter-spacing:-.015em;margin-bottom:6px}
  .bsec > .sub{color:var(--muted);font-size:14px;margin-bottom:24px}
  #frags{display:none}
  :root[data-lang="en"] .tg .s-en{opacity:1;color:var(--brass)}
  :root[data-lang="vn"] .tg .s-vn{opacity:1;color:var(--brass)}
  .ov{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:80;overflow:auto}
  .ov[hidden]{display:none}
  .ov-card{background:var(--bg);max-width:880px;margin:38px auto;border:1px solid var(--hair-strong);border-radius:10px;padding:0 8px}
"""

    doc = f"""<!DOCTYPE html>
<html lang="vi" data-theme="light" data-lang="vn" id="top">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Uncrewed Systems Review — bản dựng một file (200 thật)</title>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{css}
{bundle_css}
</style>
</head>
<body>
<div class="spec"><div class="in"><div class="wrap">
  <span>◧ Bản dựng một file</span><span style="color:var(--hair-strong)">·</span>
  <span><b>Dữ liệu registry: {f['entities']} thực thể THẬT</b> (tổng tính sống) · nội dung biên-tập là chữ mẫu đánh-dấu</span>
</div></div></div>

<header class="nbar"><div class="wrap">
  <span class="wm-name">Uncrewed Systems Review<small>Vietnam UAV Intelligence</small></span>
  <nav class="nav"><a href="#reference" class="on">Tra cứu</a><a href="#analysis">Phân tích</a></nav>
  <div class="nctl">
    <button class="tg" id="lang" aria-label="Language"><span class="s s-en">EN</span><span aria-hidden="true">/</span><span class="s s-vn">VN</span></button>
    <button class="tg" id="theme" aria-label="Theme"><span data-lang-en>Dark</span><span data-lang-vn>Tối</span></button>
  </div>
</div></header>

<main class="bwrap">
  <section class="bsec" style="border-top:0">
    <h2>Tình trạng bản ghi</h2>
    <p class="sub">Mọi con số tính sống từ {f['entities']} thực thể trong registry — không gõ tay.</p>
    {masthead}
  </section>

  <section class="bsec" id="reference">
    <h2>Tra cứu — toàn bộ {f['entities']} hệ thống</h2>
    <p class="sub">Lọc theo phân khúc · lớp tuân thủ · quốc gia; tìm; sắp. Bấm một dòng để mở hồ sơ (nguồn + tier, honest-null, ô tranh chấp).</p>
    {facets}
    <div class="index-list">
{rows}
    </div>
  </section>

  <section class="bsec" id="analysis">
    {lf}
  </section>
</main>

<div id="frags">
{frags}
</div>

<div class="ov" id="ov" hidden><div class="ov-card"><div class="dwrap">
  <div class="topbar"><a class="back" id="ov-close">← Đóng</a></div>
  <div id="ov-body"></div>
</div></div></div>

<script>
{js}
</script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.initReveal();
  USRBase.initRegistry({{ grid: ".index-list", item: ".row-item" }});
  // detail overlay — reveal the pre-rendered fragment for the clicked entity
  document.addEventListener("click", function (ev) {{
    var a = ev.target.closest('a[href^="#d-"]'); if (!a) return; ev.preventDefault();
    var frag = document.getElementById("d-" + a.getAttribute("href").slice(3));
    if (!frag) return;
    document.getElementById("ov-body").innerHTML = frag.innerHTML;
    var ov = document.getElementById("ov"); ov.hidden = false; ov.scrollTop = 0;
  }});
  document.getElementById("ov-close").addEventListener("click", function () {{ document.getElementById("ov").hidden = true; }});
  document.getElementById("ov").addEventListener("click", function (ev) {{ if (ev.target === this) this.hidden = true; }});
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""
    OUT.write_text(doc)
    sz = len(doc.encode())
    print(f"bundle.html: {len(ents)} entities · {sz//1024} KB · masthead live ({f['entities']} systems, "
          f"{f['blue_verified']} Blue, {f['coverage']}% coverage) · detail fragments embedded")


if __name__ == "__main__":
    main()
