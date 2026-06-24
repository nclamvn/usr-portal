#!/usr/bin/env python3
"""TIP-007/A — Newsroom pillar. Renders the hierarchical news-front (lead + secondary + latest,
6-section .tg facets, entity-chips) for the home, and static news/<slug>.html pages.

"Intelligence, not a feed": the front is a hierarchical front page (one lead + a considered second
tier), recency lives in a disciplined "Mới nhất" rail — not an infinite reverse-chron stream
(Utility-over-Virality). Every card carries entity-chips; bodies auto-link entities + glossary —
each article is a node of the entity graph.
"""
import json, pathlib, shutil
from build_reference import esc
from header import header
from build_analysis import (echip, autolink, link_map, SECTION, ARROW, SPEC_BANNER, NAV,
                            related_rail, sources_apparatus, load)

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
GLOSS = ROOT / "content" / "glossary.json"
OUTDIR = ROOT / "news"

SECTIONS_ORDER = ["policy", "market", "tech", "defense", "business", "intl"]


def news_articles(arts):
    return [a for a in arts if a["type"] == "news"]


def _chips(article, base):
    return "".join(echip(t, base) for t in article.get("entity_tags", []))


def news_front(arts, base="."):
    """Part A markup for the home: facets + lead + secondary list + latest rail. base='.' on home."""
    news = news_articles(arts)
    if not news:
        return ""
    lead, secondary, latest = news[0], news[1:4], news[4:] or news[1:]
    facets = ('<button class="tg" aria-pressed="true">Tất cả</button>'
              + "".join(f'<button class="tg" aria-pressed="false">{esc(SECTION[s])}</button>'
                        for s in SECTIONS_ORDER))
    # lead
    dtag = '<span class="dtag">▦ Dữ liệu</span>' if lead.get("data_marker") else ""
    lead_html = (
        '<article class="lead" data-audit="lead">'
        '<div class="plate"><span class="reg tl"></span><span class="reg br"></span>'
        '<span class="pk">Ảnh · nguồn · bản quyền — lưu ở Media Library</span></div>'
        f'<div class="kicker"><span>{esc(SECTION[lead["section"]])}</span>{dtag}</div>'
        f'<h3><a href="{base}/news/{esc(lead["slug"])}.html">{esc(lead["title"])}</a></h3>'
        f'<p class="dek">{esc(lead["dek"])}</p>'
        f'<div class="chips">{_chips(lead, base)}</div>'
        f'<div class="meta-row"><span class="byline"><b>{esc(lead.get("author",{}).get("name",""))}</b>'
        f' · {esc(SECTION[lead["section"]])}<span class="dot"></span> {esc(lead.get("date",""))}</span>'
        f'<span class="byline">{lead.get("reading_min","")} phút đọc</span></div></article>')
    # secondary
    sec_items = ""
    for a in secondary:
        sec_items += (
            '<div class="it">'
            f'<span class="kicker">{esc(SECTION[a["section"]])}</span>'
            f'<h4><a href="{base}/news/{esc(a["slug"])}.html">{esc(a["title"])}</a></h4>'
            f'<div class="row"><div class="chips">{_chips(a, base)}</div>'
            f'<span class="byline">{esc(a.get("date",""))}</span></div></div>')
    # latest rail
    latest_html = ""
    for a in latest:
        latest_html += (f'<a href="{base}/news/{esc(a["slug"])}.html"><span class="t">{esc(a.get("date",""))}</span>'
                        f'{esc(a["title"])}</a>')
    return (
        '<div class="sechead"><div><span class="eyebrow">Tin tức</span>'
        '<h2>Trang nhất, có thứ bậc</h2>'
        '<p class="sub">Một lead rõ, một tầng hai cân nhắc. Recency sống ở rail “Mới nhất”, không phải logic tổ chức.</p></div>'
        f'<div class="nfacets" role="group" aria-label="Lọc theo chuyên mục">{facets}</div></div>'
        '<div class="nr-grid">'
        f'{lead_html}'
        f'<div><div class="seclist">{sec_items}</div>'
        f'<div class="latest"><div class="lh">Mới nhất</div>{latest_html}</div></div>'
        '</div>')


def render_news_page(a, site, glossary):
    au = a.get("author", {})
    banner = SPEC_BANNER if a.get("sample") else ""
    crumb = (f'<nav class="crumb"><a href="../index.html">Trang chủ</a><span class="sep">›</span>'
             f'<a href="../index.html">Tin tức</a><span class="sep">›</span><span>{esc(a["slug"])}</span></nav>')
    lmap = link_map(a, glossary)
    body = "\n".join(f'<p>{autolink(b["p"], lmap)}</p>' for b in a.get("body", []) if "p" in b)
    dtag = '<span class="dtag">▦ Dữ liệu</span>' if a.get("data_marker") else ""
    return f"""<!DOCTYPE html>
<html lang="vi" data-theme="light" data-lang="vn">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(a["title"])} — USR Tin tức</title>
<meta name="description" content="{esc(a["dek"])}">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<link rel="stylesheet" href="../base/newsroom.css">
</head>
<body>
{banner}
{header("../")}

<header class="lf-head">
  <div class="kicker"><span>Tin tức · {esc(SECTION.get(a["section"],""))}</span>{dtag}</div>
  <h1 class="lf-h1">{esc(a["title"])}</h1>
  <p class="lf-stand">{esc(a["dek"])}</p>
  <div class="lf-meta">
    <div class="au"><span class="av"></span><span class="nm">{esc(au.get("name",""))}<small>{esc(au.get("role",""))}</small></span></div>
    <span class="dot"></span><span class="mi">{esc(a.get("date",""))}</span>
    <span class="dot"></span><span class="mi">{a.get("reading_min","")} phút đọc</span>
  </div>
</header>

<div class="lf-grid">
  <article class="lf-body" data-audit="lfbody">
{body}
  </article>
  <aside class="lf-aside">
{related_rail(a, glossary)}
  </aside>
</div>

{sources_apparatus(a)}

<footer class="nfoot"><div class="wrap">
  <span>Uncrewed Systems Review · bản dựng giao diện</span>
  <span>Tuân chuẩn: Quy tắc biên tập · PRD · Memo</span>
</div></footer>

<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));
  document.documentElement.dataset.audit="ready";
</script>
</body>
</html>
"""


def main():
    site = load(SITE)
    glossary = load(GLOSS)
    arts = load(ARTS)["articles"]
    if OUTDIR.exists():
        shutil.rmtree(OUTDIR)
    OUTDIR.mkdir(parents=True)
    n = 0
    for a in news_articles(arts):
        (OUTDIR / f'{a["slug"]}.html').write_text(render_news_page(a, site, glossary))
        n += 1
    print(f"news/: {n} page(s) written")


if __name__ == "__main__":
    main()
