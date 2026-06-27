#!/usr/bin/env python3
"""build_aggregation.py — TIP-NEWS-REALTIME Task 2 (render dòng A).

Render aggregation card (link + tóm-tắt-gốc + outlet + tier + ngày + link-ngoài) thành section
"Tin nhanh". KHÔNG nhúng body/ảnh người ta — chỉ tiêu-đề-gốc + tóm-tắt CỦA TA + nút về nguồn.
Gác bởi verify_aggregation.py (7 teeth). Hàm aggregation_block() dùng cho trang chủ + news.html."""
import json
from pathlib import Path
from build_reference import bilingual, esc

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "content" / "news-cards.json"


def load_cards():
    if not CARDS.exists():
        return []
    return json.loads(CARDS.read_text(encoding="utf-8")).get("cards", [])


def _sorted(cards):
    # ngày giảm dần; null-date xuống cuối (honest-null, không bịa ngày)
    return sorted(cards, key=lambda c: (c.get("date") or "0000-00-00"), reverse=True)


def _card_html(c):
    url = esc(c.get("source_url", ""))
    tier = esc(str(c.get("tier", "?")))
    date = esc(c.get("date") or "")
    datespan = f'<span class="agg-date">{date}</span> · ' if date else ""
    return (
        '<article class="agg-card">'
        f'<span class="agg-field">{esc(c.get("field",""))}</span>'
        f'<h4 class="agg-ttl"><a href="{url}" target="_blank" rel="noopener">{esc(c.get("source_title",""))}</a></h4>'
        f'<p class="agg-sum">{esc(c.get("summary",""))}</p>'
        f'<div class="agg-meta"><span class="agg-outlet">{esc(c.get("outlet",""))}</span> · '
        f'<span class="tier{"" if tier.startswith("A") else " bb"}">tier {tier}</span> · '
        f'{datespan}<a class="agg-src" href="{url}" target="_blank" rel="noopener">{bilingual("source","nguồn")} ↗</a></div>'
        '</article>')


def aggregation_block(prefix="", limit=12):
    """Section 'Tin nhanh' — N card mới nhất. Rỗng-string nếu chưa có card (site-null, không khung trống)."""
    cards = _sorted(load_cards())[:limit]
    if not cards:
        return ""
    items = "".join(_card_html(c) for c in cards)
    return (
        '<section class="aggwrap" data-audit="agg">'
        '<div class="agg-head">'
        f'<b class="agg-kicker">{bilingual("Quick headlines · link + sourced summary", "Tin nhanh · link + tóm-tắt có nguồn")}</b>'
        f'<span class="agg-count">{len(cards)}</span>'
        '</div>'
        f'<div class="agg-grid">{items}</div>'
        '</section>')


if __name__ == "__main__":
    cards = load_cards()
    print(f"aggregation: {len(cards)} card · block render {min(len(cards),12)} mới nhất")
