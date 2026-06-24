#!/usr/bin/env python3
"""TIP-P1.3 — compare gate. compare-data.json must be a faithful, LIVE projection of site-data —
no second source of truth that can drift. Checks, fail-loud exit 2:
  · COMPARE_DRIFT — a spec value (or disputed claim set) differs from site-data.
  · honest-null two-way — null in site-data <-> null in compare-data (no fabrication, no swallow).
  · spec_range == aggregates.spec_range (live, not hardcoded).
Usage: python3 verify_compare.py [compare-data.json]."""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
DATA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "compare-data.json"


def main():
    site = json.loads(SITE.read_bytes())
    cmp = json.loads(DATA.read_bytes())
    specs = [s["key"] for s in cmp["specs"]]
    site_by = {e["slug"]: e for e in site["entities"] if e.get("entity_type", "uav") == "uav"}
    fails = []

    # 1) count — every uav present, exactly
    if len(cmp["uavs"]) != len(site_by):
        fails.append("COMPARE_DRIFT: uav count %d != site %d" % (len(cmp["uavs"]), len(site_by)))

    # 2) per-cell fidelity + honest-null two-way
    for u in cmp["uavs"]:
        e = site_by.get(u["slug"])
        if not e:
            fails.append("COMPARE_DRIFT: %s not in site-data" % u["slug"]); continue
        for k in specs:
            fo = e.get(k) or {}
            sv = fo.get("value")
            cv = (u["specs"].get(k) or {}).get("v")
            if (sv is None) != (cv is None):
                fails.append("HONEST-NULL: %s.%s site=%r compare=%r (two-way mismatch)" % (u["slug"], k, sv, cv))
            elif sv is not None and cv != sv:
                fails.append("COMPARE_DRIFT: %s.%s compare=%r != site=%r" % (u["slug"], k, cv, sv))
            # disputed claims must match (kept whole)
            if fo.get("disputed"):
                site_claims = sorted(c.get("claimed_value") for c in (fo.get("claims") or [])
                                     if c.get("claimed_value") is not None)
                cmp_claims = sorted((u["specs"].get(k) or {}).get("claims") or [])
                if site_claims != cmp_claims:
                    fails.append("COMPARE_DRIFT: %s.%s claims %r != site %r" % (u["slug"], k, cmp_claims, site_claims))

    # 3) spec_range == live aggregate (no hardcode)
    live = {k: site["aggregates"]["spec_range"][k] for k in specs if k in site["aggregates"]["spec_range"]}
    if cmp.get("spec_range") != live:
        fails.append("COMPARE_DRIFT: spec_range != live aggregates.spec_range (hardcoded?)")

    print("compare: %d uav · %d spec rows · spec_range fields %d" % (len(cmp["uavs"]), len(specs), len(cmp.get("spec_range", {}))))
    if fails:
        print("\nCOMPARE GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("COMPARE GATE PASS: compare-data == site-data · honest-null two-way · spec_range live.")


if __name__ == "__main__":
    main()
