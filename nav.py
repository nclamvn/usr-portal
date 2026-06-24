#!/usr/bin/env python3
"""Shared global nav (breadcrumb). Every surface gets the same top-left nav so Home (USR) and the
main surfaces are always one click away — no dead-end pages. Reused by every builder; styling lives
in design-system.css (.crumb), so no per-page CSS drift."""


def _bi(en, vn):
    return f'<span data-lang-en>{en}</span><span data-lang-vn>{vn}</span>'


# (key, file, en, vn) — USR is home; the rest are the main D surfaces.
ITEMS = [
    ("home", "index.html", "USR", "USR"),
    ("reference", "reference.html", "Reference", "Tham chiếu"),
    ("search", "search.html", "Search", "Tìm kiếm"),
    ("compare", "compare.html", "Compare", "So sánh"),
]


def nav(prefix="", current=None):
    """prefix: "" for root pages, "../" for subdir pages (entity/company/country/segment).
    current: the key of the page you're on (rendered as non-link), or None (all are links)."""
    parts = []
    for key, fname, en, vn in ITEMS:
        cls = ' class="wm"' if key == "home" else ""
        if key == current:
            parts.append(f'<span class="cur"{cls}>{_bi(en, vn)}</span>')
        else:
            parts.append(f'<a href="{prefix}{fname}"{cls}>{_bi(en, vn)}</a>')
    return '<nav class="crumb">' + '<span class="sep">·</span>'.join(parts) + '</nav>'
