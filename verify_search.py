#!/usr/bin/env python3
"""TIP-P2.1 — search gate. Independent: re-derive the searchable node universe from site-data and
check search-index.json against it. Fail-loud exit 2:
  · SEARCH_DRIFT   — an entry's url/label differs from the node it claims.
  · SEARCH_ORPHAN  — an entry has no corresponding node.
  · SEARCH_MISSING — a node has no entry.
  · SEARCH_DEAD    — an entry url does not resolve to a real page on disk.
Usage: python3 verify_search.py [search-index.json]."""
import json, sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
IDX = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "search-index.json"


def tslug(v):
    return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


def derive(site):
    """Independent expected map (type,id) -> url, mirroring build_search."""
    ents = site["entities"]
    uavs = [e for e in ents if e.get("entity_type", "uav") == "uav"]
    exp = {}
    for e in uavs:
        exp[("uav", e["slug"])] = "entity/%s.html" % e["slug"]
    for e in ents:
        if e.get("entity_type") == "company":
            exp[("company", e["slug"])] = "company/%s.html" % e["slug"]
    for e in uavs:
        c = (e.get("manufacturer_country") or {}).get("value")
        if c:
            exp[("country", tslug(c))] = "country/%s.html" % tslug(c)
        s = (e.get("market_segment") or {}).get("value")
        if s:
            exp[("segment", tslug(s))] = "segment/%s.html" % tslug(s)
    return exp


def main():
    site = json.loads(SITE.read_bytes())
    idx = json.loads(IDX.read_bytes())
    exp = derive(site)
    have = {(e["type"], e["id"]): e for e in idx["entries"]}
    fails = []

    for key in sorted(exp):
        if key not in have:
            fails.append("SEARCH_MISSING: %s %r has no index entry" % key)
        elif have[key]["url"] != exp[key]:
            fails.append("SEARCH_DRIFT: %s %r url=%r != %r" % (key[0], key[1], have[key]["url"], exp[key]))
    for key, e in sorted(have.items()):
        if key not in exp:
            fails.append("SEARCH_ORPHAN: entry %s %r has no node" % key)
        # url must resolve to a real page on disk
        if not (ROOT / e["url"]).exists():
            fails.append("SEARCH_DEAD: %s %r url %r does not resolve" % (key[0], key[1], e["url"]))

    from collections import Counter
    print("search: %d entries %s | expected %d nodes"
          % (len(have), dict(Counter(t for t, _ in have)), len(exp)))
    if fails:
        print("\nSEARCH GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("SEARCH GATE PASS: index == node universe · no orphan/missing · every url resolves.")


if __name__ == "__main__":
    main()
