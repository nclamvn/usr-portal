#!/usr/bin/env python3
"""Single global footer (dark plate). Byte-identical on every surface (single source = footer()),
bilingual, theme-adaptive. Three parts — Brand / Navigate / Connect — + a provenance bottom bar.
Reuses .sec.plate (dark in both themes), the shield logo, nav.ITEMS, brass one-beat. Social links are
DRAFT placeholders (#) — no fabricated account URLs; owner fills real ones. verify_footer keeps it
byte-identical. Editorial rules: no '!', no em-dash, '…' not "…"."""
import html
from nav import ITEMS  # leaf module — avoids a build_reference<->footer import cycle


def esc(x):
    return html.escape("" if x is None else str(x), quote=True)


def bilingual(en, vn):
    return f'<span data-lang-en>{esc(en)}</span><span data-lang-vn>{esc(vn)}</span>'

# Social channels (Standard 4). href is a DRAFT placeholder until real accounts exist (zero-fab).
# Icons: recognizable brand glyphs as inline SVG (fill=currentColor -> theme/hover adaptive).
_SOC = {
    "linkedin": '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.22.79 24 1.77 24h20.45c.98 0 1.78-.78 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/>',
    "youtube": '<path d="M23.5 6.2a3.02 3.02 0 0 0-2.12-2.14C19.5 3.55 12 3.55 12 3.55s-7.5 0-9.38.51A3.02 3.02 0 0 0 .5 6.2 31.6 31.6 0 0 0 0 12a31.6 31.6 0 0 0 .5 5.8 3.02 3.02 0 0 0 2.12 2.14c1.88.51 9.38.51 9.38.51s7.5 0 9.38-.51a3.02 3.02 0 0 0 2.12-2.14A31.6 31.6 0 0 0 24 12a31.6 31.6 0 0 0-.5-5.8zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z"/>',
    "facebook": '<path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.69.24 2.69.24v2.97h-1.52c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.1 24 18.1 24 12.07z"/>',
    "mail": '<path d="M2.4 4.8h19.2c.66 0 1.2.54 1.2 1.2v12c0 .66-.54 1.2-1.2 1.2H2.4c-.66 0-1.2-.54-1.2-1.2V6c0-.66.54-1.2 1.2-1.2zm9.6 7.05L3.3 6.6h17.4L12 11.85zM2.7 8.1v9.3h18.6V8.1l-9.3 5.55L2.7 8.1z"/>',
}
_SOC_META = [("linkedin", "LinkedIn"), ("youtube", "YouTube"), ("facebook", "Facebook"), ("mail", "Email")]


def _icon(key, label):
    svg = (f'<svg class="soc-i" viewBox="0 0 24 24" aria-hidden="true" '
           f'fill="currentColor">{_SOC[key]}</svg>')
    return (f'<a class="soc-a" href="#" aria-label="{esc(label)}" data-draft="social">{svg}</a>')


def footer(prefix=""):
    """prefix: "" for root pages, "../" for subdir pages."""
    home = f"{prefix}index.html"
    nav_links = "".join(
        f'<a href="{prefix}{fn}">{bilingual(en, vn)}</a>'
        for key, fn, en, vn in ITEMS)
    soc = "".join(_icon(k, lbl) for k, lbl in _SOC_META)
    return (
        '<footer class="sfoot sec plate" data-audit="footer"><div class="wrap">'
        '<div class="sfoot-grid">'
        # 1 · Brand
        '<div class="sfoot-brand">'
        f'<a class="sfoot-wm" href="{home}" aria-label="Drone Review, home">'
        f'<img class="brandmark" src="{prefix}base/brand-shield.png" alt="Drone Review" width="40" height="40">'
        '<span class="sfoot-name">Drone Review</span></a>'
        f'<p class="sfoot-tag">{bilingual("Trusted UAV intelligence for Vietnam. Data, knowledge and analysis in one place.", "Tri-thức UAV đáng tin-cậy cho Việt Nam. Dữ-liệu, kiến-thức và phân-tích trong một nơi.")}</p>'
        f'<p class="sfoot-prov">{bilingual("Every figure traces to a cited source and tier.", "Mọi con số truy về nguồn dẫn và tier.")}</p>'
        '</div>'
        # 2 · Navigate
        '<div class="sfoot-col">'
        f'<div class="sfoot-h">{bilingual("Navigate", "Điều hướng")}</div>'
        f'<nav class="sfoot-nav">{nav_links}</nav>'
        f'<div class="sfoot-soon">{bilingual("Solutions · Community · soon", "Giải pháp · Cộng đồng · sắp có")}</div>'
        '</div>'
        # 3 · Connect
        '<div class="sfoot-col">'
        f'<div class="sfoot-h">{bilingual("Connect", "Kết nối")}</div>'
        f'<div class="sfoot-soc">{soc}</div>'
        f'<div class="sfoot-live"><span class="live-dot"></span>'
        f'<span class="sfoot-livek">{bilingual("Live, audited data", "Dữ-liệu sống, đã kiểm")}</span></div>'
        '</div>'
        '</div>'
        # bottom bar
        '<div class="sfoot-bar">'
        f'<span>© 2026 Drone Review</span>'
        f'<span>{bilingual("Static, audited pipeline · provenance-forward", "Pipeline tĩnh, đã kiểm · ưu-tiên nguồn dẫn")}</span>'
        '</div>'
        '</div></footer>'
    )
