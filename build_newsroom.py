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
from graphic import lead_graphic
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


def render_index(arts):
    items = ""
    for fm, _ in arts:
        kl_en, kl_vn = TYPE_LABEL.get(fm["type"], (fm["type"], fm["type"]))
        items += (f'<li><a href="news/{esc(fm["slug"])}.html"><span class="kind">{bilingual(kl_en, kl_vn)}</span>'
                  f'<span class="t">{esc(fm["title"])}</span>'
                  f'<span class="dt">{esc(str(fm.get("date", "")))}</span></a></li>')
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Newsroom — USR</title>
{seo_meta("Newsroom — USR", "Objective, sourced articles over the registry: data notes, explainers, profiles and reports.", "news.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{NR_CSS}
  .nidx{{list-style:none;margin:1.4rem 0 0;padding:0}}
  .nidx li{{border-bottom:1px solid var(--hair)}}
  .nidx a{{display:grid;grid-template-columns:7.5rem 1fr auto;gap:1rem;align-items:baseline;padding:.9rem 0;text-decoration:none;color:inherit}}
  .nidx a:hover .t{{color:var(--brass)}}
  .nidx .kind{{font-family:var(--font-mono);font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:var(--brass)}}
  .nidx .t{{font-family:var(--font-head);font-weight:600;font-size:1.02rem;line-height:1.25}}
  .nidx .dt{{font-family:var(--font-mono);font-size:.72rem;color:var(--muted)}}
</style>
</head>
<body>
{header("", "newsroom")}
<main class="nwrap">
  <header class="nh"><div class="kind">{bilingual("Newsroom", "Bài viết")}</div>
    <h1>{bilingual("Objective coverage over the registry", "Bài viết khách quan trên bản đăng ký")}</h1>
    <div class="by">{bilingual("Data notes, explainers, profiles and reports — every figure traces to the registry.", "Ghi chú dữ liệu, giải thích, hồ sơ và báo cáo — mọi con số truy về registry.")}</div></header>
  <ul class="nidx">{items}</ul>
</main>
{footer("")}
<script src="base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


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
