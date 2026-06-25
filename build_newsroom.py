#!/usr/bin/env python3
"""TIP-P3.3 — Newsroom (mode E, AI-authorable). Renders the objective articles authored under
content/newsroom-authoring.md (the system prompt): data-note / explainer / company-profile /
uav-profile / data-report. Source = content/newsroom/*.md (yaml frontmatter + markdown body).
Numbers in prose are figure-LIVE: each declared figure {token,trace} recomputes from site-data
(verify_newsroom proves no drift). entity_tags 'type:slug' link to real pages; glossary terms in
body auto-link to /knowledge. Opinion/analysis are NOT here — they require a human author.
"""
import json, pathlib, re, shutil, html
import yaml
from build_reference import bilingual, esc
from footer import footer
from nav import nav
from header import header
from pagenav import pagenav
from graphic import lead_graphic, feed_figure, figure_is_data
import urllib.parse
from seo import meta as seo_meta

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "content" / "newsroom"
SITE = ROOT / "out" / "site-data.json"
GLOSS = ROOT / "content" / "glossary.json"
OUTDIR = ROOT / "news"
def tslug(v): return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")

AI_TYPES = {"data-note", "explainer", "knowledge", "company-profile", "uav-profile", "data-report"}
SOURCED = ["legal_name", "founded_year", "hq_country", "hq_city", "hq_address", "website",
           "founder", "contact_email", "contact_phone", "parent_company", "stock"]


def trace_value(trace, site):
    """Recompute a figure token's value LIVE from site-data. Single source of truth."""
    from canon import canonical_slug
    ents = site["entities"]
    uavs = [e for e in ents if e.get("entity_type", "uav") == "uav"]
    t = trace.strip()
    if t == "count(entity_type=uav)": return len(uavs)
    if t == "count(entity_type=company)": return sum(1 for e in ents if e.get("entity_type") == "company")
    if t == "distinct(country)": return len({(e.get("manufacturer_country") or {}).get("value") for e in uavs if (e.get("manufacturer_country") or {}).get("value")})
    if t == "distinct(segment)": return len({(e.get("market_segment") or {}).get("value") for e in uavs if (e.get("market_segment") or {}).get("value")})
    if t == "aggregates.spec_fill_rate":
        f = site["aggregates"]["spec_fill_rate"]; p = sum(d["present"] for d in f.values()); tot = sum(d["total"] for d in f.values())
        return round(100 * p / tot) if tot else 0
    if t == "count(blue_uas=true)": return sum(1 for e in uavs if (e.get("blue_uas") or {}).get("value") is True)
    if t == "count(ndaa=true)": return sum(1 for e in uavs if (e.get("ndaa_compliant") or {}).get("value") is True)
    if t.startswith("count(uav where manufacturer="):
        mk = t[len("count(uav where manufacturer="):-1]
        return sum(1 for e in uavs if canonical_slug((e.get("manufacturer") or {}).get("value")) == mk)
    if t == "rank(count(uav) group by manufacturer)":
        from collections import Counter
        c = Counter(canonical_slug((e.get("manufacturer") or {}).get("value")) for e in uavs if (e.get("manufacturer") or {}).get("value"))
        return c.most_common(1)[0][1] if c else 0
    if t == "count(company with >=1 sourced field)":
        return sum(1 for e in ents if e.get("entity_type") == "company" and any(isinstance(e.get(k), dict) for k in SOURCED))
    raise ValueError("unknown trace: %s" % trace)


def parse(md):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", md, re.S)
    fm = yaml.safe_load(m.group(1))
    body = m.group(2).strip()
    return fm, body


TYPE_LABEL = {"data-note": ("Data note", "Ghi chú dữ liệu"), "explainer": ("Explainer", "Giải thích"),
              "company-profile": ("Profile", "Hồ sơ"), "uav-profile": ("Profile", "Hồ sơ"),
              "data-report": ("Data report", "Báo cáo dữ liệu")}

# bilingual label for each live figure token surfaced in the data-dossier rail (TIP-UX2.3)
FIG_LABEL = {"total_uav": ("systems", "hệ thống"), "total_company": ("companies", "doanh nghiệp"),
             "total_country": ("countries", "quốc gia"), "total_segment": ("segments", "nhóm ứng dụng"),
             "spec_coverage": ("spec coverage", "độ phủ spec"), "blue_uas": ("Blue UAS", "Blue UAS"),
             "ndaa": ("NDAA compliant", "tuân thủ NDAA")}


