#!/usr/bin/env python3
"""TIP-P1.3 — Compare layer. Static page + client-side select of 2–4 UAVs into a side-by-side spec
table. We cannot pre-generate every combination (302 choose k), so the page is static and renders
from compare-data.json, built LIVE from site-data (one source of truth — verify_compare proves no
drift). Reuses the existing micro-track (log), glyph, tier-badge and honest-null primitives.
"""
import json, pathlib
from build_detail import NUMERIC_SPEC, UNIT
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
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1.2rem}
  .back{font-family:var(--font-mono);font-size:.74rem;color:var(--brass);text-decoration:none}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  h1{margin:0 0 .2rem} .lead{color:var(--muted);font-size:.85rem;margin-bottom:1.1rem}
  .pick{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin-bottom:.7rem}
  .pick input{flex:1;min-width:180px;background:var(--card-bg-soft,transparent);border:1px solid var(--hair-strong);border-radius:var(--radius);padding:.45rem .6rem;font-family:var(--font-body);font-size:.85rem;color:var(--ink)}
  .chips{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:.6rem}
  .chip{font-family:var(--font-mono);font-size:.74rem;border:1px solid var(--brass);color:var(--brass);border-radius:999px;padding:.16rem .6rem;display:inline-flex;gap:.4rem;align-items:center;cursor:default}
  .chip b{cursor:pointer}
  .results{border:1px solid var(--hair);border-radius:var(--radius);max-height:230px;overflow:auto;margin-bottom:1rem}
  .results button{display:block;width:100%;text-align:left;background:transparent;border:0;border-bottom:1px solid var(--hair);padding:.4rem .6rem;font-family:var(--font-body);font-size:.82rem;color:var(--ink);cursor:pointer}
  .results button:hover{background:color-mix(in srgb,var(--brass) 8%,transparent)}
  .results button[disabled]{opacity:.4;cursor:not-allowed}
  .results .mk{color:var(--muted);font-family:var(--font-mono);font-size:.72rem}
  .results .rhint{padding:.4rem .6rem;font-family:var(--font-mono);font-size:.66rem;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--hair);background:color-mix(in srgb,var(--brass) 4%,transparent)}
  .empty{color:var(--muted);font-size:.85rem;padding:1.4rem 0;text-align:center;border:1px dashed var(--hair-strong);border-radius:var(--radius)}
  table.cmp{width:100%;border-collapse:collapse;font-size:.82rem}
  table.cmp th,table.cmp td{border-bottom:1px solid var(--hair);padding:.55rem .5rem;vertical-align:top;text-align:left}
  table.cmp thead th{position:sticky;top:0;background:var(--bg)}
  .col-h{display:flex;flex-direction:column;gap:.3rem}
  .col-h .nm{font-family:var(--font-head);font-weight:600;font-size:.92rem}
  .col-h a{color:inherit} .col-h .mk a{color:var(--brass);font-family:var(--font-mono);font-size:.72rem}
  .col-h .tags{display:flex;gap:.3rem;flex-wrap:wrap;font-family:var(--font-mono);font-size:.64rem;color:var(--muted)}
  .col-h .b{color:var(--brass)}
  .rk{font-family:var(--font-mono);font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
  .cmpcell .track{display:block;height:2px;background:var(--hair-strong);border-radius:2px;position:relative;margin:.45rem 0 .3rem}
  .cmpcell .track.null{background:transparent;border-top:1px dashed var(--hair-strong);height:0}
  .cmpcell .tick{position:absolute;top:50%;width:7px;height:7px;border-radius:50%;background:var(--brass);transform:translate(-50%,-50%)}
  .cmpcell .val{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
  .cmpcell .val.null{color:var(--muted)}
  .cmpcell .tier{border:1px solid var(--brass);color:var(--brass);border-radius:3px;font-size:.85em;padding:0 .3em;margin-left:.3em}
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
  <div class="pick"><input id="q" type="search" autocomplete="off"
       placeholder="{esc('Search by model or manufacturer…')}" aria-label="search"></div>
  <div class="results" id="results" hidden></div>
  <div class="chips" id="chips"></div>
  <div id="table"></div>
  <noscript><p class="empty">{bilingual("Compare needs JavaScript. Browse systems on the",
    "So sánh cần JavaScript. Xem hệ thống ở trang")} <a href="reference.html">{bilingual("reference","tra cứu")}</a>.</p></noscript>
  {templates}
</main>
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
