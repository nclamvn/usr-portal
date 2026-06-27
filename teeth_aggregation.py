#!/usr/bin/env python3
"""Teeth cho verify_aggregation — chứng cả 7 răng CẮN. Mỗi bite: deepcopy doc sạch → tiêm đúng một lỗi →
kỳ-vọng GateError đúng gate. Doctrine: cổng chưa chứng biết cắn thì chưa được tin."""
import copy, json, sys
from pathlib import Path
import verify_aggregation as V

ROOT = Path(__file__).resolve().parent


def _bit(doc, slugs, gloss, want):
    try:
        V.check(doc, slugs, gloss); return False, "NO BITE"
    except V.GateError as e:
        return e.gate == want, e.gate


def main():
    doc = json.loads((ROOT / "content" / "news-cards.json").read_text(encoding="utf-8"))
    site = json.loads((ROOT / "out" / "site-data.json").read_bytes())
    slugs = {e["slug"] for e in site.get("entities", [])}
    gloss = set(json.loads((ROOT / "content" / "glossary.json").read_bytes()).get("terms", {}).keys())
    ok = True
    try:
        V.check(doc, slugs, gloss); print(f"{'CLEAN (positive control)':30s} : PASS")
    except V.GateError as e:
        print(f"{'CLEAN (positive control)':30s} : !! {e}"); ok = False

    def bite(name, mut):
        nonlocal ok
        d = copy.deepcopy(doc); mut(d["cards"][0])
        bit, got = _bit(d, slugs, gloss, name)
        ok = ok and bit
        print(f"{name:30s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ['+got+']'}")

    bite("AGG_SOURCE_MISSING",   lambda c: c.update(source_url=""))
    bite("AGG_TIER_MISSING",     lambda c: c.update(tier="Z"))
    bite("AGG_SUMMARY_VERBATIM", lambda c: c.update(summary="x" * 241))
    bite("AGG_THIRDPARTY_IMAGE", lambda c: c.update(image="https://example.com/stolen.jpg"))
    bite("AGG_OPINION_NOHUMAN",  lambda c: c.update(summary="Đây là bước tiến tuyệt vời, chắc chắn sẽ thống trị thị trường."))
    bite("AGG_TAG_DANGLING",     lambda c: c.update(entity_tags=["entity:khong-ton-tai-xyz"]))
    bite("AGG_STRATUM_BAD",      lambda c: c.update(stratum="mars"))

    print("-" * 56)
    print("AGGREGATION TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
