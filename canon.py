#!/usr/bin/env python3
"""TIP-P1.2 — shared canonicalization (single source for adapter + auditor + graph + detail).
  · company alias-map (merge same-legal-entity manufacturer strings) — data-driven, auditable.
  · country normalize — declared hygiene map to ONE canonical English vocabulary (matches the 28
    other English country values). NOT fabrication; the auditor proves the map is applied.
VN display labels for country are deferred to a presentation-layer label-map (not the data value)."""
import json, pathlib, re

_ROOT = pathlib.Path(__file__).resolve().parent
ALIAS = json.loads((_ROOT / "content" / "company_aliases.json").read_bytes()).get("aliases", {})

# country canonical EN — engine-scanned: exactly two multi-variant clusters in the registry.
COUNTRY_CANON = {"US": "United States", "USA": "United States", "United States": "United States",
                 "UK": "United Kingdom", "United Kingdom": "United Kingdom"}


def canonical_name(mfr):
    """Manufacturer string -> canonical company display name (alias-merged)."""
    return ALIAS.get(mfr, mfr) if mfr else None


def canonical_slug(mfr):
    name = canonical_name(mfr)
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") if name else None


def canon_country(c):
    return COUNTRY_CANON.get(c, c)
