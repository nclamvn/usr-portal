#!/usr/bin/env python3
"""TIP-P1.3 — Compare layer. Static page + client-side select of 2–4 UAVs into a side-by-side spec
table. We cannot pre-generate every combination (302 choose k), so the page is static and renders
from compare-data.json, built LIVE from site-data (one source of truth — verify_compare proves no
drift). Reuses the existing micro-track (log), glyph, tier-badge and honest-null primitives.
"""
import json, pathlib
from build_detail import NUMERIC_SPEC, UNIT
from footer import footer
from build_reference import friendly, bilingual, esc
from glyphs import glyph_svg
from nav import nav
from header import header
from seo import meta as seo_meta

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
DATA = ROOT / "out" / "compare-data.json"
OUT = ROOT / "compare.html"
GLYPHS = ["quad", "hexa", "octo", "multirotor", "fixed", "vtol", "heli", "ducted", "unknown"]


def build_data(site):
    labels = site["labels"]
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    rng = site["aggregates"].get("spec_range", {})
    rows = []
    for e in sorted(uavs, key=lambda e: e["slug"]):
        specs = {}
        for k in NUMERIC_SPEC:
            fo = e.get(k) or {}
            cell = {"v": fo.get("value"), "tier": fo.get("source_tier")}
            if fo.get("disputed"):
                cell["claims"] = [c.get("claimed_value") for c in (fo.get("claims") or [])
                                  if c.get("claimed_value") is not None]
            specs[k] = cell
        seg = (e.get("market_segment") or {}).get("value")
        rows.append({
            "slug": e["slug"], "name": (e.get("name") or {}).get("value") or e["slug"],
            "maker": (e.get("manufacturer") or {}).get("value") or "—",
            "company_slug": e.get("company_slug") or "",
            "glyph": e.get("frame_glyph", "unknown"),
            "country": (e.get("manufacturer_country") or {}).get("value"),
            "segment": seg,
            "blue": bool((e.get("blue_uas") or {}).get("value")),
            "ndaa": bool((e.get("ndaa_compliant") or {}).get("value")),
            "specs": specs,
        })
    spec_meta = [{"key": k, "en": labels["field"][k]["en"], "vn": labels["field"][k]["vn"],
                  "unit": UNIT.get(k, "")} for k in NUMERIC_SPEC]
    seg_labels = {s: {"en": labels["segment"].get(s, {}).get("en", s),
                      "vn": labels["segment"].get(s, {}).get("vn", s)}
                  for s in {r["segment"] for r in rows if r["segment"]}}
    return {"schema": "compare-data/1", "specs": spec_meta,
            "spec_range": {k: rng[k] for k in NUMERIC_SPEC if k in rng},
            "segment_labels": seg_labels, "uavs": rows}


