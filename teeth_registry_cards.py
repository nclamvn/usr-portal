#!/usr/bin/env python3
"""Teeth for the registry-card gate — prove it bites prose-injection and provenance loss."""
import json, re, sys, pathlib
import verify_registry_cards as V


def _bit(html, names, want):
    try:
        V.check(html, names); return False, "NO BITE"
    except V.GateError as e:
        return e.gate == want, e.gate


def main():
    if not V.REG.exists():
        print("teeth_registry_cards: registry.html missing"); sys.exit(2)
    clean = V.REG.read_text(encoding="utf-8")
    names = {e.get("name") or e["entity"] for e in json.loads(V.LAE.read_bytes())["entities"]}
    ok = True
    try:
        V.check(clean, names); print(f"{'CLEAN (positive control)':32s} : PASS")
    except V.GateError as e:
        print(f"{'CLEAN (positive control)':32s} : !! {e}"); ok = False

    # bite 1 — inject an AUTHORED title that maps to no field
    bad = re.sub(r'(<h3 class="rcard-t">(?:<a[^>]*>|<span>)).*?((?:</a>|</span>)</h3>)',
                 r'\1An invented editorial sentence about the future\2', clean, count=1, flags=re.S)
    bit, g = _bit(bad, names, "PROSE")
    print(f"{'PROSE (authored title)':32s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}"); ok = ok and bit

    # bite 2 — strip a card's source/tier
    bad2 = clean.replace('class="tier', 'class="xtier', 2)   # break tier markers in first card(s)
    bit, g = _bit(bad2, names, "UNSOURCED")
    print(f"{'UNSOURCED (strip tier)':32s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}"); ok = ok and bit

    print("-" * 56)
    print("REGISTRY-CARDS TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
