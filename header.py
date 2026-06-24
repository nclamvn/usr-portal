#!/usr/bin/env python3
"""Single locked global header (TIP-UX1). Byte-identical on EVERY surface: compact wordmark (left) +
breadcrumb nav (center) + lang/theme toggles (right). Fixed height via .gbar in design-system.css —
no per-surface header markup or override allowed. The ONLY per-page difference is the active-nav
state inside nav(). Surface-specific controls (search box, live indicator, filters) live in the body,
never in this header. verify_header proves it stays byte-identical."""
from nav import nav

# Brand mark — heraldic shield outline (theme-adaptive via currentColor) + "Drone Review" wordmark.
# Inline SVG (not the PNG) so it inverts cleanly on the dark theme. Decorative shape; sizing in
# design-system.css (.gbar-wm svg). Kept byte-identical across every page (single source = header()).
SHIELD = ('<svg class="brandmark" viewBox="0 0 44 52" aria-hidden="true" fill="none" '
          'stroke="currentColor" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round">'
          '<path d="M9 5 H35 Q38 5 38 8 V28 C38 40 31 46 22 49 C13 46 6 40 6 28 V8 Q6 5 9 5 Z"/></svg>')


def header(prefix="", current=None):
    """prefix: "" for root pages, "../" for subdir pages. current: nav key of the active page."""
    home = f"{prefix}index.html"
    return (
        '<header class="gbar"><div class="gbar-in">'
        f'<a class="gbar-wm" href="{home}" aria-label="Drone Review — home">{SHIELD}'
        '<span class="brandtxt">Drone Review</span></a>'
        f'{nav(prefix, current)}'
        '<div class="gbar-ctl">'
        '<button id="lang" class="gbar-tg" aria-label="Language">'
        '<span data-lang-en>VN</span><span data-lang-vn>EN</span></button>'
        '<button id="theme" class="gbar-tg" aria-label="Theme">'
        '<span data-lang-en>Dark</span><span data-lang-vn>Tối</span></button>'
        '</div></div></header>'
    )


# the init script every page runs (theme + i18n bound to the locked toggles)
HEADER_INIT = ('USRBase.initTheme(document.getElementById("theme"));'
               'USRBase.initI18n(document.getElementById("lang"));')
