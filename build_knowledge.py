#!/usr/bin/env python3
"""TIP-P3.1 — Knowledge layer (mode E, content-light). One real page per glossary TERM at
knowledge/<slug>.html (PRD §3.4 'no empty tag', §4.4 in-body auto-link target), plus a knowledge
index. Definitions are REAL (content/glossary.json, already written). 'Related' is a LIVE view over
the registry/articles — articles that reference the term, and (for standard terms) systems on that
list. Reuses design-system + bilingual. verify_knowledge proves the term<->page bijection.
"""
import json, pathlib, shutil, re
from build_reference import bilingual, esc
from nav import nav
from header import header
from seo import meta, definedterm_ld

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
GLOSS = ROOT / "content" / "glossary.json"
ARTS = ROOT / "content" / "articles.json"
OUTDIR = ROOT / "knowledge"
INDEX = ROOT / "knowledge.html"

# standard terms that map to a real boolean field -> "systems on this list" is a live, real view
TERM_FIELD = {"Blue UAS": "blue_uas", "NDAA": "ndaa_compliant"}


def tslug(v): return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


KN_CSS = """
  .kwrap{max-width:760px;margin:0 auto;padding:1.2rem 1.4rem 3rem}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1rem}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  .khead{border-bottom:1px solid var(--hair);padding-bottom:1rem;margin-bottom:.4rem}
  .khead .eyebrow{font-family:var(--font-mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--brass)}
  .khead h1{margin:.3rem 0 0;font-family:var(--font-head)}
  .def{font-size:1.05rem;line-height:1.6;color:var(--ink);margin:1.1rem 0 .2rem;max-width:62ch}
  .ksec-h{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:1.9rem 0 .7rem;display:flex;gap:.6rem;align-items:center}
  .ksec-h::after{content:"";flex:1;height:1px;background:var(--hair)}
  .klist{list-style:none;margin:.3rem 0 0;padding:0}
  .klist li{font-size:.86rem;padding:.22rem 0;border-bottom:1px solid var(--hair)}
  .klist a{color:inherit;text-decoration:none}
  .klist a:hover{color:var(--brass)}
  .klist .tag{font-family:var(--font-mono);font-size:.7rem;color:var(--muted);margin-left:.4rem}
  .kidx{list-style:none;margin:0;padding:0}
  .kidx li{padding:.7rem 0;border-bottom:1px solid var(--hair)}
  .kidx a{font-family:var(--font-head);font-weight:600;font-size:1.05rem;color:inherit;text-decoration:none}
  .kidx a:hover{color:var(--brass)}
  .kidx .d{display:block;font-size:.82rem;color:var(--muted);margin-top:.2rem;max-width:64ch}
  .note{font-size:.72rem;color:var(--muted);margin-top:1.6rem}
"""


def shell(title_plain, head_extra, body):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_plain} — USR</title>
{head_extra}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<style>{KN_CSS}</style>
</head>
<body>
{header("../")}
<main class="kwrap">
  {body}
</main>
<script src="../base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


def term_page(term, d, arts, uavs, uav_name):
    slug = tslug(term)
    refs = [a for a in arts if term in a.get("glossary", [])]
    ref_items = "".join(
        f'<li><a href="../{esc(a["type"])}/{esc(a["slug"])}.html">{esc(a["title"])}</a>'
        f'<span class="tag">{esc(a["type"])}</span></li>' for a in refs)
    field = TERM_FIELD.get(term)
    sys_items = ""
    if field:
        on = [e for e in uavs if (e.get(field) or {}).get("value") is True]
        sys_items = "".join(f'<li><a href="../entity/{esc(e["slug"])}.html">{esc(uav_name[e["slug"]])}</a></li>'
                            for e in sorted(on, key=lambda e: e["slug"]))
    secs = ""
    if ref_items:
        secs += f'<div class="ksec-h">{bilingual("Referenced in", "Nhắc đến trong")}</div><ul class="klist">{ref_items}</ul>'
    if sys_items:
        secs += f'<div class="ksec-h">{bilingual("Systems on this list", "Hệ thống trong danh sách")}</div><ul class="klist">{sys_items}</ul>'
    head = (meta(f"{esc(term)} — USR", d["en"], f"knowledge/{slug}.html")
            + definedterm_ld(term, d["en"], f"knowledge/{slug}.html"))
    body = f"""<header class="khead"><span class="eyebrow">{bilingual("Knowledge", "Thuật ngữ")}</span><h1>{esc(term)}</h1></header>
  <p class="def"><span data-lang-en>{esc(d["en"])}</span><span data-lang-vn>{esc(d["vn"])}</span></p>
  {secs}
  <p class="note">{bilingual("A reference definition; related items are a live view over the registry.",
                             "Định nghĩa tham chiếu; mục liên quan là chỉ mục sống trên registry.")}</p>"""
    return shell(esc(term), head, body)


def index_page(terms):
    items = "".join(
        f'<li><a href="knowledge/{tslug(t)}.html">{esc(t)}</a>'
        f'<span class="d"><span data-lang-en>{esc(d["en"])}</span><span data-lang-vn>{esc(d["vn"])}</span></span></li>'
        for t, d in sorted(terms.items()))
    head = (meta("Knowledge — USR", "Reference definitions for UAV terms and standards.", "knowledge.html"))
    # index sits at root: nav prefix "" and ../ -> ./ for assets; reuse shell with root tweaks
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knowledge — USR</title>
{head}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{KN_CSS}</style>
</head>
<body>
{header("", "knowledge")}
<main class="kwrap">
  <header class="khead"><span class="eyebrow">{bilingual("Knowledge", "Thuật ngữ")}</span><h1>{bilingual("Glossary", "Thuật ngữ")}</h1></header>
  <ul class="kidx">{items}</ul>
</main>
<script src="base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


def main():
    terms = json.loads(GLOSS.read_bytes())["terms"]
    arts = json.loads(ARTS.read_bytes())["articles"]
    site = json.loads(SITE.read_bytes())
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    uav_name = {e["slug"]: (e.get("name") or {}).get("value") or e["slug"] for e in uavs}
    if OUTDIR.exists():
        shutil.rmtree(OUTDIR)
    OUTDIR.mkdir(parents=True)
    for term, d in terms.items():
        (OUTDIR / f"{tslug(term)}.html").write_text(term_page(term, d, arts, uavs, uav_name))
    INDEX.write_text(index_page(terms))
    print(f"knowledge/: {len(terms)} term pages + index")


if __name__ == "__main__":
    main()
