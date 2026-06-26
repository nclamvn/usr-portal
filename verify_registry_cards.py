#!/usr/bin/env python3
"""TIP-FP1 gate — the registry cards must stay Mode D: every card title is a real registry FIELD value
(no authored prose), every card carries source+tier and a desk+stratum tag. Scans the rendered
registry.html against content/lae-registry.json (the field source)."""
import json, re, sys, pathlib, html as _html

ROOT = pathlib.Path(__file__).resolve().parent
REG = ROOT / "registry.html"
LAE = ROOT / "content" / "lae-registry.json"

CARD_RE = re.compile(r'<article class="rcard"([^>]*)>(.*?)</article>', re.S)
TITLE_RE = re.compile(r'<h3 class="rcard-t">(?:<a[^>]*>|<span>)(.*?)(?:</a>|</span>)</h3>', re.S)


class GateError(Exception):
    def __init__(self, gate, msg):
        super().__init__(f"{gate}: {msg}"); self.gate = gate


def check(html, names):
    cards = CARD_RE.findall(html)
    if not cards:
        raise GateError("NO_CARDS", "registry.html has no rcards")
    for attrs, inner in cards:
        # 0 PROSE — the title must be a verbatim registry name field, not an authored sentence
        m = TITLE_RE.search(inner)
        if not m:
            raise GateError("TITLE_MISSING", "a card has no title")
        title = _html.unescape(m.group(1)).strip()
        if title not in names:
            raise GateError("PROSE", f"card title not a registry field value: {title[:50]!r}")
        # SOURCED — source + tier
        if 'class="tier' not in inner:
            raise GateError("UNSOURCED", f"card {title[:30]!r} has no source/tier")
        # DESK_COMPLETE — exactly one desk + a stratum
        if 'data-desk="' not in attrs or 'data-stratum="' not in attrs or 'data-desk=""' in attrs \
                or 'data-stratum=""' in attrs:
            raise GateError("DESK_INCOMPLETE", f"card {title[:30]!r} missing desk/stratum")
    return len(cards)


def main():
    if not REG.exists():
        print("verify_registry_cards: registry.html missing — run build_registry_cards.py"); sys.exit(2)
    html = REG.read_text(encoding="utf-8")
    names = {e.get("name") or e["entity"] for e in json.loads(LAE.read_bytes())["entities"]}
    # no borrowed image on this surface
    if re.search(r'<img\b[^>]*\bsrc\s*=\s*["\']https?://', html):
        print("REGISTRY-CARDS GATE FAIL — FIGURE_PROVENANCE: external image"); sys.exit(2)
    try:
        n = check(html, names)
    except GateError as e:
        print(f"REGISTRY-CARDS GATE FAIL — {e}"); sys.exit(2)
    print(f"REGISTRY-CARDS GATE PASS: {n} Mode-D cards · every title is a registry field (0 prose) · "
          f"all sourced + desk/stratum tagged · 0 borrowed image")


if __name__ == "__main__":
    main()
