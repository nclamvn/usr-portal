#!/usr/bin/env python3
"""TIP-002 — Data adapter.

Reads out/master_registry.json (read-only) and emits out/site-data.json:
each REAL entity (provenance_class != own_product) with display + spec fields,
every field carrying {value, status, source_tier, confidence} taken from the
real Cell. unverified / missing -> value: null (honest null, never fabricated).
Idempotent: same input bytes -> byte-identical output.

GLOBAL CONSTRAINTS honoured:
  1 data integrity — only real Cell values; unverified -> null; no fabrication.
  6 reuse, not rebuild — reads the registry, never writes it.
  8 totals computed live — `aggregates` recomputed here from the data, not hardcoded.
"""
import json, hashlib, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
MASTER = ROOT / "out" / "master_registry.json"
OUT = ROOT / "out" / "site-data.json"

DISPLAY_FIELDS = ["manufacturer", "manufacturer_country", "family", "name",
                  "variant", "airframe_type", "propulsion", "market_segment",
                  "live_status"]
# provenance_class is entity metadata (a top-level string), NOT a per-field Cell —
# it stays as ent["provenance_class"], rendered via friendly labels below.
SPEC_FIELDS = ["mtow_kg", "max_payload_kg", "endurance_min", "max_range_km",
               "max_link_km", "max_speed_ms", "service_ceiling_m",
               "encryption", "blue_uas", "ndaa_compliant", "gps_denied_capable"]

# Bilingual labels — field names + enum values. EN / VN.
LABELS = {
    "field": {
        "manufacturer": {"en": "Manufacturer", "vn": "Nhà sản xuất"},
        "manufacturer_country": {"en": "Country", "vn": "Quốc gia"},
        "family": {"en": "Family", "vn": "Dòng"},
        "name": {"en": "Model", "vn": "Mẫu"},
        "variant": {"en": "Variant", "vn": "Biến thể"},
        "airframe_type": {"en": "Airframe", "vn": "Khung bay"},
        "propulsion": {"en": "Propulsion", "vn": "Động lực"},
        "market_segment": {"en": "Segment", "vn": "Phân khúc"},
        "provenance_class": {"en": "Class", "vn": "Lớp"},
        "live_status": {"en": "Status", "vn": "Tình trạng"},
        "mtow_kg": {"en": "MTOW (kg)", "vn": "Khối lượng cất cánh tối đa (kg)"},
        "max_payload_kg": {"en": "Max payload (kg)", "vn": "Tải tối đa (kg)"},
        "endurance_min": {"en": "Endurance (min)", "vn": "Thời gian bay (phút)"},
        "max_range_km": {"en": "Max range (km)", "vn": "Tầm bay (km)"},
        "max_link_km": {"en": "Datalink range (km)", "vn": "Tầm truyền (km)"},
        "max_speed_ms": {"en": "Max speed (m/s)", "vn": "Tốc độ tối đa (m/s)"},
        "service_ceiling_m": {"en": "Service ceiling (m)", "vn": "Trần bay (m)"},
        "encryption": {"en": "Encryption", "vn": "Mã hoá"},
        "blue_uas": {"en": "Blue UAS", "vn": "Blue UAS"},
        "ndaa_compliant": {"en": "NDAA compliant", "vn": "Tuân thủ NDAA"},
        "gps_denied_capable": {"en": "GPS-denied capable", "vn": "Bay trong môi trường mất GPS"},
    },
    "status": {
        "verified": {"en": "Verified", "vn": "Đã kiểm chứng"},
        "unverified": {"en": "Unverified", "vn": "Chưa kiểm chứng"},
        "derived": {"en": "Derived", "vn": "Suy ra (L2)"},
        "disputed": {"en": "Disputed", "vn": "Bất đồng nguồn"},
        "inherited": {"en": "Inherited", "vn": "Kế thừa"},
    },
    "bool": {True: {"en": "Yes", "vn": "Có"}, False: {"en": "No", "vn": "Không"}},
    "segment": {  # market_segment value -> friendly label
        "military_tactical": {"en": "Military · tactical", "vn": "Quân sự · chiến thuật"},
        "defense_government": {"en": "Defense · government", "vn": "Quốc phòng · chính phủ"},
        "enterprise": {"en": "Enterprise", "vn": "Doanh nghiệp"},
        "consumer": {"en": "Consumer", "vn": "Tiêu dùng"},
        "agriculture": {"en": "Agriculture", "vn": "Nông nghiệp"},
        "delivery": {"en": "Delivery", "vn": "Giao hàng"},
        "passenger_uam": {"en": "Passenger air taxi", "vn": "Taxi bay"},
        "surveying": {"en": "Surveying & mapping", "vn": "Khảo sát · lập bản đồ"},
        "public_safety": {"en": "Public safety", "vn": "An toàn công cộng"},
        "loitering_munition": {"en": "Loitering munition", "vn": "Đạn tuần kích"},
        "fpv": {"en": "FPV", "vn": "FPV"},
        "cinema": {"en": "Cinema", "vn": "Điện ảnh"},
        "counter_uas": {"en": "Counter-UAS", "vn": "Chống UAV"},
        "isr": {"en": "ISR / reconnaissance", "vn": "Trinh sát (ISR)"},
    },
    "klass": {  # provenance_class value -> friendly label (compliance posture)
        "blue_public": {"en": "Blue UAS cleared", "vn": "Blue UAS"},
        "commercial_us_public": {"en": "Commercial · US", "vn": "Thương mại · Mỹ"},
        "commercial_covered_public": {"en": "Commercial · covered", "vn": "Thương mại · covered"},
        "commercial_noncovered_public": {"en": "Commercial · allied", "vn": "Thương mại · đồng minh"},
        "competitor_military_public": {"en": "Military", "vn": "Quân sự"},
        "military_noncovered_public": {"en": "Military · allied", "vn": "Quân sự · đồng minh"},
        "own_product": {"en": "RtR product", "vn": "Sản phẩm RtR"},
    },
}

