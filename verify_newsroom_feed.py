#!/usr/bin/env python3
"""TIP-NEWSROOM gates — the two teeth that keep "tin có hình" from sliding into "mượn/bịa ảnh".

  FIGURE_PROVENANCE — news.html carries NO borrowed image: no external <img> hotlink, no external
    url() background, no <img> that is not a local asset; every figure is an inline <svg class="nf-svg">.
  NEWSROOM_SOURCED — the lead and every secondary carry a source + tier badge (provenance at the top).

Both scan the RENDERED news.html (the real artifact), so the teeth bite on output, not on intent.
Functions are importable by teeth_newsroom_feed.py.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
NEWS = ROOT / "news.html"

EXT_IMG = re.compile(r'<img\b[^>]*\bsrc\s*=\s*["\']https?://', re.I)
EXT_URL = re.compile(r'url\(\s*["\']?https?://', re.I)
IMG_TAG = re.compile(r'<img\b[^>]*>', re.I)
LEAD_RE = re.compile(r'<article class="lead">.*?</article>', re.S)
SEC_RE = re.compile(r'<article class="sec">.*?</article>', re.S)
MROW_RE = re.compile(r'<article class="mrow">.*?</article>', re.S)


class GateError(Exception):
    def __init__(self, gate, msg):
        super().__init__(f"{gate}: {msg}")
        self.gate = gate


def check_figure_provenance(html):
    """No borrowed imagery anywhere in the feed; figures are inline SVG only."""
    if EXT_IMG.search(html):
        raise GateError("FIGURE_PROVENANCE", "external <img> hotlink found (borrowed image)")
    if EXT_URL.search(html):
        raise GateError("FIGURE_PROVENANCE", "external url() image reference found")
    for m in IMG_TAG.finditer(html):
        tag = m.group(0)
        if 'src="base/' not in tag:                       # only the local brand asset is allowed
            raise GateError("FIGURE_PROVENANCE", f"non-asset <img> found: {tag[:60]}")
    nsvg = html.count('class="nf-svg"')
    if nsvg < 3:
        raise GateError("FIGURE_PROVENANCE", f"feed has only {nsvg} inline figures (expected one per item)")
    return nsvg


def check_newsroom_sourced(html):
    """Lead + every secondary must carry a source+tier badge (provenance at the head of each item)."""
    lead = LEAD_RE.search(html)
    if not lead:
        raise GateError("NEWSROOM_SOURCED", "no lead article found")
    if 'class="tier' not in lead.group(0):
        raise GateError("NEWSROOM_SOURCED", "lead has no source/tier badge")
    secs = SEC_RE.findall(html)
    if len(secs) < 2:
        raise GateError("NEWSROOM_SOURCED", f"expected >=2 secondary, found {len(secs)}")
    for i, s in enumerate(secs):
        if 'class="tier' not in s:
            raise GateError("NEWSROOM_SOURCED", f"secondary #{i+1} has no source/tier badge")
    # the "More" tail must NOT go loose on provenance — every river row carries source+tier too
    for i, m in enumerate(MROW_RE.findall(html)):
        if 'class="tier' not in m:
            raise GateError("NEWSROOM_SOURCED", f"More row #{i+1} has no source/tier badge")
    return len(secs)


def main():
    if not NEWS.exists():
        print("verify_newsroom_feed: news.html missing — run build_newsroom.py first"); sys.exit(2)
    html = NEWS.read_text(encoding="utf-8")
    try:
        nsvg = check_figure_provenance(html)
        nsec = check_newsroom_sourced(html)
    except GateError as e:
        print(f"NEWSROOM-FEED GATE FAIL — {e}"); sys.exit(2)
    print(f"NEWSROOM-FEED GATE PASS: {nsvg} inline figures · lead+{nsec} secondary all sourced · 0 borrowed image")


if __name__ == "__main__":
    main()
