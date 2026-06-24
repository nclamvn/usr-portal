#!/usr/bin/env python3
"""TIP-UX2 — homepage gate. Fail-loud exit 2:
  · HOME_FIGURE_DRIFT — the hero/ribbon numbers (systems · countries · coverage%) must equal a live
    recompute from site-data (never hardcoded).
  · EMPTY_MEDIA_SLOT — no empty media placeholder on the home (the old black 'Media Library' box).
  · HOME_SAMPLE — no sample:true / opinion-without-author article surfaced on the public home
    (home links only the real factual newsroom articles, not the articles.json drafts)."""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
HOME = ROOT / "index.html"


def main():
    site = json.loads(SITE.read_bytes())
    html = HOME.read_text()
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    countries = len({(e.get("manufacturer_country") or {}).get("value") for e in uavs
                     if (e.get("manufacturer_country") or {}).get("value")})
    fill = site["aggregates"]["spec_fill_rate"]
    present = sum(d["present"] for d in fill.values()); total = sum(d["total"] for d in fill.values())
    coverage = round(100 * present / total) if total else 0
    n = len(uavs)
    fails = []

    # 1) figure drift — live values must be present in the rendered hero/ribbon
    if f'>{n}<' not in html:
        fails.append("HOME_FIGURE_DRIFT: hero count %d not rendered (hardcoded/stale?)" % n)
    if f'>{countries}<' not in html:
        fails.append("HOME_FIGURE_DRIFT: countries %d not rendered" % countries)
    if f'>{coverage}%<' not in html:
        fails.append("HOME_FIGURE_DRIFT: coverage %d%% not rendered" % coverage)

    # 2) empty media slot — the old placeholder box must be gone
    for marker in ('Media Library', 'lưu ở Media', 'class="pk"'):
        if marker in html:
            fails.append("EMPTY_MEDIA_SLOT: home still contains placeholder %r" % marker)

    # 3) no sample / opinion article surfaced on the public home
    arts = json.loads(ARTS.read_bytes())["articles"]
    for a in arts:
        if a.get("sample") or (a.get("type") in ("analysis", "opinion") and not a.get("human_author")):
            for path in (f'news/{a["slug"]}.html', f'analysis/{a["slug"]}.html'):
                if path in html:
                    fails.append("HOME_SAMPLE: home links draft/opinion %r" % a["slug"])

    print("home: count=%d countries=%d coverage=%d%% · checks run" % (n, countries, coverage))
    if fails:
        print("\nHOME GATE FAIL:")
        for x in fails:
            print("  -", x)
        sys.exit(2)
    print("HOME GATE PASS: hero figures live · no empty media slot · no sample/opinion on home.")


if __name__ == "__main__":
    main()