TIER_RANK = {"A": 0, "B": 1, "C": 2}

# DECISION D-1 — explicit, TOTAL airframe_type -> frame_glyph map. Unknown/unmapped -> "unknown".
# 'multirotor' is generic (no rotor count) -> "multirotor"; NEVER quad/hexa/octo (would invent count).
# fixed-wing/fixed_wing normalised to "fixed" ONLY here (the raw airframe_type is left untouched).
AIRFRAME_GLYPH = {
    "quadcopter": "quad", "hexacopter": "hexa", "octocopter": "octo",
    "multirotor": "multirotor",
    "fixed-wing": "fixed", "fixed_wing": "fixed",
    "vtol_fixedwing": "vtol", "helicopter": "heli", "ducted-fan": "ducted",
}


def best_source_tier(cell):
    """Best (A>B>C) source tier on a cell, or the raw tier (e.g. 'derived'), or None."""
    srcs = cell.get("sources") or []
    abc = [s.get("tier") for s in srcs if s.get("tier") in TIER_RANK]
    if abc:
        return min(abc, key=lambda t: TIER_RANK[t])
    raw = [s.get("tier") for s in srcs if s.get("tier")]
    return raw[0] if raw else None


def field_obj(cell):
    """Project a Cell to {value, status, source_tier, confidence, flags}.
    unverified or absent -> value null. Never invents a value."""
    if cell is None:
        return {"value": None, "status": None, "source_tier": None, "confidence": None}
    status = cell.get("status")
    value = cell.get("value")
    if status == "unverified":          # AC: unverified -> null, no exceptions
        value = None
    obj = {"value": value, "status": status,
           "source_tier": best_source_tier(cell), "confidence": cell.get("confidence")}
    # provenance apparatus: keep the real source URLs + tiers for the detail page (every number
    # traces to its source). Honest-null cells keep their attempted sources too; never invented.
    srcs = [{"url": s.get("url"), "tier": s.get("tier"), "retrieved": s.get("retrieved")}
            for s in (cell.get("sources") or []) if s.get("url")]
    if srcs:
        obj["sources"] = srcs
    if cell.get("inherited_from") is not None:
        obj["inherited_from"] = cell["inherited_from"]
    if status == "disputed":
        obj["disputed"] = True
        # keep the competing claims visible (provenance-forward), never pick one
        obj["claims"] = [{"tier": s.get("tier"), "claimed_value": s.get("claimed_value"),
                          "url": s.get("url")} for s in (cell.get("sources") or [])]
    return obj


