#!/usr/bin/env python3
"""Shared global nav (breadcrumb). Every surface gets the same top-left nav so Home (USR) and the
main surfaces are always one click away — no dead-end pages. Reused by every builder; styling lives
in design-system.css (.crumb), so no per-page CSS drift."""


def _bi(en, vn):
    return f'<span data-lang-en>{en}</span><span data-lang-vn>{vn}</span>'


# (key, file, en, vn) — the breadcrumb surfaces. "home" is NOT here: the wordmark (header.py) is the
# single home link, so a "USR" nav item would be a confusing second link to the same place.
ITEMS = [
    ("reference", "reference.html", "Reference", "Tham chiếu"),
    ("compare", "compare.html", "Compare", "So sánh"),
    ("data", "data.html", "Data", "Dữ liệu"),
    ("knowledge", "knowledge.html", "Knowledge", "Thuật ngữ"),
    ("review", "review.html", "Review", "Đánh giá"),
    ("newsroom", "news.html", "Newsroom", "Bài viết"),
    ("monitor", "monitor.html", "Monitor", "Bản đồ"),
]


def nav(prefix="", current=None):
    """prefix: "" for root pages, "../" for subdir pages (uav/company/country/segment).
    current: the key of the page you're on (rendered as non-link), or None (all are links)."""
    parts = []
    for key, fname, en, vn in ITEMS:
        cls = ' class="wm"' if key == "home" else ""
        if key == current:
            parts.append(f'<span class="cur"{cls}>{_bi(en, vn)}</span>')
        else:
            parts.append(f'<a href="{prefix}{fname}"{cls}>{_bi(en, vn)}</a>')
    return '<nav class="crumb">' + '<span class="sep">·</span>'.join(parts) + '</nav>'
