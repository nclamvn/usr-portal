#!/usr/bin/env python3
"""TIP-P3.2 — review gate. review-data.json must be a faithful, LIVE projection of site-data (synced
with Compare/UAV-DB — no second source). Independent recompute, fail-loud exit 2:
  · REVIEW_DRIFT      — a dimension score != log-position recompute from the spec + live range.
  · honest-null two-way — null spec <-> null score (a missing spec must NOT be scored, never 0).
  · REVIEW_TOTAL      — total != mean of scored dimensions (no hand-tuned weighting).
Usage: python3 verify_review.py [review-data.json]."""
import json, sys, pathlib
from build_detail import log_pos

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
RV = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "review-data.json"


def main():
    site = json.loads(SITE.read_bytes())
    rv = json.loads(RV.read_bytes())
    by = {e["slug"]: e for e in site["entities"] if e.get("entity_type", "uav") == "uav"}
    rng = site["aggregates"]["spec_range"]
    dkeys = [d["key"] for d in rv["dims"]]
    fails = []

    if len(rv["uavs"]) != len(by):
        fails.append("REVIEW_DRIFT: uav count %d != site %d" % (len(rv["uavs"]), len(by)))

    for u in rv["uavs"]:
        e = by.get(u["slug"])
        if not e:
            fails.append("REVIEW_DRIFT: %s not in site-data" % u["slug"]); continue
        present = []
        for k in dkeys:
            v = (e.get(k) or {}).get("value")
            r = rng.get(k)
            scored = isinstance(v, (int, float)) and not isinstance(v, bool) and r
            s = u["scores"].get(k)
            if not scored:
                if s is not None:
                    fails.append("HONEST-NULL: %s.%s no spec but score=%r (must be null)" % (u["slug"], k, s))
            else:
                exp = round(log_pos(v, r["min"], r["max"]))
                if s is None:
                    fails.append("HONEST-NULL: %s.%s has spec but score is null" % (u["slug"], k))
                elif s != exp:
                    fails.append("REVIEW_DRIFT: %s.%s score=%r != recompute %r" % (u["slug"], k, s, exp))
                else:
                    present.append(exp)
        exp_total = round(sum(present) / len(present)) if present else None
        if u["total"] != exp_total:
            fails.append("REVIEW_TOTAL: %s total=%r != mean-of-scored %r" % (u["slug"], u["total"], exp_total))
        if u["scored"] != len(present):
            fails.append("REVIEW_DRIFT: %s scored=%r != %d" % (u["slug"], u["scored"], len(present)))

    print("review: %d uav · %d dims" % (len(rv["uavs"]), len(dkeys)))
    if fails:
        print("\nREVIEW GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("REVIEW GATE PASS: every score == spec recompute · honest-null two-way · total = mean-of-scored.")


if __name__ == "__main__":
    main()
