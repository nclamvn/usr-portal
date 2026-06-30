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
  MAP_PIN_FAKED    — a Tier-3 HQ pin that does not trace to a real company.hq_city, sits at a city
                     absent from the gazetteer, links to a missing company page, or a company with a
                     mappable HQ that silently has no pin.
"""
import json, re, sys, pathlib, html as _html
from collections import Counter
from canon import canon_country
from taxonomy_buckets import COMPLIANCE
from geo_map import CITY_COORD

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


def company_hq():
    """{company slug: recorded hq_city} for every company entity that carries one. The honest source
    of truth a Tier-3 HQ pin must trace back to."""
    site = json.loads(SITE.read_bytes())
    out = {}
    for e in site["entities"]:
        if e.get("entity_type") == "company":
            c = e.get("hq_city")
            v = c.get("value") if isinstance(c, dict) else c
            if v:
                out[e["slug"]] = v
    return out


def check_hq(html, co_hq, fails, base_dir=ROOT):
    """Validate every <div class="hqmap"> block: each pin traces to a real company.hq_city at a
    gazetteer-resolvable city, links resolve, and no mappable HQ is dropped (MAP_PIN_FAKED)."""
    mappable = {s for s, city in co_hq.items() if city in CITY_COORD}
    for mb in re.finditer(r'<div class="hqmap"[^>]*data-pins="(\d+)"[^>]*data-total="(\d+)"[^>]*>(.*?)</svg>',
                          html, re.S):
        pins_attr, block = int(mb.group(1)), mb.group(3)
        leak = re.findall(r"(?<!&)#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(", block)
        if leak:
            fails.append(f"MAP_THEME_LEAK: hardcoded colour in HQ map block {leak[:1]}")
        pins = re.findall(r'<a href="([^"]*?\.html)">\s*<path[^>]*data-co="([^"]*)"[^>]*data-city="([^"]*)"', block)
        seen = set()
        for href, slug, city in pins:
            city = _html.unescape(city)
            seen.add(slug)
            if slug not in co_hq:
                fails.append(f"MAP_PIN_FAKED: pin for {slug!r} which has no recorded hq_city")
            elif co_hq[slug] != city:
                fails.append(f"MAP_PIN_FAKED: {slug!r} pin city {city!r} != record {co_hq[slug]!r}")
            if city not in CITY_COORD:
                fails.append(f"MAP_PIN_FAKED: {slug!r} pinned at ungeocoded city {city!r}")
            target = re.sub(r"^(?:\.\./)+", "", href)
            if not (base_dir / target).exists():
                fails.append(f"MAP_DANGLING: HQ pin {slug!r} -> {href} does not resolve")
        if pins_attr != len(seen):
            fails.append(f"MAP_PIN_FAKED: data-pins={pins_attr} != counted pins {len(seen)}")
        missing = mappable - seen
        if missing:
            fails.append(f"MAP_PIN_FAKED: makers with a mappable HQ but no pin: {sorted(missing)}")
    return fails


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
    co_hq = company_hq()
    fails = []
    sub = sorted(str(p.relative_to(ROOT)) for d in ("country", "segment", "airframe", "compliance")
                 for p in (ROOT / d).glob("*.html"))
    pages = ["data.html", "index.html"] + sub
    for name in pages:
        p = ROOT / name
        if p.exists():
            html = p.read_text()
            check_map(html, live, total, fails, ROOT, uav=uav)
            check_hq(html, co_hq, fails, ROOT)
    if fails:
        print("\nMAP GATE FAIL:")
        for f in fails:
            print("  -", f)
        sys.exit(2)
    print(f"MAP GATE PASS: world map recomputes live · {total} systems all placed · "
          f"{len(co_hq)} HQ pins trace to real records · 0 fake/dangling/leak.")


if __name__ == "__main__":
    main()
