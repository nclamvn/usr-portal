#!/usr/bin/env python3
"""TIP-P1.4 — Taxonomy layer. One real index page per taxonomy TERM (no empty tags, PRD §4.3):
  country/<slug>.html   — every UAV from that country + the manufacturers there
  segment/<slug>.html   — every UAV in that market segment
The manufacturer axis is already served by company/<slug> (P1.1). Pages are a LIVE view over
site-data (zero new data). Slugs match field_row's taxonomy links and the graph's tax:* nodes.
Design-system-of-record only; bilingual (en/vn).
"""
import json, pathlib, shutil, re
from build_reference import friendly, bilingual, esc
from canon import canonical_slug, canonical_name
from nav import nav
from seo import meta, collection_ld

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"


def tslug(v):
    return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


TAX_CSS = """
  .twrap{max-width:820px;margin:0 auto;padding:1.6rem 1.4rem 3rem}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1.4rem}
  .back{font-family:var(--font-mono);font-size:.74rem;color:var(--brass);text-decoration:none;cursor:pointer}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  .thead{border-bottom:1px solid var(--hair);padding-bottom:1rem;margin-bottom:.4rem}
  .thead h1{margin:0}
  .thead .meta{font-size:.8rem;color:var(--muted);margin-top:.3rem;font-family:var(--font-mono)}
  .tsec-h{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:1.9rem 0 .7rem;display:flex;gap:.6rem;align-items:center}
  .tsec-h::after{content:"";flex:1;height:1px;background:var(--hair)}
  .tlist{list-style:none;margin:.3rem 0 0;padding:0;columns:2;column-gap:1.4rem}
  @media(max-width:640px){.tlist{columns:1}}
  .tlist li{font-size:.82rem;padding:.18rem 0;break-inside:avoid}
  .tlist a{color:inherit}
  .note{font-size:.72rem;color:var(--muted);margin-top:1.4rem}
"""


def page(kind, title_html, meta_html, sections, path, plain_title, count):
    body = "".join(
        f'<div class="tsec-h">{h}</div><ul class="tlist">{items}</ul>'
        for h, items in sections)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_html} — USR</title>
{meta(f"{plain_title} — USR", f"{plain_title}: {count} systems in the registry.", path)}
{collection_ld(plain_title, path, count)}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<style>{TAX_CSS}</style>
</head>
<body>
<main class="twrap">
  <div class="topbar">
    {nav("../")}
    <div class="ctrl">
      <button id="lang"><span data-lang-en>VN</span><span data-lang-vn>EN</span></button>
      <button id="theme"><span data-lang-en>Dark</span><span data-lang-vn>Tối</span></button>
    </div>
  </div>
  <header class="thead"><h1>{title_html}</h1><div class="meta">{meta_html}</div></header>
  {body}
  <p class="note">{bilingual(
    "A live index over the registry — every entry links to its full record. Counts are computed at build time.",
    "Chỉ mục sống trên registry — mỗi mục liên kết tới hồ sơ đầy đủ. Số đếm tính lúc build.")}</p>
</main>
<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    uav_name = {e["slug"]: (e.get("name") or {}).get("value") or e["slug"] for e in uavs}

    # group by country and by segment (live)
    countries, segments = {}, {}
    for e in uavs:
        c = (e.get("manufacturer_country") or {}).get("value")
        if c:
            countries.setdefault(c, {"uavs": [], "companies": set()})
            countries[c]["uavs"].append(e["slug"])
            mfr = (e.get("manufacturer") or {}).get("value")
            if mfr:
                countries[c]["companies"].add((canonical_slug(mfr), canonical_name(mfr)))
        s = (e.get("market_segment") or {}).get("value")
        if s:
            segments.setdefault(s, []).append(e["slug"])

    for d in ("country", "segment"):
        p = ROOT / d
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)

    nco = 0
    for c, g in countries.items():
        uav_items = "".join(f'<li><a href="../entity/{esc(s)}.html">{esc(uav_name[s])}</a></li>'
                            for s in sorted(g["uavs"]))
        co_items = "".join(f'<li><a href="../company/{esc(cs)}.html">{esc(cn)}</a></li>'
                           for cs, cn in sorted(g["companies"]))
        meta_line = (f'{len(g["uavs"])} ' + bilingual("systems", "hệ thống")
                     + f' · {len(g["companies"])} ' + bilingual("manufacturers", "nhà sản xuất"))
        html = page("country", esc(c), meta_line, [
            (bilingual("Systems", "Hệ thống"), uav_items),
            (bilingual("Manufacturers", "Nhà sản xuất"), co_items)],
            f"country/{tslug(c)}.html", c, len(g["uavs"]))
        (ROOT / "country" / f"{tslug(c)}.html").write_text(html)
        nco += 1

    nse = 0
    for s, slugs in segments.items():
        uav_items = "".join(f'<li><a href="../entity/{esc(x)}.html">{esc(uav_name[x])}</a></li>'
                            for x in sorted(slugs))
        title = friendly("segment", s, labels)
        plain = labels["segment"].get(s, {}).get("en", s)
        meta_line = f'{len(slugs)} ' + bilingual("systems", "hệ thống")
        html = page("segment", title, meta_line, [(bilingual("Systems", "Hệ thống"), uav_items)],
                    f"segment/{tslug(s)}.html", plain, len(slugs))
        (ROOT / "segment" / f"{tslug(s)}.html").write_text(html)
        nse += 1

    print(f"country/: {nco} pages · segment/: {nse} pages")


if __name__ == "__main__":
    main()
