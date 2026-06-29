#!/usr/bin/env python3
"""TIP-P2.3 — data-overview gate. Independent: re-derive every distribution straight from site-data
and check data-overview.json against it. Fail-loud exit 2:
  · OVERVIEW_DRIFT — a bucket value (or total/coverage) differs from the live recompute.
  · OVERVIEW_SUM   — a distribution's buckets (incl. honest-null + 'other') don't sum to its total.
  · honest-null two-way — segment 'null' bucket == COUNT(null segment); standards unverified == total - yes.
Usage: python3 verify_data.py [data-overview.json]."""
import json, sys, pathlib, re
from collections import Counter
from canon import canon_country, canonical_slug, canonical_name

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
OV = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "data-overview.json"
SPEC_FIELDS = ["mtow_kg", "max_payload_kg", "endurance_min", "max_range_km", "max_link_km",
               "max_speed_ms", "service_ceiling_m", "encryption", "blue_uas", "ndaa_compliant",
               "gps_denied_capable"]
def tslug(v): return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


def main():
    site = json.loads(SITE.read_bytes())
    ov = json.loads(OV.read_bytes())
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    companies = [e for e in site["entities"] if e.get("entity_type") == "company"]
    total = len(uavs)
    fails = []

    # re-derive slug-keyed distributions
    cty = Counter(tslug(canon_country((e.get("manufacturer_country") or {}).get("value")))
                  for e in uavs if (e.get("manufacturer_country") or {}).get("value"))
    mkr = Counter(canonical_slug((e.get("manufacturer") or {}).get("value"))
                  for e in uavs if (e.get("manufacturer") or {}).get("value"))
    seg = Counter(tslug((e.get("market_segment") or {}).get("value"))
                  for e in uavs if (e.get("market_segment") or {}).get("value"))
    seg_null = sum(1 for e in uavs if not (e.get("market_segment") or {}).get("value"))

    def check_dist(name, buckets, ref, tail_total, null_expected=None):
        shown = 0
        for b in buckets:
            if b.get("other"):
                continue
            if b.get("null"):
                if null_expected is not None and b["v"] != null_expected:
                    fails.append("OVERVIEW_DRIFT: %s null bucket=%d != live %d" % (name, b["v"], null_expected))
                shown += b["v"]; continue
            live = ref.get(b["slug"], 0)
            if b["v"] != live:
                fails.append("OVERVIEW_DRIFT: %s[%s]=%d != live %d" % (name, b["slug"], b["v"], live))
            shown += b["v"]
        other = sum(b["v"] for b in buckets if b.get("other"))
        if shown + other != tail_total:
            fails.append("OVERVIEW_SUM: %s buckets sum %d != total %d" % (name, shown + other, tail_total))

    check_dist("country", ov["country"], cty, total)
    check_dist("maker", ov["maker"], mkr, total)
    check_dist("segment", ov["segment"], seg, total, null_expected=seg_null)

    # standards — yes == COUNT(true); unverified is total - yes (never inferred 'false')
    for s in ov["standards"]:
        yes = sum(1 for e in uavs if (e.get(s["key"]) or {}).get("value") is True)
        if s["yes"] != yes:
            fails.append("OVERVIEW_DRIFT: standard %s yes=%d != live %d" % (s["key"], s["yes"], yes))
        if s["total"] != total:
            fails.append("OVERVIEW_DRIFT: standard %s total=%d != %d" % (s["key"], s["total"], total))

    # coverage — per-field % from live spec_fill_rate
    fill = site["aggregates"]["spec_fill_rate"]
    cov = {c["key"]: c for c in ov["coverage"]}
    for k in SPEC_FIELDS:
        live = round(100 * fill[k]["present"] / fill[k]["total"]) if fill.get(k) else 0
        if cov.get(k, {}).get("pct") != live:
            fails.append("OVERVIEW_DRIFT: coverage %s=%s != live %d" % (k, cov.get(k, {}).get("pct"), live))

    # capability spectrum — min/max must match live aggregates.spec_range (no hardcoded envelope)
    sr_live = site["aggregates"].get("spec_range", {})
    for r in ov.get("spec_range", []):
        live = sr_live.get(r["key"])
        if not live or r["min"] != live["min"] or r["max"] != live["max"]:
            fails.append("OVERVIEW_DRIFT: spec_range %s min/max=%s/%s != live %s" % (r["key"], r.get("min"), r.get("max"), live))

    # masthead totals
    exp = {"uav": total, "company": len(companies), "country": len(cty), "segment": len(seg),
           "disputed": site["aggregates"]["field_status_counts"].get("disputed", 0)}
    for k, v in exp.items():
        if ov["totals"].get(k) != v:
            fails.append("OVERVIEW_DRIFT: total %s=%s != live %d" % (k, ov["totals"].get(k), v))

    print("data-overview: country %d · maker %d · segment %d (null=%d) · total %d"
          % (len(cty), len(mkr), len(seg), seg_null, total))
    if fails:
        print("\nDATA GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("DATA GATE PASS: every figure == live recompute · sums close · honest-null two-way.")


if __name__ == "__main__":
    main()
