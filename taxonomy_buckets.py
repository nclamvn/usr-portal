#!/usr/bin/env python3
"""Derived-axis taxonomy buckets (TIP-TAXONOMY §1). Weight (mtow_kg) + flight-time (endurance_min):
thresholds are FIXED; membership recomputes LIVE from the numeric value — no hardcoded entity lists.
An entity whose field is null/non-numeric belongs to NO bucket (honest-null), never dumped into 'other'.
Shared by build_taxonomy (group), build_detail (entity->bucket link), verify_taxonomy (recompute)."""

INF = float("inf")

# (slug, en, vn, lo, hi) — half-open [lo, hi)
WEIGHT_BUCKETS = [
    ("nano",   "< 0.5 kg",   "< 0,5 kg",   0,    0.5),
    ("micro",  "0.5-2 kg",   "0,5-2 kg",   0.5,  2),
    ("small",  "2-25 kg",    "2-25 kg",    2,    25),
    ("medium", "25-150 kg",  "25-150 kg",  25,   150),
    ("large",  "150-600 kg", "150-600 kg", 150,  600),
    ("heavy",  "> 600 kg",   "> 600 kg",   600,  INF),
]

FLIGHT_BUCKETS = [
    ("under-30", "< 30 min",  "< 30 phut",  0,    30),
    ("30-60",    "30-60 min", "30-60 phut", 30,   60),
    ("1-2h",     "1-2 h",     "1-2 gio",    60,   120),
    ("2-6h",     "2-6 h",     "2-6 gio",    120,  360),
    ("over-6h",  "> 6 h",     "> 6 gio",    360,  INF),
]

# compliance axis: boolean field -> term page; ONLY value True qualifies (false & null are NOT listed)
COMPLIANCE = [
    ("ndaa",     "ndaa_compliant", "NDAA compliant", "Tuan thu NDAA"),
    ("blue-uas", "blue_uas",       "Blue UAS",       "Blue UAS"),
]


def _bucket(value, buckets):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    for slug, en, vn, lo, hi in buckets:
        if lo <= value < hi:
            return slug
    return None


def weight_bucket(v):
    return _bucket(v, WEIGHT_BUCKETS)


def flight_bucket(v):
    return _bucket(v, FLIGHT_BUCKETS)
