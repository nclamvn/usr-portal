#!/usr/bin/env python3
"""Teeth for the LAE-registry ingest gate — prove it bites the two flattening faults it guards."""
import json, sys, copy, pathlib
import verify_lae_registry as V

REG = V.REG


def _bit(doc, want):
    try:
        V.check(doc)
        return False, "NO BITE"
    except V.GateError as e:
        return e.gate == want, e.gate


def main():
    if not REG.exists():
        print("teeth_lae_registry: lae-registry.json missing"); sys.exit(2)
    clean = json.loads(REG.read_text(encoding="utf-8"))
    ok = True

    try:
        V.check(clean); print(f"{'CLEAN (positive control)':36s} : PASS")
    except V.GateError as e:
        print(f"{'CLEAN (positive control)':36s} : !! {e}"); ok = False

    # bite 1 — flatten a field's provenance (value kept, sources stripped)
    d1 = copy.deepcopy(clean)
    for e in d1["entities"]:
        if e["fields"]:
            f = next(iter(e["fields"])); e["fields"][f]["sources"] = []; break
    bit, g = _bit(d1, "PROVENANCE_FLATTENED")
    print(f"{'PROVENANCE_FLATTENED (strip sources)':36s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}")
    ok = ok and bit

    # bite 2 — collapse a disputed cell to a single claim
    d2 = copy.deepcopy(clean)
    hit = False
    for e in d2["entities"]:
        for f, c in e["fields"].items():
            if c.get("state") == "disputed":
                c["claims"] = (c.get("claims") or [])[:1]; hit = True; break
        if hit:
            break
    if hit:
        bit, g = _bit(d2, "DISPUTED_FLATTENED")
        print(f"{'DISPUTED_FLATTENED (collapse claims)':36s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+g+']'}")
        ok = ok and bit
    else:
        print(f"{'DISPUTED_FLATTENED':36s} : N/A (no disputed cell)")

    print("-" * 60)
    print("LAE-REGISTRY TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
