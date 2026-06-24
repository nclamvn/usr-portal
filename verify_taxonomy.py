#!/usr/bin/env python3
"""TIP-P1.4 — taxonomy gate. Independent bijection between taxonomy TERMS (live in site-data) and
the rendered index pages: every term has exactly one page (PRD 'no empty tag'), every page maps to
a real term (no orphan page). Fail-loud exit 2. Usage: python3 verify_taxonomy.py [country_dir segment_dir]."""
import json, sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
CDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 2 else ROOT / "country"
SDIR = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "segment"


def tslug(v):
    return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


def main():
    site = json.loads(SITE.read_bytes())
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    exp_c = {tslug((e.get("manufacturer_country") or {}).get("value"))
             for e in uavs if (e.get("manufacturer_country") or {}).get("value")}
    exp_s = {tslug((e.get("market_segment") or {}).get("value"))
             for e in uavs if (e.get("market_segment") or {}).get("value")}
    have_c = {p.stem for p in CDIR.glob("*.html")} if CDIR.exists() else set()
    have_s = {p.stem for p in SDIR.glob("*.html")} if SDIR.exists() else set()

    fails = []
    for t in sorted(exp_c - have_c): fails.append("TAXONOMY_MISSING: country term %r has no index page" % t)
    for t in sorted(have_c - exp_c): fails.append("TAXONOMY_ORPHAN: country page %r has no term" % t)
    for t in sorted(exp_s - have_s): fails.append("TAXONOMY_MISSING: segment term %r has no index page" % t)
    for t in sorted(have_s - exp_s): fails.append("TAXONOMY_ORPHAN: segment page %r has no term" % t)

    print("taxonomy: country %d term/%d page · segment %d term/%d page"
          % (len(exp_c), len(have_c), len(exp_s), len(have_s)))
    if fails:
        print("\nTAXONOMY GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("TAXONOMY GATE PASS: every term has exactly one page · no orphan page (no empty tags).")


if __name__ == "__main__":
    main()