def data_rail(fm, site):
    """Sticky right rail — every panel from the article's OWN real data (zero-fab, honest-null:
    a panel renders only when its data exists). Figures recompute LIVE via trace_value."""
    panels = []
    # 1) live key figures (same source of truth as the body — verify_newsroom gates traceability)
    rows = ""
    for fig in fm.get("figures") or []:
        tok = fig.get("token", "")
        try:
            val = trace_value(fig["trace"], site)
        except Exception:
            continue
        en, vn = FIG_LABEL.get(tok, (tok, tok))
        sval = f"{val}%" if tok == "spec_coverage" else str(val)
        rows += (f'<div class="rstat"><b class="rv">{esc(sval)}</b>'
                 f'<span class="rk">{bilingual(en, vn)}</span></div>')
    if rows:
        panels.append(f'<div class="rpanel"><div class="rh">{bilingual("Key figures", "Số liệu")}</div>{rows}</div>')
    # 2) related entities (chips → real registry/company/knowledge pages)
    chips = ""
    for tag in fm.get("entity_tags") or []:
        typ, _, s = tag.partition(":")
        d = {"company": "company", "uav": "entity", "knowledge": "knowledge"}.get(typ)
        if d:
            chips += f'<a class="echip" href="../{d}/{esc(s)}.html"><i>{esc(typ)}</i> {esc(s)}</a>'
    if chips:
        panels.append(f'<div class="rpanel"><div class="rh">{bilingual("Entities", "Thực thể")}</div>'
                      f'<div class="rchips">{chips}</div></div>')
    # 3) sources at a glance (tier + claim; full list with URLs stays at the article foot)
    srows = "".join(f'<div class="rsrc"><span class="tb">{esc(s.get("tier", "—"))}</span>{esc(s.get("claim", ""))}</div>'
                    for s in fm.get("sources") or [])
    if srows:
        panels.append(f'<div class="rpanel"><div class="rh">{bilingual("Sources", "Nguồn")}</div>{srows}</div>')
    # 4) open data (always) — registry count is live
    n_uav = trace_value("count(entity_type=uav)", site)
    en, vn = TYPE_LABEL.get(fm["type"], (fm["type"], fm["type"]))
    panels.append(
        f'<div class="rpanel"><div class="rh">{bilingual("Open data", "Mở dữ-liệu")}</div>'
        f'<a class="rlink" href="../reference.html"><span class="d">▦</span> '
        f'{bilingual("Open registry", "Mở registry")} · {n_uav} {bilingual("systems", "hệ thống")}</a>'
        f'<div class="rmeta">{bilingual(en, vn)} · {esc(str(fm.get("date", "")))}</div></div>')
    return '<aside class="nrail" data-audit="nrail">' + "".join(panels) + '</aside>'

