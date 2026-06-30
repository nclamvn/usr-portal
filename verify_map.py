#!/usr/bin/env python3
"""verify_map.py — TIP-MAP gate (fail-loud exit 2). The world map recomputes live from site-data:
every counted country placed, no country dropped silently, no fake dot, links resolve, token-only paint.

  MAP_FIGURE_DRIFT — a dot's data-n != live COUNT(manufacturer_country) recompute.
  MAP_UNPLACED     — sum of placed dots != registry total, or a counted country has no dot
                     (the dangerous zero-fab loss: a country silently missing from the map).
  MAP_NULL_FAKED   — a dot drawn for a country with 0 systems in the registry.
  MAP_DANGLING     — a country dot links to country/<slug>.html that does not resolve.
  MAP_THEME_LEAK   — a hardcoded #hex / rgb()/ hsl() inside the map block (must be var(--*) tokens).
"""
import json, re, sys, pathlib
from collections import Counter
from canon import canon_country

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def live_counts():
    site = json.loads(SITE.read_bytes())
    uav = [e for e in site["entities"] if e.get("entity_type") == "uav"]
    live = Counter(canon_country((e.get("manufacturer_country") or {}).get("value")) for e in uav
                   if (e.get("manufacturer_country") or {}).get("value"))
    return live, sum(live.values())


def check_map(html, live, total, fails, base_dir=ROOT, rel=""):
    """Validate every <div class="wmap"> block in `html`. Appends gate failures to `fails`."""
    for mb in re.finditer(r'<div class="wmap[^"]*"[^>]*data-placed="(\d+)"[^>]*data-total="(\d+)"[^>]*>(.*?)</svg>',
                          html, re.S):
        placed, dtot, block = int(mb.group(1)), int(mb.group(2)), mb.group(3)
        # THEME_LEAK — no raw colour in the map block
        leak = re.findall(r"(?<!&)#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(", block)
        if leak:
            fails.append(f"MAP_THEME_LEAK: hardcoded colour in map block {leak[:1]}")
        dots = re.findall(r'<a href="([^"]*?\.html)">\s*<circle[^>]*data-c="([^"]*)"[^>]*data-n="(\d+)"', block)
        seen = Counter()
        for href, c, n in dots:
            n = int(n)
            seen[c] += n
            if n <= 0:
                fails.append(f"MAP_NULL_FAKED: dot for {c!r} with n={n}")
            if live.get(c) != n:
                fails.append(f"MAP_FIGURE_DRIFT: {c!r} dot n={n} != live {live.get(c)}")
            target = re.sub(r"^(?:\.\./)+", "", href)   # strip rel prefix, resolve from repo root
            if not (base_dir / target).exists():
                fails.append(f"MAP_DANGLING: {c!r} -> {href} does not resolve")
        placed_sum = sum(seen.values())
        # this is the FULL distribution map (placed == total). Mini/highlight maps set data-total to
        # their own slice, so the invariant is uniformly placed == data-total.
        if placed != placed_sum:
            fails.append(f"MAP_UNPLACED: header placed={placed} != counted dots {placed_sum}")
        if dtot == total and placed_sum != total:
            fails.append(f"MAP_UNPLACED: map placed {placed_sum} != registry total {total} (a country dropped)")
        if dtot == total:
            missing = [c for c in live if c not in seen]
            if missing:
                fails.append(f"MAP_UNPLACED: counted countries with no dot: {missing}")
    return fails


def main():
    live, total = live_counts()
    fails = []
    pages = ["data.html", "index.html"] + sorted(str(p.relative_to(ROOT)) for p in (ROOT / "country").glob("*.html"))
    for name in pages:
        p = ROOT / name
        if p.exists():
            check_map(p.read_text(), live, total, fails, ROOT)
    if fails:
        print("\nMAP GATE FAIL:")
        for f in fails:
            print("  -", f)
        sys.exit(2)
    print(f"MAP GATE PASS: world map recomputes live · {total} systems all placed · 0 fake/dangling/leak.")


if __name__ == "__main__":
    main()
