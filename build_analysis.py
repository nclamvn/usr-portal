#!/usr/bin/env python3
"""TIP-007/B — Analysis pillar. Static-generate analysis/<slug>.html (long-form) from
content/articles.json, in the newsroom-specimen idiom. Also exposes analysis_feature() for the home.

Editorial-intelligence invariants:
  - The four-questions box is REQUIRED (decision-support, inverted-pyramid at document level).
  - Figures pull REAL numbers LIVE from out/site-data.json (figure.kind -> a registry computation);
    never hardcoded. Prose is sample (sample:true -> banner) — the data is real, the narrative is not.
  - Every article is a node: entity-chips + inline auto-links (entity -> detail page; glossary -> def),
    "related entities" + "glossary" rails, source apparatus with tier A/B/C.
Zero-fabrication: no invented news, no quotes attributed to real people; entity-chips link only to
entities that exist in the registry.
"""
import json, pathlib, shutil, re, html
from build_reference import esc

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
GLOSS = ROOT / "content" / "glossary.json"
OUTDIR = ROOT / "analysis"

ETYPE = {"company": "HÃNG", "aircraft": "MẪU", "technology": "CN", "country": "QG"}
SECTION = {"policy": "Chính sách", "market": "Thị trường", "tech": "Công nghệ",
           "defense": "Quốc phòng", "business": "Doanh nghiệp", "intl": "Quốc tế"}
FQ = [("happening", "Đang diễn ra"), ("meaning", "Có ý nghĩa gì"),
      ("todo", "Nên làm gì tiếp"), ("data", "Dữ liệu chứng minh")]
# short VN axis labels for spec fields (display only; values are real from the registry)
SPEC_SHORT = {"mtow_kg": "MTOW", "max_payload_kg": "Tải", "endurance_min": "Bay",
              "max_range_km": "Tầm", "max_link_km": "Link", "max_speed_ms": "Tốc",
              "service_ceiling_m": "Trần", "encryption": "Mã hoá", "blue_uas": "Blue",
              "ndaa_compliant": "NDAA", "gps_denied_capable": "GPS-denied"}


def load(p):
    return json.loads(p.read_bytes())


# ---------- figures: numbers computed LIVE from the registry (never hardcoded) ----------
def figure_bars(kind, site):
    """Return (bars[(label,int_pct)], source_str). Auditor recomputes this to verify traceability."""
    if kind == "spec_fill_rate":
        fill = site["aggregates"]["spec_fill_rate"]
        bars = []
        for f in site["field_groups"]["spec"][:6]:
            d = fill.get(f)
            if not d or not d["total"]:
                continue
            bars.append((SPEC_SHORT.get(f, f), round(100 * d["present"] / d["total"])))
        return bars, "UAV Registry — aggregates.spec_fill_rate"
    if kind == "country_share":
        from collections import Counter
        uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
        tot = len(uavs) or 1
        c = Counter((e.get("manufacturer_country") or {}).get("value") for e in uavs
                    if (e.get("manufacturer_country") or {}).get("value"))
        bars = [(name, round(100 * n / tot)) for name, n in c.most_common(6)]
        return bars, "UAV Registry — manufacturer_country share"
    raise ValueError(f"unknown figure kind: {kind}")


def figure_svg(bars):
    x0, x1, base, top = 48, 500, 170, 44
    n = len(bars) or 1
    slot = (x1 - x0) / n
    bw = slot * 0.6
    rects, labs, vals = [], [], []
    for i, (lab, val) in enumerate(bars):
        cx = x0 + slot * i + slot / 2
        h = round((base - top) * val / 100)
        y = base - h
        rects.append(f'<rect class="bar-r" x="{cx-bw/2:.0f}" y="{y}" width="{bw:.0f}" height="{h}"></rect>')
        labs.append(f'<text x="{cx:.0f}" y="186">{esc(lab)}</text>')
        vals.append(f'<text x="{cx:.0f}" y="{y-8}">{val}%</text>')
    return (f'<svg viewBox="0 0 520 200" role="img" aria-label="Biểu đồ: độ phủ trường nguồn theo nhóm thông số">'
            f'<line class="axis" x1="{x0}" y1="{base}" x2="{x1}" y2="{base}"></line>'
            f'<g>{"".join(rects)}</g>'
            f'<g class="glab" text-anchor="middle">{"".join(labs)}</g>'
            f'<g class="gval" text-anchor="middle">{"".join(vals)}</g></svg>')


