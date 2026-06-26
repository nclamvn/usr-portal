#!/usr/bin/env python3
"""TIP-FP1.5 gate — the LAE registry ingested from refinery must NOT flatten the provenance the
REF1–4 work built: every field carries source+tier, and DISPUTED cells keep their competing claims
(never collapsed to one value). Scans the committed content/lae-registry.json (the real artifact)."""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
REG = ROOT / "content" / "lae-registry.json"


class GateError(Exception):
    def __init__(self, gate, msg):
        super().__init__(f"{gate}: {msg}")
        self.gate = gate


def check(doc):
    ents = doc.get("entities", [])
    if len(ents) != doc.get("count"):
        raise GateError("COUNT_MISMATCH", f"declared {doc.get('count')} vs {len(ents)} entities")
    ndisp = 0
    for e in ents:
        if not e.get("entity_type") or not e.get("stratum"):
            raise GateError("HEAD_MISSING", f"{e.get('entity')!r}: entity_type/stratum missing")
        for f, c in (e.get("fields") or {}).items():
            srcs = c.get("sources") or []
            if not srcs or not all(s.get("tier") for s in srcs):
                raise GateError("PROVENANCE_FLATTENED",
                                f"{e['entity']!r}.{f}: field value with no sourced tier (flattened)")
            if c.get("state") == "disputed":
                ndisp += 1
                vals = {str(cl.get("value")) for cl in (c.get("claims") or [])}
                if len(vals) < 2:
                    raise GateError("DISPUTED_FLATTENED",
                                    f"{e['entity']!r}.{f}: disputed cell lost its competing claims")
    return len(ents), ndisp


def main():
    if not REG.exists():
        print("verify_lae_registry: content/lae-registry.json missing — run refinery/export_registry.py")
        sys.exit(2)
    doc = json.loads(REG.read_text(encoding="utf-8"))
    try:
        n, nd = check(doc)
    except GateError as e:
        print(f"LAE-REGISTRY GATE FAIL — {e}")
        sys.exit(2)
    print(f"LAE-REGISTRY GATE PASS: {n} entities ingested · every field carries source+tier "
          f"(no flatten) · {nd} disputed cell(s) kept whole")


if __name__ == "__main__":
    main()