def build(master):
    fam_by_id = {f["family_id"]: f for f in master["families"]}
    entities = []
    for v in master["variants"]:
        if v.get("provenance_class") == "own_product":
            continue  # scaffolds (pending internal) are not public reference entities
        fam_cells = fam_by_id.get(v["family_id"], {}).get("cells", {})
        eff = {**fam_cells, **v.get("cells", {})}  # variant overrides family
        # Flat shape: each field-cell is a DIRECT child of the entity, keyed canonical_id.
        # (Matches the independent auditor's contract; UI groups via field_groups below.)
        ent = {"canonical_id": v["canonical_id"],
               "slug": re.sub(r"[^a-z0-9]+", "-", v["canonical_id"].lower()).strip("-"),
               "family_id": v["family_id"], "provenance_class": v.get("provenance_class")}
        for f in DISPLAY_FIELDS + SPEC_FIELDS:
            ent[f] = field_obj(eff.get(f))
        # derived (L2) frame glyph — suy ra từ airframe_type, total map, honest "unknown" fallback
        ent["frame_glyph"] = AIRFRAME_GLYPH.get(ent["airframe_type"].get("value")) or "unknown"
        entities.append(ent)
    entities.sort(key=lambda e: e["canonical_id"])  # deterministic order -> idempotent

    # CONSTRAINT 8: aggregates computed live, counting field-cells exactly as the
    # auditor does (every {value,status} child, status stringified incl. None).
    status_counts, tier_counts, fill, ranges = {}, {}, {}, {}
    for e in entities:
        for f in DISPLAY_FIELDS + SPEC_FIELDS:
            fo = e[f]
            key = str(fo["status"])
            status_counts[key] = status_counts.get(key, 0) + 1
            t = fo["source_tier"]
            if t:
                tier_counts[t] = tier_counts.get(t, 0) + 1
            if f in SPEC_FIELDS:
                fill.setdefault(f, {"present": 0, "total": 0})
                fill[f]["total"] += 1
                v = fo["value"]
                if v is not None:
                    fill[f]["present"] += 1
                # spec_range: live min/max over numeric values (TIP-P03 — micro-track log scale)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    r = ranges.setdefault(f, {"min": v, "max": v})
                    r["min"] = min(r["min"], v)
                    r["max"] = max(r["max"], v)
    return {
        "schema": "site-data/1",
        "source_registry_sha256": hashlib.sha256(
            json.dumps(master, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "labels": LABELS,
        "field_groups": {"display": DISPLAY_FIELDS, "spec": SPEC_FIELDS},
        "aggregates": {  # live — recomputed every build
            "entity_count": len(entities),
            "field_status_counts": status_counts,
            "source_tier_counts": tier_counts,
            "spec_fill_rate": fill,
            "spec_range": ranges,
        },
        "entities": entities,
    }


def main():
    master = json.loads(MASTER.read_bytes())
    site = build(master)
    # sort_keys -> stable; LABELS bool keys (True/False) need string coercion for JSON
    OUT.write_text(json.dumps(site, sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    print(f"site-data.json: {site['aggregates']['entity_count']} entities | "
          f"status {site['aggregates']['field_status_counts']}")


if __name__ == "__main__":
    main()
