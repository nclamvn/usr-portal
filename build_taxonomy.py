#!/usr/bin/env python3
"""TIP-P1.4 — Taxonomy layer. One real index page per taxonomy TERM (no empty tags, PRD §4.3):
  country/<slug>.html   — every UAV from that country + the manufacturers there
  segment/<slug>.html   — every UAV in that market segment
The manufacturer axis is already served by company/<slug> (P1.1). Pages are a LIVE view over
site-data (zero new data). Slugs match field_row's taxonomy links and the graph's tax:* nodes.
Design-system-of-record only; bilingual (en/vn).
"""
import json, pathlib, shutil, re
from collections import Counter
from build_reference import friendly, bilingual, esc
from footer import footer
from canon import canonical_slug, canonical_name, canon_country
from geo_map import country_map, subset_map
from nav import nav
from header import header
from seo import meta, collection_ld, breadcrumb_ld
from taxonomy_buckets import WEIGHT_BUCKETS, FLIGHT_BUCKETS, COMPLIANCE, weight_bucket, flight_bucket

AXIS_LABEL = {"country": "Countries", "segment": "Market segments", "airframe": "Airframe types",
              "propulsion": "Propulsion types", "weight": "Weight class",
              "flight-time": "Flight-time class", "compliance": "Compliance"}

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"


def tslug(v):
    return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


