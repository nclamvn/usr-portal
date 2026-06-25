#!/usr/bin/env python3
"""Edge prev/next navigation — two minimalist circular arrow buttons pinned to the left/right screen
edges at header level. Leaf module (no imports from builders) so any page builder can use it without a
cycle. Renders only the side that has a neighbour; stops at the ends (no wrap). The buttons are SEPARATE
<body> children from the locked .gbar header (HEADER gate stays byte-identical). Class .pgnav is NOT in
the overlap-audit set (text/.chip/[data-audit]/h1-3/.btn), so it cannot cause false overlaps."""

# minimal arrow svg — root fill="none" + stroke=currentColor (passes verify_svg); points RIGHT.
_ARROW = ('<svg class="ar" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
          '<path d="M4.5 12H16.5M11 6.5L16.5 12L11 17.5" stroke="currentColor" '
          'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def pagenav(prev_href=None, next_href=None):
    """Return the edge buttons. prev_href/next_href are bare sibling filenames (e.g. '<slug>.html')
    resolved within the page's own directory. Omit a side by passing None."""
    out = ""
    if prev_href:
        out += f'<a class="pgnav pgnav-prev" href="{prev_href}" aria-label="Trang trước" rel="prev">{_ARROW}</a>'
    if next_href:
        out += f'<a class="pgnav pgnav-next" href="{next_href}" aria-label="Trang sau" rel="next">{_ARROW}</a>'
    return out