NR_CSS = """
  .nwrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3.5rem}
  .nh{max-width:var(--w-read)}
  .nh .kind{font-family:var(--font-mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--brass)}
  .nh h1{font-family:var(--font-head);font-weight:700;font-size:clamp(26px,3.6vw,38px);line-height:1.12;letter-spacing:-.01em;margin:.4rem 0 0}
  .nh .by{font-family:var(--font-mono);font-size:.74rem;color:var(--muted);margin-top:.7rem;border-top:1px solid var(--hair);padding-top:.7rem}
  .nfig{max-width:var(--w-read);margin:1.4rem 0 0}
  .nfig img{width:100%;height:auto;display:block;border:1px solid var(--hair)}
  .nfig-graphic svg{width:100%;height:auto;display:block}
  .nfig figcaption{font-family:var(--font-mono);font-size:10px;letter-spacing:.04em;color:var(--muted);margin-top:.5rem;display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;line-height:1.5}
  .nfig .lic{color:var(--brass);border:1px solid var(--brass);border-radius:3px;padding:0 .35em;text-transform:uppercase;letter-spacing:.06em;white-space:nowrap}
  .echip{font-family:var(--font-mono);font-size:10px;letter-spacing:.04em;color:var(--ink-soft);border:1px solid var(--hair-strong);border-radius:3px;padding:.1rem .45rem;text-decoration:none}
  .echip:hover{border-color:var(--brass);color:var(--brass)} .echip i{color:var(--muted);font-style:normal}
  /* two-column editorial layout — reading column + sticky data-dossier rail (TIP-UX2.3) */
  .narticle{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:52px;align-items:start;margin-top:1.6rem}
  @media(max-width:980px){.narticle{grid-template-columns:1fr;gap:32px}}
  .nbody{font-family:var(--serif);font-size:1.06rem;line-height:1.74;color:var(--ink)}
  .nbody p{margin:0 0 1.1rem;max-width:66ch} .nbody h2{font-family:var(--font-head);font-size:1.3rem;margin:2rem 0 .8rem}
  .nbody a.kref{color:inherit;border-bottom:1px dotted var(--brass)}
  .nrail{position:sticky;top:90px;display:flex;flex-direction:column;gap:1.4rem}
  @media(max-width:980px){.nrail{position:static}}
  .rpanel{border-top:1px solid var(--hair-strong);padding-top:.9rem}
  .rh{font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:.7rem}
  .rstat{display:flex;align-items:baseline;gap:.7rem;padding:.22rem 0}
  .rstat .rv{font-family:var(--font-head);font-weight:600;font-size:1.5rem;line-height:1;letter-spacing:-.02em;color:var(--ink);font-variant-numeric:tabular-nums;min-width:3.2ch;text-align:right}
  .rstat .rk{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
  .rchips{display:flex;flex-wrap:wrap;gap:.4rem}
  .rsrc{font-family:var(--font-mono);font-size:.72rem;color:var(--ink-soft);margin:.32rem 0;overflow-wrap:anywhere;line-height:1.5}
  .tb{display:inline-block;border:1px solid var(--brass);color:var(--brass);border-radius:3px;padding:0 .3em;margin-right:.4em}
  .rlink{display:inline-flex;align-items:center;gap:.45rem;font-family:var(--font-mono);font-size:.74rem;letter-spacing:.04em;color:var(--brass);text-decoration:none}
  .rlink:hover{color:var(--brass-bright)} .rlink .d{font-size:.9rem}
  .rmeta{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);margin-top:.6rem}
  .srcs{margin-top:2.4rem;border-top:1px solid var(--hair);padding-top:1rem;max-width:var(--w-read)}
  .srcs h3{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 .6rem}
  .srcs ul{margin:0;padding:0;list-style:none}
  .srcs li{font-family:var(--font-mono);font-size:.74rem;color:var(--ink-soft);margin:.35rem 0;overflow-wrap:anywhere;list-style:none}
"""


