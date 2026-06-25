#!/usr/bin/env python3
"""Teeth for the TIP-NEWSROOM gates — prove each bites by injecting the exact fault it guards.

  FIGURE_PROVENANCE: inject a borrowed <img> hotlink → must be caught.
  NEWSROOM_SOURCED: strip the tier badge from the lead → must be caught.
"""
import sys, pathlib
import verify_newsroom_feed as V

ROOT = pathlib.Path(__file__).resolve().parent
NEWS = ROOT / "news.html"


def _bit(fn, html, want_gate):
    try:
        fn(html)
        return False, "NO BITE (gate passed faulty input)"
    except V.GateError as e:
        return (e.gate == want_gate), e.gate


def main():
    if not NEWS.exists():
        print("teeth_newsroom_feed: news.html missing"); sys.exit(2)
    clean = NEWS.read_text(encoding="utf-8")
    ok = True

    # positive control — clean output passes both
    try:
        V.check_figure_provenance(clean); V.check_newsroom_sourced(clean)
        print(f"{'CLEAN (positive control)':40s} : PASS")
    except V.GateError as e:
        print(f"{'CLEAN (positive control)':40s} : !! {e}"); ok = False

    # bite 1 — borrowed image injected
    bad = clean.replace("</main>", '<img src="https://example.com/stolen.jpg"></main>', 1)
    bit, g = _bit(V.check_figure_provenance, bad, "FIGURE_PROVENANCE")
    print(f"{'FIGURE_PROVENANCE (borrowed <img>)':40s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}")
    ok = ok and bit

    # bite 2 — lead stripped of its source/tier badge
    lead = V.LEAD_RE.search(clean).group(0)
    stripped = lead.replace('class="tier', 'class="xtier')          # break the badge marker in the lead only
    bad2 = clean.replace(lead, stripped, 1)
    bit, g = _bit(V.check_newsroom_sourced, bad2, "NEWSROOM_SOURCED")
    print(f"{'NEWSROOM_SOURCED (lead no source)':40s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}")
    ok = ok and bit

    print("-" * 60)
    print("NEWSROOM-FEED TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
