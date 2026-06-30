#!/usr/bin/env python3
"""verify_map.py — TIP-MAP gate (fail-loud exit 2). The world map recomputes live from site-data:
every counted country placed, no country dropped silently, no fake dot, links resolve, token-only paint.

  MAP_FIGURE_DRIFT — a dot's data-n != live COUNT(manufacturer_country) recompute (global maps).
  MAP_FILTER_DRIFT — a Tier-2 filter map (data-filter="segment:..|airframe:..|compliance:..") dot
                     != the SUBSET country distribution recomputed from site-data, or a subset
                     country has no dot.
  MAP_UNPLACED     — sum of placed dots != registry total, or a counted country has no dot
                     (the dangerous zero-fab loss: a country silently missing from the map).
  MAP_NULL_FAKED   — a dot drawn for a country with 0 systems in the registry.
  MAP_DANGLING     — a country dot links to country/<slug>.html that does not resolve.
  MAP_THEME_LEAK   — a hardcoded #hex / rgb()/ hsl() inside the map block (must be var(--*) tokens).
"""
import json, re, sys, pathlib
from collections import Counter
from canon import canon_country
from taxonomy_buckets import COMPLIANCE

_CFIELD = {s: f for s, f, _, _ in COMPLIANCE}
_AXIS_FIELD = {"segment": "market_segment", "airframe": "airframe_type"}

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def live_counts():
    site = json.loads(SITE.read_bytes())
    uav = [e for e in site["entities"] if e.get("entity_type") == "uav"]
    live = Counter(canon_country((e.get("manufacturer_country") or {}).get("value")) for e in uav
                   if (e.get("manufacturer_country") or {}).get("value"))
    return live, sum(live.values()), uav


def subset_counts(uav, fkey):
    """Recompute, straight from site-data, the manufacturer-country distribution of the subset a
    Tier-2 filter map claims to show. Same grouping the taxonomy builder used (tslug on the axis
    field; compliance = field is True). Returns None for an unknown filter key."""
    if ":" not in fkey:
        return None
    axis, term = fkey.split(":", 1)
    if axis == "compliance":
        field = _CFIELD.get(term)
        if not field:
            return None
        sel = [e for e in uav if (e.get(field) or {}).get("value") is True]
    elif axis in _AXIS_FIELD:
        field = _AXIS_FIELD[axis]
        sel = [e for e in uav if (lambda v: bool(v) and _slug(v) == term)((e.get(field) or {}).get("value"))]
    else:
        return None
    return Counter(canon_country((e.get("manufacturer_country") or {}).get("value")) for e in sel
                   if (e.get("manufacturer_country") or {}).get("value"))


def check_map(html, live, total, fails, base_dir=ROOT, rel="", uav=None):
    """Validate every <div class="wmap"> block in `html`. Four kinds, told apart by data-filter and
    whether data-total == registry total: full /data map · hero · country locator · Tier-2 filter."""
    for mb in re.finditer(r'<div class="wmap[^"]*"[^>]*data-placed="(\d+)"[^>]*data-total="(\d+)"[^>]*>(.*?)</svg>',
                          html, re.S):
        placed, dtot, block = int(mb.group(1)), int(mb.group(2)), mb.group(3)
        fm = re.search(r'data-filter="([^"]*)"', mb.group(0))
        fkey = fm.group(1) if fm else ""
        if fkey:                                  # Tier-2 filter map: reference is the subset recompute
            ref = subset_counts(uav, fkey)
            if ref is None:
                fails.append(f"MAP_FILTER_DRIFT: unknown filter {fkey!r}")
                continue
            drift = "MAP_FILTER_DRIFT"
        else:
            ref, drift = live, "MAP_FIGURE_DRIFT"
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
            if ref.get(c) != n:
                fails.append(f"{drift}: {fkey or 'global'} {c!r} dot n={n} != recompute {ref.get(c)}")
            target = re.sub(r"^(?:\.\./)+", "", href)   # strip rel prefix, resolve from repo root
            if not (base_dir / target).exists():
                fails.append(f"MAP_DANGLING: {c!r} -> {href} does not resolve")
        placed_sum = sum(seen.values())
        # universal integrity: both header numbers must equal the dots actually drawn. A country
        # dropped from any map (global, hero, locator or filter) makes data-total != counted.
        if placed != placed_sum:
            fails.append(f"MAP_UNPLACED: header placed={placed} != counted dots {placed_sum}")
        if dtot != placed_sum:
            fails.append(f"MAP_UNPLACED: {fkey or 'global'} data-total={dtot} != counted dots {placed_sum}")
        # completeness: a map that claims its whole reference (full/hero global, or a filter subset)
        # must carry every counted country. The country locator is intentionally a single dot -> skip.
        complete = bool(fkey) or (dtot == total)
        if complete:
            missing = [c for c in ref if ref[c] and c not in seen]
            if missing:
                fails.append(f"{drift if fkey else 'MAP_UNPLACED'}: {fkey or 'global'} countries with no dot: {missing}")
    return fails


def main():
    live, total, uav = live_counts()
    fails = []
    sub = sorted(str(p.relative_to(ROOT)) for d in ("country", "segment", "airframe", "compliance")
                 for p in (ROOT / d).glob("*.html"))
    pages = ["data.html", "index.html"] + sub
    for name in pages:
        p = ROOT / name
        if p.exists():
            check_map(p.read_text(), live, total, fails, ROOT, uav=uav)
    if fails:
        print("\nMAP GATE FAIL:")
        for f in fails:
            print("  -", f)
        sys.exit(2)
    print(f"MAP GATE PASS: world map recomputes live · {total} systems all placed · 0 fake/dangling/leak.")


if __name__ == "__main__":
    main()
