#!/usr/bin/env python3
"""TIP-HOMEPAGE gate — the homepage stays honest, independent recompute. Fail-loud exit 2:
  · HP_FIGURE_DRIFT — systems/countries/coverage on the page != live recompute (kills '13 vs 28').
  · HP_DANGLING    — a hero/card/report/hot link points to a slug with no built page.
  · HP_NULL_FAKED  — compare shows a value where the registry is null, or hides a real null.
  · HP_THEME_LEAK  — hardcoded color in inline <style>, or a mock-only font (Space Grotesk/Inter/amber).
  · HP_I18N        — visible-string en/vn pairs unbalanced in the homepage.
  · HP_MOTION      — ticker/blink animation not guarded by prefers-reduced-motion.
"""
import json, re, sys, pathlib
from build_reference import maker_model

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
HOME = ROOT / "index.html"
NULL_MARKERS = ("chưa ghi nhận", "not recorded")


def live(site):
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    countries = len({(e.get("manufacturer_country") or {}).get("value") for e in ents
                     if (e.get("manufacturer_country") or {}).get("value")})
    fill = site["aggregates"]["spec_fill_rate"]
    present = sum(d["present"] for d in fill.values()); total = sum(d["total"] for d in fill.values())
    coverage = round(100 * present / total) if total else 0
    return ents, len(ents), countries, coverage


def compare_picks(ents):
    """Replicate build_index.compare_preview pick — deterministic, independent."""
    def score(e):
        return sum(1 for k in ("max_range_km", "endurance_min", "mtow_kg", "market_segment")
                   if (e.get(k) or {}).get("value") is not None)
    picks, seen = [], set()
    for e in sorted(ents, key=lambda e: (-score(e), e["canonical_id"])):
        fam = e.get("family_id")
        if fam in seen:
            continue
        seen.add(fam); picks.append(e)
        if len(picks) == 3:
            break
    return picks


def fmt(v):
    if isinstance(v, float) and v != int(v):
        return ("%g" % v).replace(".", ",")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return str(int(v))
    return str(v)


def main():
    site = json.loads(SITE.read_bytes())
    html = HOME.read_text(encoding="utf-8")
    ents, n, countries, coverage = live(site)
    fails = []

    # 1) figure drift — masthead live stats
    for needle, what in ((f">{n}<", "systems"), (f">{countries}<", "countries"), (f">{coverage}%<", "coverage")):
        if needle not in html:
            fails.append("HP_FIGURE_DRIFT: %s %r not rendered live" % (what, needle))

    # 2) dangling — every news/<slug> link resolves; top-level section links resolve
    for slug in set(re.findall(r'href="news/([a-z0-9-]+)\.html"', html)):
        if not (ROOT / "news" / f"{slug}.html").exists():
            fails.append("HP_DANGLING: news/%s.html does not resolve" % slug)
    for top in set(re.findall(r'href="([a-z-]+\.html)"', html)):
        if not (ROOT / top).exists():
            fails.append("HP_DANGLING: %s does not resolve" % top)

    # 3) null-faked — compare table cells vs registry for the same deterministic picks
    picks = compare_picks(ents)
    FIELDS = ["max_range_km", "endurance_min", "mtow_kg", "market_segment"]
    tbl = re.search(r'<table class="compare-table">.*?</table>', html, re.S)
    tbl = tbl.group(0) if tbl else ""
    exp_nulls = 0
    for e in picks:
        for k in FIELDS:
            v = (e.get(k) or {}).get("value")
            if v is None:
                exp_nulls += 1
            elif k != "market_segment":
                if fmt(v) not in tbl:
                    fails.append("HP_NULL_FAKED: compare missing real %s=%s for %s"
                                 % (k, fmt(v), maker_model(e)[1]))
    rendered_nulls = sum(tbl.count(m) for m in NULL_MARKERS)
    # each null cell renders one bilingual marker pair (both en+vn strings present) -> count en marker
    en_nulls = tbl.count("not recorded")
    if en_nulls != exp_nulls:
        fails.append("HP_NULL_FAKED: compare shows %d null-markers != %d registry nulls" % (en_nulls, exp_nulls))

    # 4) theme leak — inline style must be token-only; no mock fonts anywhere
    style = "".join(re.findall(r"<style>(.*?)</style>", html, re.S))
    leak = re.findall(r"(?<!&)#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(", style)
    if leak:
        fails.append("HP_THEME_LEAK: hardcoded color in <style>: %s" % leak[:3])
    for bad in ("Space Grotesk", "Inter:wght", "#FF6A13"):
        if bad in html:
            fails.append("HP_THEME_LEAK: mock-only asset present: %r" % bad)

    # 5) i18n balance
    en = len(re.findall(r"data-lang-en", html))
    vn = len(re.findall(r"data-lang-vn", html))
    if en != vn:
        fails.append("HP_I18N: en(%d) != vn(%d) lang spans" % (en, vn))

    # 6) reduced-motion guard for ticker/blink
    rm = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^@]*?\}[^@]*?)\}", style, re.S)
    if "animation:none" not in style.replace(" ", "") or ".ticker" not in (rm.group(1) if rm else ""):
        fails.append("HP_MOTION: ticker/blink not guarded by prefers-reduced-motion")

    print("homepage: %d systems · %d countries · %d%% coverage · %d compare-nulls" % (n, countries, coverage, exp_nulls))
    if fails:
        print("\nHOMEPAGE GATE FAIL (%d):" % len(fails))
        for x in fails[:20]:
            print("  -", x)
        sys.exit(2)
    print("HOMEPAGE GATE PASS: figures live · links real · honest-null compare · token paint · i18n balanced · motion guarded.")


if __name__ == "__main__":
    main()