def render(fm, body, site, glossary, prev=None, next=None):
    slug = fm["slug"]
    terms = list(glossary["terms"])
    # markdown body -> blocks; first '# ' is the title (skip)
    blocks = []
    for para in [p.strip() for p in body.split("\n\n") if p.strip()]:
        if para.startswith("# "):
            continue
        if para.startswith("## "):
            blocks.append(("h2", para[3:].strip())); continue
        blocks.append(("p", " ".join(para.split("\n"))))

    def autolink(text):
        t = esc(text)
        for term in sorted(terms, key=len, reverse=True):
            if term in t:
                t = t.replace(term, f'<a class="kref" href="../knowledge/{tslug(term)}.html">{term}</a>', 1)
        return t
    body_html = "".join(f"<h2>{esc(x)}</h2>" if k == "h2" else f"<p>{autolink(x)}</p>" for k, x in blocks)

    rail = data_rail(fm, site)

    srcs = "".join(f'<li><span class="tb">{esc(s.get("tier", "—"))}</span>{esc(s.get("claim", ""))} — {esc(s.get("url", ""))}</li>'
                   for s in fm.get("sources") or [])
    # lead — a REAL source photo if present (credit + license; empty license => no badge), otherwise a
    # data-driven ORIGINAL graphic generated per-article by the graphic core (no shared/repeated file).
    img = fm.get("image") or {}
    if img.get("src"):
        lic = img.get("license", "")
        lic_html = f' <span class="lic">{esc(lic)}</span>' if lic else ""
        lead_fig = (f'<figure class="nfig"><img src="{esc(img["src"])}" alt="{esc(fm.get("title", ""))}" loading="lazy">'
                    f'<figcaption>{esc(img.get("credit", ""))}{lic_html}</figcaption></figure>')
    else:
        lead_fig = lead_graphic(fm)
    kl_en, kl_vn = TYPE_LABEL.get(fm["type"], (fm["type"], fm["type"]))
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(fm["title"])} — USR</title>
{seo_meta(esc(fm["title"]) + " — USR", esc(fm["title"]), f"news/{slug}.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<style>{NR_CSS}</style>
</head>
<body>
{header("../")}
{pagenav(prev, next)}
<main class="nwrap">
  <header class="nh"><div class="kind">{bilingual(kl_en, kl_vn)}</div><h1>{esc(fm["title"])}</h1>
    <div class="by">{esc(fm.get("author", "Ban Dữ liệu USR"))} · {esc(str(fm.get("date", "")))} · {bilingual("data desk", "ban dữ liệu")}</div></header>
  {lead_fig}
  <div class="narticle">
    <div class="nbody">{body_html}</div>
    {rail}
  </div>
  <div class="srcs"><h3>{bilingual("Sources", "Nguồn")}</h3><ul>{srcs}</ul></div>
</main>
{footer("../")}
<script src="../base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


def load_articles():
    """[(fm, body)] for every newsroom .md, newest first. Shared with the index + entity cross-link."""
    out = []
    for f in sorted(SRC.glob("*.md")):
        fm, body = parse(f.read_text())
        fm.setdefault("slug", f.stem)
        out.append((fm, body))
    out.sort(key=lambda x: str(x[0].get("date", "")), reverse=True)
    return out


def articles_for(tag):
    """Newsroom article metas (newest first) whose entity_tags include `tag` (e.g. 'company:dji')."""
    return [fm for fm, _ in load_articles() if tag in (fm.get("entity_tags") or [])]



REGION = {"lae-cn": ("China", "Trung Quốc"), "lae-trung-quoc": ("China", "Trung Quốc"),
          "lae-tg": ("World", "Thế giới"), "lae-the-gioi": ("World", "Thế giới"),
          "lae-vn": ("Vietnam", "Việt Nam")}


def _region(slug):
    for pre, (en, vn) in REGION.items():
        if slug.startswith(pre):
            return en, vn
    return None, None


def _src(fm):
    """First source as a provenance label: host + tier. None if the article carries no source."""
    srcs = fm.get("sources") or []
    if not srcs:
        return None
    s0 = srcs[0]
    host = urllib.parse.urlparse(s0.get("url", "")).netloc.replace("www.", "") or "—"
    return {"host": host, "tier": str(s0.get("tier", "?")), "n": len(srcs)}


def _date_short(d):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(d or ""))
    return f"{m.group(3)}.{m.group(2)}" if m else str(d or "")


def _status_tag(fm):
    g = fm.get("graphic") or {}
    st = g.get("status")
    if not st:
        return ""
    low = str(st).lower()
    is_t = bool(g.get("target")) or any(k in low for k in ("mục tiêu", "dự kiến", "kế hoạch"))
    cls = "tag-target" if is_t else "tag-actual"
    return f'<span class="{cls}">{esc(st)}</span>'


def _kicker(fm):
    kl_en, kl_vn = TYPE_LABEL.get(fm["type"], (fm["type"], fm["type"]))
    ren, rvn = _region(fm["slug"])
    if ren:
        return bilingual(f"{kl_en} · {ren}", f"{kl_vn} · {rvn}")
    return bilingual(kl_en, kl_vn)


def _meta(fm):
    """Source-first meta line: SOURCE · TIER · [target/actual] · DATE — all from the article's own data."""
    s = _src(fm)
    out = ""
    if s:
        tcls = "tier" if s["tier"].startswith("A") else "tier bb"
        out += (f'<span class="src">{bilingual("Source", "Nguồn")} {esc(s["host"])}</span>'
                f'<span class="{tcls}">✓{esc(s["tier"])}</span>')
    out += _status_tag(fm)
    out += f'<span class="mdate">{esc(_date_short(fm.get("date")))}</span>'
    return out


def _figcap(fm):
    """Caption under a figure. Data-figure → real source+tier. Honest-null glyph → 'minh hoạ', no source claim."""
    g = fm.get("graphic") or {}
    if figure_is_data(fm):
        s = _src(fm)
        cap = esc(g.get("caption", "")) if g.get("kind") == "chart" else ""
        prov = f'{bilingual("Source","Nguồn")} {esc(s["host"])} · ✓{esc(s["tier"])}' if s else ""
        return cap, prov
    kl_en, kl_vn = TYPE_LABEL.get(fm["type"], (fm["type"], fm["type"]))
    return "", bilingual(f"Illustration · {kl_en}", f"Minh hoạ · {kl_vn}")


def _figttl(fm):
    g = fm.get("graphic") or {}
    if g.get("kind") == "chart":
        return esc(g.get("title", ""))
    if g.get("kind") == "count":
        return esc(g.get("label", ""))
    if g.get("kind") == "compare":
        return bilingual("Comparison", "So sánh")
    return bilingual("Classification", "Phân loại")


def _weight(fb):
    fm = fb[0]
    k = (fm.get("graphic") or {}).get("kind")
    w = 100 if k == "chart" else 60 if k in ("count", "compare") else 0
    s = _src(fm)
    if s and s["tier"].startswith("A"):
        w += 10
    return (w, str(fm.get("date", "")))


def _lead_html(fm):
    cap, prov = _figcap(fm)
    return (
        '<article class="lead">'
        '<div class="lead-body">'
        f'<span class="kicker">{_kicker(fm)}</span>'
        f'<h2><a href="news/{esc(fm["slug"])}.html">{esc(fm["title"])}</a></h2>'
        + (f'<p class="dek">{esc(fm.get("dek"))}</p>' if fm.get("dek") else "")
        + f'<div class="meta">{_meta(fm)}</div>'
        '</div>'
        '<aside class="figure">'
        f'<div class="figttl">{_figttl(fm)}</div>'
        f'{feed_figure(fm, "lead")}'
        f'<div class="cap"><span>{cap}</span><span class="src">{prov}</span></div>'
        '</aside></article>')


def _sec_html(fm, idx):
    cap, prov = _figcap(fm)
    return (
        '<article class="sec">'
        f'<a class="thumb" href="news/{esc(fm["slug"])}.html">{feed_figure(fm, "thumb")}'
        f'<span class="tlbl">{prov or cap}</span></a>'
        f'<span class="kicker">{_kicker(fm)}</span>'
        f'<h3><span class="idx">{idx:02d}</span><a href="news/{esc(fm["slug"])}.html">{esc(fm["title"])}</a></h3>'
        f'<div class="meta">{_meta(fm)}</div></article>')


def _brief_html(fm):
    return (
        '<article class="brief">'
        f'<a class="bthumb" href="news/{esc(fm["slug"])}.html">{feed_figure(fm, "brief")}</a>'
        '<div class="brief-main">'
        f'<div class="brief-top"><span class="k">{_kicker(fm)}</span>'
        f'<span class="bt">{esc(_date_short(fm.get("date")))}</span></div>'
        f'<h4><a href="news/{esc(fm["slug"])}.html">{esc(fm["title"])}</a></h4>'
        f'<div class="meta">{_meta(fm)}</div></div></article>')


STREAM_N = 6   # the "Latest" rail size — tuned so the rail ≈ lead+secondary height (no column void);
               # the REST auto-fill the full-width "More" tier (grows with the registry, never hardcoded)


def _more_html(fm):
    """A dense river row — kicker · headline · source+tier · date · small glyph. List, not figure
    (preserves the lead/secondary > More hierarchy). Carries the same provenance as every other item."""
    return (
        '<article class="mrow">'
        f'<a class="mg" href="news/{esc(fm["slug"])}.html">{feed_figure(fm, "brief")}</a>'
        '<div class="m-main">'
        f'<span class="kicker">{_kicker(fm)}</span>'
        f'<h4><a href="news/{esc(fm["slug"])}.html">{esc(fm["title"])}</a></h4>'
        f'<div class="meta">{_meta(fm)}</div></div></article>')


def render_index(arts):
    ranked = sorted(arts, key=_weight, reverse=True)
    lead_fm = ranked[0][0]
    sec_fms = [fb[0] for fb in ranked[1:3]]
    chosen = {lead_fm["slug"], *(f["slug"] for f in sec_fms)}
    rest = [fm for fm, _ in arts if fm["slug"] not in chosen]            # remainder, newest-first
    stream = rest[:STREAM_N]                                            # the "Latest" rail
    more = rest[STREAM_N:]                                              # AUTO-FILL the tail: all that is left
    updated = max((str(fm.get("date", "")) for fm, _ in arts if re.match(r"\d{4}-", str(fm.get("date", "")))),
                  default="")
    lead_html = _lead_html(lead_fm)
    sec_html = "".join(_sec_html(fm, i + 2) for i, fm in enumerate(sec_fms))
    brief_html = "".join(_brief_html(fm) for fm in stream)
    more_html = "".join(_more_html(fm) for fm in more)
    more_block = (f'<section class="more"><div class="more-h">'
                  f'<span>{bilingual("More from the record", "Thêm trong hồ sơ")}</span>'
                  f'<span class="live">{len(more)}</span></div>'
                  f'<div class="more-grid">{more_html}</div></section>') if more else ""
    n = len(arts)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Newsroom — USR</title>
{seo_meta("Newsroom — USR", "Objective, sourced coverage over the registry — every item carries its source, every figure is generated from data.", "news.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
</head>
<body>
{header("", "newsroom")}
<main class="nfeed">
  <div class="mast">
    <div class="mast-l"><span class="mast-no">01</span><h1>{bilingual("Newsroom", "Bài viết")}</h1></div>
    <span class="mast-date">{bilingual("Low-altitude economy record", "Bản ghi kinh tế tầm thấp")}</span>
  </div>
  <div class="subrule">
    <span>{bilingual("Updated", "Cập nhật")} {esc(_date_short(updated))}</span>
    <span>{bilingual(f"{n} articles · every item is sourced · every figure is generated from data",
                     f"{n} bài · mỗi mục mang nguồn · mỗi hình sinh từ dữ liệu")}</span>
  </div>
  <div class="frame">
    <div class="col-lead">
      {lead_html}
      <div class="secondary">{sec_html}</div>
    </div>
    <div class="col-stream">
      <div class="stream-h"><span>{bilingual("Latest", "Mới nhất")}</span><span class="live">{bilingual("Record stream", "Dòng hồ sơ")}</span></div>
      {brief_html}
    </div>
  </div>
  {more_block}
  <div class="allcta">
    <span class="lbl">{bilingual("Every item traces to a source; figures are drawn from the registry, never borrowed.",
                                 "Mỗi mục truy về một nguồn; hình vẽ từ registry, không mượn ảnh.")}</span>
    <a class="btn" href="reference.html">{bilingual("Browse the registry", "Duyệt registry")} <span class="arr">→</span></a>
  </div>
</main>
{footer("")}
<script src="base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


def homepage_news_block(prefix=""):
    """Compact newsroom frame for the homepage: one lead (with figure) + three side items + link.
    Same source-first treatment; figures generated from data. Articles auto-pick newest/strongest."""
    arts = load_articles()
    if not arts:
        return ""
    ranked = sorted(arts, key=_weight, reverse=True)
    lead_fm = ranked[0][0]
    side = [fb[0] for fb in ranked[1:5]]   # fill the column beside the lead (avoid empty space)
    items = "".join(
        f'<article class="hl-item"><span class="kicker">{_kicker(fm)}</span>'
        f'<h4><a href="{prefix}news/{esc(fm["slug"])}.html">{esc(fm["title"])}</a></h4>'
        f'<div class="meta">{_meta(fm)}</div></article>' for fm in side)
    return (f'<div class="nfeed nfeed-mini">'
            f'<div class="frame"><div class="col-lead">{_lead_html(lead_fm)}</div>'
            f'<div class="col-side">{items}</div></div></div>')


def main():
    site = json.loads(SITE.read_bytes())
    glossary = json.loads(GLOSS.read_bytes())
    OUTDIR.mkdir(parents=True, exist_ok=True)
    arts = load_articles()
    for i, (fm, body) in enumerate(arts):
        prev = f'{arts[i-1][0]["slug"]}.html' if i > 0 else None            # edge prev/next (newest-first order)
        nxt = f'{arts[i+1][0]["slug"]}.html' if i < len(arts) - 1 else None
        (OUTDIR / f'{fm["slug"]}.html').write_text(render(fm, body, site, glossary, prev=prev, next=nxt))
    (ROOT / "news.html").write_text(render_index(arts))
    print(f"newsroom: {len(arts)} objective articles + index (news.html)")


if __name__ == "__main__":
    main()
