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

NR_CSS = """
  .nwrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3.5rem}
  .nwrap>*{max-width:var(--w-read)}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1.2rem}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  .nh .kind{font-family:var(--font-mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--brass)}
  .nh h1{font-family:var(--font-head);font-weight:700;font-size:clamp(26px,3.6vw,38px);line-height:1.12;letter-spacing:-.01em;margin:.4rem 0 0}
  .nh .by{font-family:var(--font-mono);font-size:.74rem;color:var(--muted);margin-top:.7rem;border-top:1px solid var(--hair);padding-top:.7rem}
  .ntag{display:flex;flex-wrap:wrap;gap:.4rem;margin:1rem 0 0}
  .echip{font-family:var(--font-mono);font-size:10px;letter-spacing:.04em;color:var(--ink-soft);border:1px solid var(--hair-strong);border-radius:3px;padding:.1rem .45rem;text-decoration:none}
  .echip:hover{border-color:var(--brass);color:var(--brass)} .echip i{color:var(--muted);font-style:normal}
  .nbody{font-family:var(--serif);font-size:1.06rem;line-height:1.74;color:var(--ink);margin-top:1.6rem}
  .nbody p{margin:0 0 1.1rem;max-width:66ch} .nbody h2{font-family:var(--font-head);font-size:1.3rem;margin:2rem 0 .8rem}
  .nbody a.kref{color:inherit;border-bottom:1px dotted var(--brass)}
  .srcs{margin-top:2.4rem;border-top:1px solid var(--hair);padding-top:1rem}
  .srcs h3{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 .6rem}
  .srcs li{font-family:var(--font-mono);font-size:.74rem;color:var(--ink-soft);margin:.35rem 0;overflow-wrap:anywhere;list-style:none}
  .srcs .tb{display:inline-block;border:1px solid var(--brass);color:var(--brass);border-radius:3px;padding:0 .3em;margin-right:.4em}
"""


def render(fm, body, site, glossary):
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

    chips = ""
    for tag in fm.get("entity_tags") or []:
        typ, _, s = tag.partition(":")
        d = {"company": "company", "uav": "entity", "knowledge": "knowledge"}.get(typ)
        if d:
            chips += f'<a class="echip" href="../{d}/{esc(s)}.html"><i>{esc(typ)}</i> {esc(s)}</a>'
    chips = f'<div class="ntag">{chips}</div>' if chips else ""

    srcs = "".join(f'<li><span class="tb">{esc(s.get("tier", "—"))}</span>{esc(s.get("claim", ""))} — {esc(s.get("url", ""))}</li>'
                   for s in fm.get("sources") or [])
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
<main class="nwrap">
  <header class="nh"><div class="kind">{bilingual(kl_en, kl_vn)}</div><h1>{esc(fm["title"])}</h1>
    <div class="by">{esc(fm.get("author", "Ban Dữ liệu USR"))} · {esc(str(fm.get("date", "")))} · {bilingual("data desk", "ban dữ liệu")}</div>
    {chips}</header>
  <div class="nbody">{body_html}</div>
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
    for fm, body in arts:
        (OUTDIR / f'{fm["slug"]}.html').write_text(render(fm, body, site, glossary))
    (ROOT / "news.html").write_text(render_index(arts))
    print(f"newsroom: {len(arts)} objective articles + index (news.html)")


if __name__ == "__main__":
    main()
