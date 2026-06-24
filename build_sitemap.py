#!/usr/bin/env python3
"""TIP-P2.2 — sitemap.xml generated from the actual built surfaces (uav · company · country ·
segment · the static top-level pages incl. /search and /data · editorial). One <loc> per real page;
verify_seo proves the bijection (loc <-> page). Deterministic (sorted) -> idempotent. lastmod is
omitted on purpose: we don't track per-page modification dates, and a volatile/fabricated date would
break idempotency and honesty."""
import pathlib
from seo import BASE

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "sitemap.xml"
TOP = ["index.html", "reference.html", "search.html", "compare.html", "data.html", "knowledge.html"]
DIRS = ["entity", "company", "country", "segment", "news", "analysis", "knowledge"]


def surfaces():
    paths = [p for p in TOP if (ROOT / p).exists()]
    for d in DIRS:
        paths += sorted(str(p.relative_to(ROOT)) for p in (ROOT / d).glob("*.html"))
    return sorted(paths)


def main():
    locs = surfaces()
    body = "\n".join(f"  <url><loc>{BASE}/{p}</loc></url>" for p in locs)
    OUT.write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                   + body + "\n</urlset>\n")
    print(f"sitemap.xml: {len(locs)} urls")


if __name__ == "__main__":
    main()
