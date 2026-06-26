#!/usr/bin/env python3
"""TIP-FP2 gate — the front-page registry tier must stay honest: DEDUP (no D-card on the homepage for
an entity that already has an E article — would show the event twice) and DESK_HONEST (a desk renders a
full strip only when it has >= N cards; a thin desk collapses to a 'building' line, never a padded block).
Scans the rendered index.html against the curated article->entity map."""
import json, re, sys, pathlib, html as _html

ROOT = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
MAP = ROOT / "content" / "article_entity_map.json"
N = 4

CARD_T = re.compile(r'<h3 class="rcard-t">(?:<a[^>]*>|<span>)(.*?)(?:</a>|</span>)</h3>', re.S)
STRIP = re.compile(r'<section class="fp-desk" data-mode="strip" data-n="(\d+)"', re.S)
LINE = re.compile(r'<a class="fp-deskline" data-mode="line" data-n="(\d+)"', re.S)


class GateError(Exception):
    def __init__(self, gate, msg):
        super().__init__(f"{gate}: {msg}"); self.gate = gate


def check(html, articled):
    titles = [_html.unescape(t).strip() for t in CARD_T.findall(html)]
    # DEDUP — no homepage D-card is an entity that has an E article
    dup = [t for t in titles if t in articled]
    if dup:
        raise GateError("DEDUP", f"{len(dup)} D-card(s) duplicate an articled event, e.g. {dup[0][:40]!r}")
    # DESK_HONEST — strips only at >= N, lines only at < N
    strips = [int(x) for x in STRIP.findall(html)]
    lines = [int(x) for x in LINE.findall(html)]
    for c in strips:
        if c < N:
            raise GateError("DESK_HONEST", f"a desk renders a full strip with only {c} cards (< {N})")
    for c in lines:
        if c >= N:
            raise GateError("DESK_HONEST", f"a desk with {c} cards (>= {N}) collapsed to a line")
    return len(titles), len(strips), len(lines)


def main():
    if not INDEX.exists():
        print("verify_frontpage: index.html missing"); sys.exit(2)
    html = INDEX.read_text(encoding="utf-8")
    articled = {v for v in json.loads(MAP.read_bytes())["map"].values() if v}
    try:
        ncards, nstrip, nline = check(html, articled)
    except GateError as e:
        print(f"FRONTPAGE GATE FAIL — {e}"); sys.exit(2)
    print(f"FRONTPAGE GATE PASS: {ncards} desk-cards · {nstrip} strip + {nline} honest line(s) · "
          f"0 event shown twice (E/D deduped via explicit map)")


if __name__ == "__main__":
    main()