# ---------- entity chips + inline auto-linking (entity-centric, made visible) ----------
def echip(tag, base=".."):
    lab, t = esc(tag["label"]), ETYPE.get(tag.get("type"), "")
    inner = f'<i>{esc(t)}</i> {lab}'
    if tag.get("slug"):
        return f'<a class="echip" href="{base}/entity/{esc(tag["slug"])}.html">{inner}</a>'
    return f'<span class="echip">{inner}</span>'


def link_map(article, glossary, base=".."):
    """label -> inline HTML. Priority: entity-with-slug (link) > glossary term (def) > entity (no link)."""
    m = {}
    for tg in article.get("entity_tags", []):
        lab = tg["label"]
        if tg.get("slug"):
            m[lab] = f'<a class="eref" href="{base}/entity/{esc(tg["slug"])}.html">{esc(lab)}</a>'
    import re as _re
    for term in article.get("glossary", []):
        if term in m:
            continue
        d = glossary["terms"].get(term, {}).get("vn", "")
        kslug = _re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
        m[term] = f'<a class="kref" href="{base}/knowledge/{kslug}.html" title="{esc(d)}">{esc(term)}</a>'
    for tg in article.get("entity_tags", []):
        lab = tg["label"]
        if lab not in m:
            m[lab] = f'<span class="eref">{esc(lab)}</span>'
    return m


def autolink(text, lmap):
    t = esc(text)
    repl = []
    for label in sorted(lmap, key=len, reverse=True):
        el = esc(label)
        if el in t:
            t = t.replace(el, f"\x00{len(repl)}\x00", 1)
            repl.append(lmap[label])
    for i, h in enumerate(repl):
        t = t.replace(f"\x00{i}\x00", h)
    return t


# ---------- body + boxes ----------
def four_questions(fq):
    rows = "".join(
        f'<div class="q"><span class="lab">{esc(lbl)}</span>'
        f'<span class="ans">{esc(fq.get(key, ""))}</span></div>'
        for key, lbl in FQ)
    return ('<div class="intel" data-audit="intel"><div class="ih">◧ <b>Bản tóm tắt tình báo</b> · bốn câu hỏi</div>'
            f'{rows}</div>')


def render_body(article, site, glossary):
    lmap = link_map(article, glossary)
    figs = {f["id"]: f for f in article.get("figures", [])}
    out = []
    for blk in article["body"]:
        if "p" in blk:
            cls = ' class="dropcap"' if blk.get("dropcap") else ""
            out.append(f'<p{cls}>{autolink(blk["p"], lmap)}</p>')
        elif "h2" in blk:
            n = f'<span class="n">{esc(blk["n"])}</span>' if blk.get("n") else ""
            out.append(f'<h2>{n}{autolink(blk["h2"], lmap)}</h2>')
        elif "pq" in blk:
            pq = blk["pq"]
            out.append(f'<blockquote class="lf-pq">{autolink(pq["text"], lmap)}'
                       f'<span class="src">{esc(pq.get("src", ""))}</span></blockquote>')
        elif "fig" in blk:
            f = figs[blk["fig"]]
            bars, src = figure_bars(f["kind"], site)
            out.append(
                f'<figure class="lf-fig" data-audit="fig"><div class="canvas">{figure_svg(bars)}</div>'
                f'<figcaption class="cap"><span>{esc(f["caption"])} (số liệu thật từ registry)</span>'
                f'<span class="sc">Nguồn: {esc(src)}</span></figcaption></figure>')
    return "\n".join(out)