COMPARE_CSS = """
  .cmpwrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3rem}
  h1{margin:0 0 .2rem} .lead{color:var(--muted);font-size:.85rem;margin-bottom:1.3rem}
  /* instrument console (picker) */
  .cmp-console{background:var(--bg-2);border:1px solid var(--hair);border-radius:var(--radius);padding:1.15rem 1.2rem 1.25rem;margin-bottom:1.4rem}
  .cmp-kick{font-family:var(--font-mono);font-size:.64rem;letter-spacing:.18em;text-transform:uppercase;color:var(--brass);margin-bottom:.7rem}
  .cmp-search{display:flex;align-items:center;gap:.55rem;border:1px solid var(--hair-strong);border-radius:var(--radius);padding:.55rem .75rem;background:var(--bg);transition:border-color .2s var(--ease),box-shadow .2s var(--ease)}
  .cmp-search:focus-within{border-color:var(--brass-bright);box-shadow:0 0 0 3px var(--hair)}
  .cmp-search svg{width:15px;height:15px;flex:0 0 auto;color:var(--muted)}
  .cmp-search:focus-within svg{color:var(--brass)}
  .cmp-search input{flex:1;min-width:0;background:transparent;border:0;outline:0;padding:0;font-family:var(--font-body);font-size:.9rem;color:var(--ink)}
  .cmp-search input::placeholder{color:var(--faint)}
  .cmp-search input::-webkit-search-cancel-button{-webkit-appearance:none}
  .cmp-sub{font-family:var(--font-mono);font-size:.58rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:1.05rem 0 .55rem}
  /* rack of 4 bays */
  .bays{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem}
  @media(max-width:640px){.bays{grid-template-columns:repeat(2,1fr)}}
  .bay{border:1px solid var(--hair-strong);border-radius:var(--radius);padding:.6rem;min-height:84px;display:flex;flex-direction:column;gap:.22rem;background:var(--bg)}
  .bay.empty{border-style:dashed;align-items:center;justify-content:center;color:var(--faint);background:transparent}
  .bay .bnum{font-family:var(--font-mono);font-size:.54rem;letter-spacing:.12em;text-transform:uppercase;color:var(--faint)}
  .bay.empty .dots{letter-spacing:.34em;color:var(--hair-strong);font-size:.85rem;margin-top:.3rem}
  .bay .gl{width:30px;height:30px}
  .bay .bnm{font-family:var(--font-head);font-weight:600;font-size:.84rem;line-height:1.12}
  .bay .bmk{font-family:var(--font-mono);font-size:.6rem;color:var(--brass);text-transform:uppercase;letter-spacing:.04em}
  .bay .brm{margin-top:auto;align-self:flex-end;font-family:var(--font-mono);font-size:.95rem;color:var(--muted);cursor:pointer;line-height:1}
  .bay .brm:hover{color:var(--brass)}
  .bay.chip{cursor:default}
  /* suggestion cards */
  .results{display:grid;grid-template-columns:repeat(auto-fill,minmax(152px,1fr));gap:.55rem;margin-top:.15rem}
  .results .rhint{grid-column:1/-1;font-family:var(--font-mono);font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
  .sugg{display:flex;flex-direction:column;gap:.2rem;text-align:left;background:var(--bg);border:1px solid var(--hair);border-radius:var(--radius);padding:.55rem .6rem;color:var(--ink);cursor:pointer;transition:border-color .15s var(--ease),background .15s var(--ease)}
  .sugg:hover{border-color:var(--brass-bright);background:color-mix(in srgb,var(--brass) 7%,transparent)}
  .sugg[disabled]{opacity:.4;cursor:not-allowed}
  .sugg .gl{width:28px;height:28px;margin-bottom:.05rem}
  .sugg .snm{font-family:var(--font-head);font-weight:600;font-size:.82rem;line-height:1.14}
  .sugg .smk{font-family:var(--font-mono);font-size:.58rem;color:var(--brass);text-transform:uppercase;letter-spacing:.04em}
  .sugg .sspec{font-family:var(--font-mono);font-size:.62rem;color:var(--muted);font-variant-numeric:tabular-nums}
  .sugg .sadd{margin-top:.1rem;align-self:flex-end;font-family:var(--font-mono);font-size:.58rem;letter-spacing:.08em;text-transform:uppercase;color:var(--brass)}
  .empty{color:var(--muted);font-size:.85rem;padding:1.6rem 0;text-align:center;border:1px dashed var(--hair-strong);border-radius:var(--radius);margin-top:.6rem}
  table.cmp{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:.6rem}
  table.cmp th,table.cmp td{border-bottom:1px solid var(--hair);padding:.6rem .55rem;vertical-align:top;text-align:left}
  table.cmp thead th{position:sticky;top:0;background:var(--bg)}
  .col-h{display:flex;flex-direction:column;gap:.3rem}
  .col-h .gl{width:34px;height:34px}
  .col-h .nm{font-family:var(--font-head);font-weight:600;font-size:.95rem}
  .col-h a{color:inherit} .col-h .mk a{color:var(--brass);font-family:var(--font-mono);font-size:.64rem;text-transform:uppercase;letter-spacing:.05em}
  .col-h .tags{display:flex;gap:.3rem;flex-wrap:wrap;font-family:var(--font-mono);font-size:.62rem;color:var(--muted)}
  .col-h .b{color:var(--brass)}
  .rk{font-family:var(--font-mono);font-size:.66rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
  .cmpcell .ri-spark{margin:.45rem 0 .3rem}   /* fleet-position sparkbar (shared spec-table language; .ri-spark from design-system.css) */
  .cmpcell .val{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
  .cmpcell .val.null{color:var(--muted)}
  .cmpcell .ri-tier{margin-left:.3em}   /* source-tier badge: shared .ri-tier (A brass, B/C muted) from design-system.css */
  .cmpcell .disp{display:block;font-size:.92em;color:var(--ink-soft)}
  .gl{width:34px;height:34px}
  [hidden]{display:none}
"""


def render_page(site):
    templates = "".join(f'<template data-glyph-kind="{g}">{glyph_svg(g, "gl")}</template>' for g in GLYPHS)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Compare UAVs — USR</title>
{seo_meta("Compare UAVs — USR", "Pick 2-4 systems for a side-by-side, source-cited comparison.", "compare.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{COMPARE_CSS}</style>
</head>
<body>
{header("", "compare")}
<main class="cmpwrap">
  <h1>{bilingual("Compare", "So sánh")}</h1>
  <div class="lead">{bilingual("Pick 2–4 systems for a side-by-side, source-cited comparison.",
                                "Chọn 2–4 hệ thống để so sánh song song, có dẫn nguồn.")}</div>
  <section class="cmp-console reg-frame">
    <div class="cmp-kick">{bilingual("Select systems · 2–4", "Chọn hệ thống · 2–4")}</div>
    <div class="cmp-search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="20" y1="20" x2="16.05" y2="16.05"></line></svg>
      <input id="q" type="search" autocomplete="off" placeholder="{esc('Search by model or manufacturer…')}" aria-label="search">
    </div>
    <div class="cmp-sub">{bilingual("Selected bays", "Khoang đã chọn")}</div>
    <div class="bays" id="chips"></div>
    <div class="results" id="results" hidden></div>
  </section>
  <div id="table"></div>
  <noscript><p class="empty">{bilingual("Compare needs JavaScript. Browse systems on the",
    "So sánh cần JavaScript. Xem hệ thống ở trang")} <a href="reference.html">{bilingual("reference","tra cứu")}</a>.</p></noscript>
  {templates}
</main>
{footer("")}
<script src="base/base.js"></script>
<script src="base/compare.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
</script>
</body>
</html>
"""


def main():
    site = json.loads(SITE.read_bytes())
    # sort_keys -> deterministic: segment_labels is built from a set (hash-seed order), so without
    # this the JSON byte-order varies run-to-run. Lists (specs, uavs) keep their explicit order.
    DATA.write_text(json.dumps(build_data(site), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    OUT.write_text(render_page(site))
    n = len(json.loads(DATA.read_bytes())["uavs"])
    print(f"compare.html + compare-data.json: {n} uav, {len(NUMERIC_SPEC)} spec rows")


if __name__ == "__main__":
    main()