TAX_CSS = """
  .twrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3rem}
  .twrap>*{max-width:var(--w-read)}
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


def page(kind, title_html, meta_html, sections, path, plain_title, count, lead=""):
    body = "".join(
        f'<div class="tsec-h">{h}</div><ul class="tlist">{items}</ul>'
        for h, items in sections)
    axis = path.split("/")[0]
    trail = [("Uncrewed Systems Review", "index.html")]
    if not path.endswith("/index.html"):                       # term page -> anchor to its axis index
        trail.append((AXIS_LABEL.get(axis, axis), f"{axis}/index.html"))
    trail.append((plain_title, path))
    bc = breadcrumb_ld(trail)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_html} — USR</title>
{meta(f"{plain_title} — USR", f"{plain_title}: {count} systems in the registry.", path)}
{collection_ld(plain_title, path, count)}
{bc}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<style>{TAX_CSS}</style>
</head>
<body>
{header("../")}
<main class="twrap">
  <header class="thead"><h1>{title_html}</h1><div class="meta">{meta_html}</div></header>{(chr(10) + "  " + lead) if lead else ""}
  {body}
  <p class="note">{bilingual(
    "A live index over the registry — every entry links to its full record. Counts are computed at build time.",
    "Chỉ mục sống trên registry — mỗi mục liên kết tới hồ sơ đầy đủ. Số đếm tính lúc build.")}</p>
</main>
{footer("../")}
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
    # slug -> canon manufacturer country (None if unrecorded) — feeds the Tier-2 filter maps,
    # same recompute as the global /data map so verify_map's MAP_FILTER_DRIFT can prove every dot.
    slug_country = {e["slug"]: canon_country((e.get("manufacturer_country") or {}).get("value")) for e in uavs}

    def filter_map(slugs, fkey, group_en, group_vn):
        cc = Counter(slug_country[x] for x in slugs if slug_country.get(x))
        placed = sum(cc.values())
        return subset_map(dict(cc), placed, len(slugs), rel="../", fkey=fkey,
                          cap_en=f"Manufacturer country of {placed}/{len(slugs)} {group_en}",
                          cap_vn=f"Nước sản xuất của {placed}/{len(slugs)} {group_vn}")

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
        uav_items = "".join(f'<li><a href="../uav/{esc(s)}.html">{esc(uav_name[s])}</a></li>'
                            for s in sorted(g["uavs"]))
        co_items = "".join(f'<li><a href="../company/{esc(cs)}.html">{esc(cn)}</a></li>'
                           for cs, cn in sorted(g["companies"]))
        meta_line = (f'{len(g["uavs"])} ' + bilingual("systems", "hệ thống")
                     + f' · {len(g["companies"])} ' + bilingual("manufacturers", "nhà sản xuất"))
        html = page("country", esc(c), meta_line, [
            (bilingual("Systems", "Hệ thống"), uav_items),
            (bilingual("Manufacturers", "Nhà sản xuất"), co_items)],
            f"country/{tslug(c)}.html", c, len(g["uavs"]),
            lead=country_map(c, len(g["uavs"]), rel="../"))
        (ROOT / "country" / f"{tslug(c)}.html").write_text(html)
        nco += 1

    nse = 0
    for s, slugs in segments.items():
        uav_items = "".join(f'<li><a href="../uav/{esc(x)}.html">{esc(uav_name[x])}</a></li>'
                            for x in sorted(slugs))
        title = friendly("segment", s, labels)
        plain = labels["segment"].get(s, {}).get("en", s)
        meta_line = f'{len(slugs)} ' + bilingual("systems", "hệ thống")
        html = page("segment", title, meta_line, [(bilingual("Systems", "Hệ thống"), uav_items)],
                    f"segment/{tslug(s)}.html", plain, len(slugs),
                    lead=filter_map(slugs, f"segment:{tslug(s)}", "systems in this segment",
                                    "hệ thống trong nhóm ứng dụng"))
        (ROOT / "segment" / f"{tslug(s)}.html").write_text(html)
        nse += 1

    # ---- new axes (TIP-TAXONOMY): categorical airframe/propulsion · derived weight/flight-time · compliance ----
    def fresh(d):
        p = ROOT / d
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)

    def entity_items(slugs):
        return "".join(f'<li><a href="../uav/{esc(x)}.html">{esc(uav_name[x])}</a></li>'
                       for x in sorted(slugs))

    def write_index(axis_dir, plain_title, title_html, terms, total_cov, extra_meta=""):
        # index lives at <axis>/index.html; term links are same-dir (slug.html)
        items = "".join(f'<li><a href="{esc(slug)}.html">{esc(label)}</a> · {n}</li>'
                        for slug, label, n in terms)
        meta_line = (f'{len(terms)} ' + bilingual("categories", "nhóm")
                     + f' · {total_cov} ' + bilingual("systems classified", "hệ thống đã phân loại") + extra_meta)
        html = page(axis_dir, title_html, meta_line, [(bilingual("Categories", "Nhóm"), items)],
                    f"{axis_dir}/index.html", plain_title, total_cov)
        (ROOT / axis_dir / "index.html").write_text(html)

    counts = {}

    # index pages for the existing country/segment axes (uniform with the new axes)
    write_index("country", "Countries", bilingual("Countries", "Quốc gia"),
                sorted([(tslug(c), c, len(g["uavs"])) for c, g in countries.items()], key=lambda x: -x[2]),
                len(uavs))
    write_index("segment", "Market segments", bilingual("Market segments", "Nhóm ứng dụng"),
                sorted([(tslug(s), labels["segment"].get(s, {}).get("en", s), len(sl))
                        for s, sl in segments.items()], key=lambda x: -x[2]),
                sum(len(sl) for sl in segments.values()))

    # categorical: group by tslug (merges formatting variants); display = most common raw variant
    for field, axis_dir, ptitle, vtitle in (
            ("airframe_type", "airframe", "Airframe types", "Loại khung bay"),
            ("propulsion", "propulsion", "Propulsion types", "Loại động lực")):
        fresh(axis_dir)
        groups = {}
        for e in uavs:
            v = (e.get(field) or {}).get("value")
            if not v:
                continue
            g = groups.setdefault(tslug(v), {"slugs": [], "labels": Counter()})
            g["slugs"].append(e["slug"]); g["labels"][v] += 1
        terms = []
        for t, g in groups.items():
            label = g["labels"].most_common(1)[0][0]
            meta_line = f'{len(g["slugs"])} ' + bilingual("systems", "hệ thống")
            lead = (filter_map(g["slugs"], f"airframe:{t}", "systems with this airframe",
                               "hệ thống cùng loại khung bay") if axis_dir == "airframe" else "")
            html = page(axis_dir, esc(label), meta_line,
                        [(bilingual("Systems", "Hệ thống"), entity_items(g["slugs"]))],
                        f"{axis_dir}/{t}.html", label, len(g["slugs"]), lead=lead)
            (ROOT / axis_dir / f"{t}.html").write_text(html)
            terms.append((t, label, len(g["slugs"])))
        cov = sum(len(g["slugs"]) for g in groups.values())
        write_index(axis_dir, ptitle, bilingual(ptitle, vtitle), sorted(terms, key=lambda x: -x[2]), cov)
        counts[axis_dir] = len(terms)

    # derived buckets: weight (mtow_kg) · flight-time (endurance_min) — membership recomputes from value
    for field, axis_dir, buckets, fn, ptitle, vtitle in (
            ("mtow_kg", "weight", WEIGHT_BUCKETS, weight_bucket, "Weight class", "Hạng trọng lượng"),
            ("endurance_min", "flight-time", FLIGHT_BUCKETS, flight_bucket, "Flight-time class", "Hạng thời gian bay")):
        fresh(axis_dir)
        members, present = {}, 0
        for e in uavs:
            b = fn((e.get(field) or {}).get("value"))
            if b is None:
                continue
            present += 1
            members.setdefault(b, []).append(e["slug"])
        terms = []
        for slug, en, vn, lo, hi in buckets:          # fixed order; skip empty (no empty tags)
            if slug not in members:
                continue
            ms = members[slug]
            meta_line = f'{len(ms)} ' + bilingual("systems", "hệ thống")
            html = page(axis_dir, bilingual(en, vn), meta_line,
                        [(bilingual("Systems", "Hệ thống"), entity_items(ms))],
                        f"{axis_dir}/{slug}.html", en, len(ms))
            (ROOT / axis_dir / f"{slug}.html").write_text(html)
            terms.append((slug, bilingual(en, vn), len(ms)))
        unrec = len(uavs) - present
        extra = " · " + bilingual(f"{unrec} not recorded", f"{unrec} chưa ghi nhận")
        write_index(axis_dir, ptitle, bilingual(ptitle, vtitle), terms, present, extra)
        counts[axis_dir] = len(terms)

    # compliance: ndaa / blue-uas — list ONLY true; meta shows true/false/unknown (honest-null, 3-state)
    fresh("compliance")
    comp_terms = []
    for slug, field, en, vn in COMPLIANCE:
        vals = [(e.get(field) or {}).get("value") for e in uavs]
        ntrue = sum(1 for v in vals if v is True)
        nfalse = sum(1 for v in vals if v is False)
        nnull = sum(1 for v in vals if v is None)
        true_slugs = [e["slug"] for e in uavs if (e.get(field) or {}).get("value") is True]
        meta_line = (f'{ntrue} ' + bilingual("compliant", "tuân thủ")
                     + f' · {nfalse} ' + bilingual("not", "không")
                     + f' · {nnull} ' + bilingual("not recorded", "chưa ghi nhận") + f' / {len(uavs)}')
        html = page("compliance", bilingual(en, vn), meta_line,
                    [(bilingual("Compliant systems", "Hệ thống tuân thủ"), entity_items(true_slugs))],
                    f"compliance/{slug}.html", en, ntrue,
                    lead=filter_map(true_slugs, f"compliance:{slug}", "compliant systems",
                                    "hệ thống tuân thủ"))
        (ROOT / "compliance" / f"{slug}.html").write_text(html)
        comp_terms.append((slug, bilingual(en, vn), ntrue))
    write_index("compliance", "Compliance", bilingual("Compliance", "Tuân thủ"),
                comp_terms, sum(t[2] for t in comp_terms))
    counts["compliance"] = len(comp_terms)

    print(f"country/: {nco} · segment/: {nse} · " + " · ".join(f"{k}/: {v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