def related_rail(article, glossary):
    groups = {}
    for tg in article.get("entity_tags", []):
        groups.setdefault(tg.get("type", ""), []).append(tg)
    order = [("technology", "Công nghệ"), ("aircraft", "Mẫu bay"), ("company", "Hãng"), ("country", "Quốc gia")]
    blocks = ""
    for key, lbl in order:
        if groups.get(key):
            chips = "".join(echip(t) for t in groups[key])
            blocks += f'<div class="grp"><div class="gt">{lbl}</div><div class="chips">{chips}</div></div>'
    gl = ""
    for term in article.get("glossary", []):
        d = glossary["terms"].get(term, {}).get("vn", "")
        gl += f'<div class="kdef"><dt>{esc(term)}</dt><dd>{esc(d)}</dd></div>'
    rel = ""
    return (f'<div class="rail" data-audit="rail"><div class="rh">Thực thể liên quan</div>{blocks}</div>'
            + (f'<div class="rail"><div class="rh">Thuật ngữ</div><dl>{gl}</dl></div>' if gl else "")
            + '<div class="rail"><div class="rh">Dữ liệu nguồn</div>'
              '<a class="dlink" href="../reference.html"><span class="d">▦</span> Mở registry · 200 hệ thống</a></div>')


def sources_apparatus(article):
    items = "".join(
        f'<li><span>{s["text"]}</span><span class="tierb tier-{s["tier"].lower()}">Tier {esc(s["tier"])}</span></li>'
        for s in article.get("sources", []))
    if not items:
        return ""
    return (f'<section class="srcs"><div class="sh">Nguồn &amp; chú thích</div><ol>{items}</ol></section>')


def jsonld(article):
    about = [{"@type": "Thing", "name": t["label"]} for t in article.get("entity_tags", [])]
    obj = {"@context": "https://schema.org", "@type": "AnalysisNewsArticle",
           "headline": article["title"], "inLanguage": "vi",
           "author": {"@type": "Person", "name": article.get("author", {}).get("name", "")},
           "about": about, "isAccessibleForFree": True}
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


SPEC_BANNER = ('<div class="smpl"><div class="in"><div class="wrap">'
               '<span>◧ Bản dựng giao diện</span><span style="color:var(--hair-strong)">·</span>'
               '<span><b>Nội dung là chữ mẫu</b>, không phải tin thật — minh hoạ cấu trúc &amp; chuẩn biên tập</span>'
               '</div></div></div>')

NAV = ('<nav class="nav"><a href="../index.html">Tin tức</a><a href="../index.html#analysis" class="on">Phân tích</a>'
       '<a href="../reference.html">Dữ liệu</a><a href="../index.html">Tri thức</a><a href="../reference.html">Review</a></nav>')

