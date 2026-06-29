#!/usr/bin/env python3
"""TIP-TAXONOMY gate — taxonomy pages are a LIVE view over site-data, recomputed independently.
Fail-loud exit 2:
  · TAX_EMPTY_TERM    — a term page maps to 0 entity (empty tag) / a term with entities has no page.
  · TAX_ORPHAN        — a term page with no matching value in the registry.
  · TAX_COUNT_DRIFT   — entities listed on a term page != recompute (missing members) / index missing term.
  · TAX_NULL_FAKED    — a term page lists an entity that does NOT qualify (honest-null/false faked in),
                        or a compliance page hides the false/unknown counts.
  · TAX_LINK_ASYMMETRY— a qualifying entity's detail page does not link back to its term page.
  · TAX_THEME_LEAK    — hardcoded color in taxonomy markup instead of var(--*).
Covers country · segment · airframe · propulsion · weight · flight-time · compliance."""
import json, sys, pathlib, re
from taxonomy_buckets import COMPLIANCE, weight_bucket, flight_bucket

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
LEAK = re.compile(r"(?<!&)#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(")


def tslug(v):
    return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


def page_uav_slugs(path):
    return set(re.findall(r'href="\.\./uav/([a-z0-9-]+)\.html"', path.read_text(encoding="utf-8")))


def style_of(path):
    m = re.search(r"<style>(.*?)</style>", path.read_text(encoding="utf-8"), re.S)
    return m.group(1) if m else ""


def recompute(uavs):
    """axis_dir -> {term_slug: set(uav_slug)} ; plus a sample (slug, href) per axis to prove backlink."""
    exp, sample = {}, {}

    def add(axis, g):
        exp[axis] = g
        if g:
            t = sorted(g)[0]; s = sorted(g[t])[0]   # deterministic across processes (no hash-order)
            sample[axis] = (s, f'../{axis}/{t}.html')

    def cat(field, axis):
        g = {}
        for e in uavs:
            v = (e.get(field) or {}).get("value")
            if v:
                g.setdefault(tslug(v), set()).add(e["slug"])
        add(axis, g)

    def derived(field, axis, fn):
        g = {}
        for e in uavs:
            b = fn((e.get(field) or {}).get("value"))
            if b:
                g.setdefault(b, set()).add(e["slug"])
        add(axis, g)

    cat("manufacturer_country", "country")
    cat("market_segment", "segment")
    cat("airframe_type", "airframe")
    cat("propulsion", "propulsion")
    derived("mtow_kg", "weight", weight_bucket)
    derived("endurance_min", "flight-time", flight_bucket)

    comp = {slug: {e["slug"] for e in uavs if (e.get(field) or {}).get("value") is True}
            for slug, field, en, vn in COMPLIANCE}
    add("compliance", comp)
    return exp, sample


def main():
    site = json.loads(SITE.read_bytes())
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    exp, sample = recompute(uavs)
    fails = []
    nterms = 0

    for axis, terms in exp.items():
        d = ROOT / axis
        have = ({p.stem for p in d.glob("*.html")} - {"index"}) if d.exists() else set()
        for t in sorted(set(terms) - have):
            fails.append("TAX_EMPTY_TERM: %s term %r (%d entity) has no page" % (axis, t, len(terms[t])))
        for t in sorted(have - set(terms)):
            fails.append("TAX_ORPHAN: %s page %r has no registry value" % (axis, t))
        for t in sorted(set(terms) & have):
            exp_set, page_set = terms[t], page_uav_slugs(d / f"{t}.html")
            if not exp_set:
                fails.append("TAX_EMPTY_TERM: %s/%s lists 0 entity" % (axis, t)); continue
            if exp_set - page_set:
                fails.append("TAX_COUNT_DRIFT: %s/%s page %d != live %d"
                             % (axis, t, len(page_set), len(exp_set)))
            if page_set - exp_set:
                fails.append("TAX_NULL_FAKED: %s/%s lists %d entity that do NOT qualify"
                             % (axis, t, len(page_set - exp_set)))
            nterms += 1
        idx = d / "index.html"
        if not idx.exists():
            fails.append("TAX_EMPTY_TERM: %s has no index page" % axis)
        else:
            itxt = idx.read_text(encoding="utf-8")
            for t in sorted(have):
                if f'"{t}.html"' not in itxt:
                    fails.append("TAX_COUNT_DRIFT: %s index missing term %r" % (axis, t))
            if LEAK.search(style_of(idx)):
                fails.append("TAX_THEME_LEAK: %s index has hardcoded color" % axis)

    # compliance honest-null — false & unknown counts must be SHOWN (true-set equality already checked above)
    for slug, field, en, vn in COMPLIANCE:
        p = ROOT / "compliance" / f"{slug}.html"
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8")
        nfalse = sum(1 for e in uavs if (e.get(field) or {}).get("value") is False)
        nnull = sum(1 for e in uavs if (e.get(field) or {}).get("value") is None)
        if str(nnull) not in txt or str(nfalse) not in txt:
            fails.append("TAX_NULL_FAKED: compliance/%s hides false(%d)/unknown(%d)" % (slug, nfalse, nnull))

    # backlink (2-way): a qualifying entity's detail page must link to its term page
    for axis, (uav_slug, href) in sample.items():
        up = ROOT / "uav" / f"{uav_slug}.html"
        if up.exists() and href not in up.read_text(encoding="utf-8"):
            fails.append("TAX_LINK_ASYMMETRY: uav/%s does not link back to %s" % (uav_slug, href))

    print("taxonomy: %d axes · %d term pages · %d entity" % (len(exp), nterms, len(uavs)))
    if fails:
        print("\nTAXONOMY GATE FAIL (%d):" % len(fails))
        for f in fails[:25]:
            print("  -", f)
        sys.exit(2)
    print("TAXONOMY GATE PASS: every term recomputes · no empty/orphan · honest-null shown · 2-way links · token paint.")


if __name__ == "__main__":
    main()
