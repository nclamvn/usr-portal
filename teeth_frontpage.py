#!/usr/bin/env python3
"""Teeth for the front-page gate — prove DEDUP and DESK_HONEST each bite."""
import json, re, sys
import verify_frontpage as V


def _bit(html, articled, want):
    try:
        V.check(html, articled); return False, "NO BITE"
    except V.GateError as e:
        return e.gate == want, e.gate


def main():
    if not V.INDEX.exists():
        print("teeth_frontpage: index.html missing"); sys.exit(2)
    clean = V.INDEX.read_text(encoding="utf-8")
    articled = {v for v in json.loads(V.MAP.read_bytes())["map"].values() if v}
    ok = True
    try:
        V.check(clean, articled); print(f"{'CLEAN (positive control)':30s} : PASS")
    except V.GateError as e:
        print(f"{'CLEAN (positive control)':30s} : !! {e}"); ok = False

    # bite 1 — DEDUP: rename a D-card to an articled entity (event would show twice)
    target = sorted(articled)[0]
    bad = re.sub(r'(<h3 class="rcard-t">(?:<a[^>]*>|<span>)).*?((?:</a>|</span>)</h3>)',
                 r'\1' + target.replace('\\', '\\\\') + r'\2', clean, count=1, flags=re.S)
    bit, g = _bit(bad, articled, "DEDUP")
    print(f"{'DEDUP (card == articled event)':30s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}"); ok = ok and bit

    # bite 2 — DESK_HONEST: force a strip to claim < N cards
    bad2 = re.sub(r'(<section class="fp-desk" data-mode="strip" data-n=")\d+(")', r'\g<1>2\2', clean, count=1)
    bit, g = _bit(bad2, articled, "DESK_HONEST")
    print(f"{'DESK_HONEST (thin strip)':30s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}"); ok = ok and bit

    print("-" * 54)
    print("FRONTPAGE TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