ARROW = ('<svg class="ar" viewBox="0 0 24 24" fill="none" aria-hidden="true" style="width:14px;height:14px">'
         '<path d="M4.5 12H16.5M11 6.5L16.5 12L11 17.5" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def render_analysis_page(article, site, glossary):
    a = article
    au = a.get("author", {})
    crumb = (f'<nav class="crumb"><a href="../index.html">Trang chủ</a><span class="sep">›</span>'
             f'<a href="../index.html#analysis">Phân tích</a><span class="sep">›</span><span>{esc(a["slug"])}</span></nav>')
    dtag = '<span class="dtag">▦ Dữ liệu</span>' if a.get("figures") else ""
    head_chips = "".join(echip(t) for t in a.get("entity_tags", []) if t.get("type") == "technology")
    banner = SPEC_BANNER if a.get("sample") else ""
    return f"""<!DOCTYPE html>
<html lang="vi" data-theme="light" data-lang="vn">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(a["title"])} — USR Phân tích</title>
<meta name="description" content="{esc(a["dek"])}">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<link rel="stylesheet" href="../base/newsroom.css">
{jsonld(a)}
</head>
<body>
<div class="prog" id="prog"></div>
{banner}
<header class="nbar"><div class="wrap">
  <a class="wm-name" href="../index.html">Uncrewed Systems Review<small>Vietnam UAV Intelligence</small></a>
  {NAV}
  <div class="nctl"><button class="tg" id="theme" aria-label="Theme"><span data-lang-en>Dark</span><span data-lang-vn>Tối</span></button></div>
</div></header>

<div class="wrap">{crumb}</div>

<header class="lf-head">
  <div class="kicker"><span>Phân tích · {esc(SECTION.get(a["section"], ""))}</span>{dtag}</div>
  <h1 class="lf-h1">{esc(a["title"])}</h1>
  <p class="lf-stand">{esc(a["dek"])}</p>
  <div class="lf-meta">
    <div class="au"><span class="av"></span><span class="nm">{esc(au.get("name",""))}<small>{esc(au.get("role",""))}</small></span></div>
    <span class="dot"></span><span class="mi">{esc(a.get("date",""))}</span>
    <span class="dot"></span><span class="mi">{a.get("reading_min","")} phút đọc</span>
    <span class="dot"></span><span class="chips" style="display:inline-flex">{head_chips}</span>
  </div>
</header>

{four_questions(a["four_questions"])}

<div class="lf-grid">
  <article class="lf-body" data-audit="lfbody">
{render_body(a, site, glossary)}
  </article>
  <aside class="lf-aside">
{related_rail(a, glossary)}
    <div class="rail rel"><div class="rh">Bài liên quan</div>
      <a href="#">Phân loại ECCN và đường đi của giấy phép xuất khẩu</a>
      <a href="#">Vì sao độ phủ nguồn là điểm khởi đầu, không phải điểm yếu</a>
    </div>
  </aside>
</div>

<div class="srcs"><div class="regdiv"><b class="lab">Nguồn</b><span class="ln"></span></div></div>
{sources_apparatus(a)}

<div class="author"><span class="av"></span>
  <div><div class="nm">{esc(au.get("name",""))}</div><div class="bio">{esc(au.get("bio","Tiểu sử là chữ mẫu."))}</div></div>
</div>

<footer class="nfoot"><div class="wrap">
  <span>Uncrewed Systems Review · bản dựng giao diện</span>
  <span>Tuân chuẩn: Quy tắc biên tập · PRD · Memo</span>
</div></footer>

<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  var prog=document.getElementById('prog');
  function up(){{var h=document.documentElement,sc=h.scrollTop||document.body.scrollTop,mx=h.scrollHeight-h.clientHeight;prog.style.width=(mx>0?sc/mx*100:0)+'%';}}
  addEventListener('scroll',up,{{passive:true}});up();
  document.documentElement.dataset.audit="ready";
</script>
</body>
</html>
"""


def analysis_feature(articles, site):
    """Home teaser card for the lead analysis article (Part B side = compact four-questions)."""
    al = [a for a in articles if a["type"] == "analysis"]
    if not al:
        return ""
    a = al[0]
    fq = a["four_questions"]
    qs = "".join(f'<div class="q"><span class="n">{esc(lbl)}</span>'
                 f'<span class="a">{esc(fq.get(key,""))}</span></div>' for key, lbl in FQ)
    return (
        '<article class="feat" data-audit="feat">'
        '<span class="reg tl"></span><span class="reg tr"></span><span class="reg bl"></span><span class="reg br"></span>'
        '<div class="txt"><span class="ghost">01</span>'
        f'<span class="kicker">Phân tích · {esc(SECTION.get(a["section"],""))}</span>'
        f'<h3><a href="analysis/{esc(a["slug"])}.html" style="color:inherit">{esc(a["title"])}</a></h3>'
        f'<p>{esc(a["dek"])}</p>'
        f'<a class="readmore" href="analysis/{esc(a["slug"])}.html"><span>Đọc bài</span>'
        f'<span class="ico">{ARROW}</span></a></div>'
        f'<div class="side">{qs}</div></article>')


def main():
    site = load(SITE)
    glossary = load(GLOSS)
    arts = load(ARTS)["articles"]
    if OUTDIR.exists():
        shutil.rmtree(OUTDIR)
    OUTDIR.mkdir(parents=True)
    n = 0
    for a in arts:
        if a["type"] != "analysis":
            continue
        (OUTDIR / f'{a["slug"]}.html').write_text(render_analysis_page(a, site, glossary))
        n += 1
    print(f"analysis/: {n} long-form page(s) written")


if __name__ == "__main__":
    main()
