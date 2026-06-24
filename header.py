#!/usr/bin/env python3
"""Single locked global header (TIP-UX1). Byte-identical on EVERY surface: compact wordmark (left) +
breadcrumb nav (center) + lang/theme toggles (right). Fixed height via .gbar in design-system.css —
no per-surface header markup or override allowed. The ONLY per-page difference is the active-nav
state inside nav(). Surface-specific controls (search box, live indicator, filters) live in the body,
never in this header. verify_header proves it stays byte-identical."""
from nav import nav

# Brand mark — the Drone Review shield logo (DRONE/REVIEW set inside the shield). The artwork is a
# transparent black PNG; on the dark theme it's inverted to white via CSS (design-system.css), so the
# single asset serves both themes. Byte-identical across every page (single source = header()).


def header(prefix="", current=None):
    """prefix: "" for root pages, "../" for subdir pages. current: nav key of the active page."""
    home = f"{prefix}index.html"
    return (
        '<header class="gbar"><div class="gbar-in">'
        f'<a class="gbar-wm" href="{home}" aria-label="Drone Review — home">'
        f'<img class="brandmark" src="{prefix}base/brand-shield.png" alt="Drone Review" width="34" height="34"></a>'
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
