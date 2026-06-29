#!/usr/bin/env python3
"""Teeth for the front-page gate — prove DEDUP and DESK_HONEST each bite. Self-contained: tests
V.check() on SYNTHETIC markup, so it stays valid even though the homepage no longer renders the
registry-desks block (TIP-HOMEPAGE dropped it for REPORT/03). If desks return, this still guards them."""
import json, sys
import verify_frontpage as V


def _bit(html, articled, want):
    try:
        V.check(html, articled); return False, "NO BITE"
    except V.GateError as e:
        return e.gate == want, e.gate


def main():
    articled = {v for v in json.loads(V.MAP.read_bytes())["map"].values() if v}
    target = sorted(articled)[0]
    ok = True

    # clean positive control — a healthy strip (>= N) + a non-articled card
    clean = (f'<section class="fp-desk" data-mode="strip" data-n="{V.N}">'
             f'<h3 class="rcard-t"><span>__not_an_articled_event__</span></h3></section>')
    try:
        V.check(clean, articled); print(f"{'CLEAN (positive control)':30s} : PASS")
    except V.GateError as e:
        print(f"{'CLEAN (positive control)':30s} : !! {e}"); ok = False

    # bite 1 — DEDUP: a D-card titled as an articled event (would show the event twice)
    dedup = f'<h3 class="rcard-t"><span>{target}</span></h3>'
    bit, g = _bit(dedup, articled, "DEDUP")
    print(f"{'DEDUP (card == articled event)':30s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}"); ok = ok and bit

    # bite 2 — DESK_HONEST: a strip claiming < N cards
    thin = '<section class="fp-desk" data-mode="strip" data-n="2">'
    bit, g = _bit(thin, articled, "DESK_HONEST")
    print(f"{'DESK_HONEST (thin strip)':30s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}"); ok = ok and bit

    print("-" * 54)
    print("FRONTPAGE TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
