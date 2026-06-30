#!/usr/bin/env python3
"""TIP-P2.1 — Search layer. Multi-type, build-time index over the SAME node universe the graph holds
(uav · company · country · segment), rendered client-side (no backend, no heavy lib). search-index.json
is a LIVE projection of site-data — one source of truth; verify_search proves no drift / no orphan /
no missing and that every hit's url resolves. Reuses the Compare pattern (data-as-files + client).
"""
import json, pathlib, re
from build_reference import friendly, bilingual, esc
from footer import footer
from nav import nav
from header import header
from seo import meta as seo_meta

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
OUT = ROOT / "out" / "search-index.json"
PAGE = ROOT / "search.html"

TYPE_LABELS = {
    "uav": {"en": "System", "vn": "Hệ thống"},
    "company": {"en": "Manufacturer", "vn": "Nhà sản xuất"},
    "country": {"en": "Country", "vn": "Quốc gia"},
    "segment": {"en": "Segment", "vn": "Phân khúc"},
}


def tslug(v):
    return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


def build_index(site):
    labels = site["labels"]
    ents = site["entities"]
    uavs = [e for e in ents if e.get("entity_type", "uav") == "uav"]
    companies = [e for e in ents if e.get("entity_type") == "company"]
    entries = []

    for e in uavs:
        name = (e.get("name") or {}).get("value") or e["slug"]
        maker = (e.get("manufacturer") or {}).get("value") or ""
        country = (e.get("manufacturer_country") or {}).get("value") or ""
        seg = (e.get("market_segment") or {}).get("value")
        seg_l = labels["segment"].get(seg, {"en": seg or "", "vn": seg or ""})
        terms = " ".join([name, maker, country, seg_l["en"], seg_l["vn"]]).lower()
        entries.append({"id": e["slug"], "type": "uav", "label_en": name, "label_vn": name,
                        "sub_en": maker, "sub_vn": maker, "url": "uav/%s.html" % e["slug"], "terms": terms})

    for e in companies:
        name = e.get("name") or e["slug"]
        n = (e.get("rollup") or {}).get("uav_count", 0)
        entries.append({"id": e["slug"], "type": "company", "label_en": name, "label_vn": name,
                        "sub_en": "%d systems" % n, "sub_vn": "%d hệ thống" % n,
                        "url": "company/%s.html" % e["slug"], "terms": name.lower()})

    # country + segment terms (live counts over uavs)
    cc, sc = {}, {}
    for e in uavs:
        c = (e.get("manufacturer_country") or {}).get("value")
        if c:
            cc[c] = cc.get(c, 0) + 1
        s = (e.get("market_segment") or {}).get("value")
        if s:
            sc[s] = sc.get(s, 0) + 1
    for c, n in cc.items():
        entries.append({"id": tslug(c), "type": "country", "label_en": c, "label_vn": c,
                        "sub_en": "%d systems" % n, "sub_vn": "%d hệ thống" % n,
                        "url": "country/%s.html" % tslug(c), "terms": c.lower()})
    for s, n in sc.items():
        sl = labels["segment"].get(s, {"en": s, "vn": s})
        entries.append({"id": tslug(s), "type": "segment", "label_en": sl["en"], "label_vn": sl["vn"],
                        "sub_en": "%d systems" % n, "sub_vn": "%d hệ thống" % n,
                        "url": "segment/%s.html" % tslug(s), "terms": (sl["en"] + " " + sl["vn"]).lower()})

    entries.sort(key=lambda x: (x["type"], x["id"]))
    return {"schema": "search-index/1", "types": TYPE_LABELS, "entries": entries}


SEARCH_CSS = """
  .swrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3rem}
  .swrap>*{max-width:var(--w-read)}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1.2rem}
  .back{font-family:var(--font-mono);font-size:.74rem;color:var(--brass);text-decoration:none}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  h1{margin:0 0 .8rem}
  #q{width:100%;background:transparent;border:1px solid var(--hair-strong);border-radius:var(--radius);padding:.6rem .8rem;font-family:var(--font-body);font-size:1rem;color:var(--ink)}
  .grp{margin-top:1.4rem}
  .grp-h{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:.4rem;display:flex;gap:.5rem;align-items:center}
  .grp-h .n{color:var(--faint)}
  .hit{display:flex;gap:.6rem;align-items:baseline;padding:.4rem 0;border-bottom:1px solid var(--hair)}
  .hit a{color:inherit;text-decoration:none;font-size:.9rem}
  .hit .sub{color:var(--muted);font-family:var(--font-mono);font-size:.74rem;margin-left:auto}
  .badge{font-family:var(--font-mono);font-size:.6rem;letter-spacing:.06em;text-transform:uppercase;border:1px solid var(--hair-strong);color:var(--muted);border-radius:3px;padding:.05rem .35rem;flex:0 0 auto}
  .empty{color:var(--muted);font-size:.9rem;padding:1.6rem 0;text-align:left}
"""


def render_page():
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Search — USR</title>
{seo_meta("Search — USR", "Search systems, manufacturers, countries and segments across the registry.", "search.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{SEARCH_CSS}</style>
</head>
<body>
{header("", "search")}
<main class="swrap">
  <h1>{bilingual("Search", "Tìm kiếm")}</h1>
  <input id="q" type="search" autocomplete="off" aria-label="search"
     placeholder="{esc('Systems, manufacturers, countries, segments…')}"
     data-ph-en="{esc('Systems, manufacturers, countries, segments…')}"
     data-ph-vn="{esc('Hệ thống, hãng, quốc gia, phân khúc…')}">
  <div id="out"></div>
  <noscript><p class="empty">{bilingual("Search needs JavaScript. Browse on the",
    "Tìm kiếm cần JavaScript. Xem ở trang")} <a href="reference.html">{bilingual("reference","tra cứu")}</a>.</p></noscript>
</main>
{footer("")}
<script src="base/base.js"></script>
<script src="base/search.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
</script>
</body>
</html>
"""


def main():
    site = json.loads(SITE.read_bytes())
    OUT.write_text(json.dumps(build_index(site), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    PAGE.write_text(render_page())
    idx = json.loads(OUT.read_bytes())
    from collections import Counter
    print("search-index.json: %d entries %s" % (len(idx["entries"]), dict(Counter(e["type"] for e in idx["entries"]))))


if __name__ == "__main__":
    main()
