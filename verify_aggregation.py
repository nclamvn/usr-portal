#!/usr/bin/env python3
"""verify_aggregation.py — TIP-NEWS-REALTIME Task 3 (gate dòng A, fail-loud exit 2).

Aggregation card = link + tóm-tắt-GỐC + outlet + tier. KHÔNG chép body/ảnh người ta. Bảy răng:
  AGG_SOURCE_MISSING   thiếu source_url hoặc outlet
  AGG_TIER_MISSING     tier ∉ {A,B,C}
  AGG_SUMMARY_VERBATIM summary > 240 ký-tự, HOẶC trùng verbatim ≥ 1 mệnh-đề (8-gram) với source_title
  AGG_THIRDPARTY_IMAGE image ≠ null (ảnh card phải qua media.json/tường-quyền, không nhúng trần)
  AGG_OPINION_NOHUMAN  summary mang luận-điểm/đặc-tả mà human_author rỗng
  AGG_TAG_DANGLING     entity_tags 'kind:id' trỏ thực-thể/knowledge không có trong graph
  AGG_STRATUM_BAD      stratum ∉ {vietnam, world, china}
"""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "content" / "news-cards.json"
SITE = ROOT / "out" / "site-data.json"
GLOSS = ROOT / "content" / "glossary.json"

VALID_TIER = {"A", "B", "C"}
VALID_STRATUM = {"vietnam", "world", "china"}
# Marker đặc-tả/luận-điểm — bảo-thủ (factual reporting không dính): chỉ khen/chê/quả-quyết rõ-ràng của CARD.
OPINION_RE = re.compile(r"(tuyệt vời|xuất sắc|vượt trội|thất bại|tệ hại|đáng thất vọng|"
                        r"chắc chắn sẽ|sẽ thống trị|không thể phủ nhận|rõ ràng là|đáng tiếc|tồi tệ)", re.I)


class GateError(Exception):
    def __init__(self, gate, msg):
        self.gate = gate
        super().__init__(f"{gate}: {msg}")


def _words(s):
    return re.findall(r"[0-9a-zà-ỹ]+", (s or "").lower())


def _verbatim_clause(summary, title, n=8):
    """True nếu một chuỗi ≥ n từ liên-tiếp của title xuất-hiện nguyên trong summary (chép mệnh-đề)."""
    sw, tw = _words(summary), _words(title)
    if len(tw) < n:
        return False
    sj = " " + " ".join(sw) + " "
    for i in range(len(tw) - n + 1):
        if " " + " ".join(tw[i:i+n]) + " " in sj:
            return True
    return False


def check(doc, entity_slugs, gloss_terms):
    for c in doc.get("cards", []):
        cid = c.get("id") or c.get("source_url") or "?"
        if not c.get("source_url") or not c.get("outlet"):
            raise GateError("AGG_SOURCE_MISSING", f"card {cid!r}: thiếu source_url/outlet")
        if c.get("tier") not in VALID_TIER:
            raise GateError("AGG_TIER_MISSING", f"card {cid!r}: tier {c.get('tier')!r} ∉ A/B/C")
        summ = c.get("summary") or ""
        if len(summ) > 240:
            raise GateError("AGG_SUMMARY_VERBATIM", f"card {cid!r}: summary {len(summ)} ký-tự > 240")
        if _verbatim_clause(summ, c.get("source_title", "")):
            raise GateError("AGG_SUMMARY_VERBATIM", f"card {cid!r}: summary chép ≥1 mệnh-đề verbatim từ source_title")
        if c.get("image") is not None:
            raise GateError("AGG_THIRDPARTY_IMAGE", f"card {cid!r}: image≠null — ảnh card phải qua media.json (tường-quyền), không nhúng trần")
        if OPINION_RE.search(summ) and not c.get("human_author"):
            raise GateError("AGG_OPINION_NOHUMAN", f"card {cid!r}: summary mang luận-điểm/đặc-tả mà không human_author")
        for t in c.get("entity_tags") or []:
            if ":" in t:
                kind, ident = t.split(":", 1)
                ok = (ident in gloss_terms) if kind == "knowledge" else (ident in entity_slugs or t in entity_slugs)
                if not ok:
                    raise GateError("AGG_TAG_DANGLING", f"card {cid!r}: entity_tag {t!r} không có trong graph/glossary")
        if c.get("stratum") not in VALID_STRATUM:
            raise GateError("AGG_STRATUM_BAD", f"card {cid!r}: stratum {c.get('stratum')!r} ∉ vietnam/world/china")
    return len(doc.get("cards", []))


def main():
    if not CARDS.exists():
        print("verify_aggregation: news-cards.json chưa có — bỏ qua (0 card)"); return
    doc = json.loads(CARDS.read_text(encoding="utf-8"))
    site = json.loads(SITE.read_bytes())
    slugs = {e["slug"] for e in site.get("entities", [])}
    gloss = set(json.loads(GLOSS.read_bytes()).get("terms", {}).keys())
    try:
        n = check(doc, slugs, gloss)
    except GateError as e:
        print(f"\nAGGREGATION FAIL:\n  - {e}"); sys.exit(2)
    print(f"AGGREGATION PASS: {n} card dòng A · source+tier đủ · summary gốc ≤240 · 0 ảnh nhúng trần · tag resolve.")


if __name__ == "__main__":
    main()
