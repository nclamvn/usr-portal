#!/usr/bin/env python3
"""Single global footer (dark plate). Byte-identical on every surface (single source = footer()),
bilingual, theme-adaptive. Three parts — Brand / Navigate / Connect — + a provenance bottom bar.
Reuses .sec.plate (dark in both themes), the shield logo, nav.ITEMS, brass one-beat. Social links are
DRAFT placeholders (#) — no fabricated account URLs; owner fills real ones. verify_footer keeps it
byte-identical. Editorial rules: no '!', no em-dash, '…' not "…"."""
import html, json, pathlib
from nav import ITEMS  # leaf module — avoids a build_reference<->footer import cycle

_ROOT = pathlib.Path(__file__).resolve().parent
_BY = {key: (fn, en, vn) for key, fn, en, vn in ITEMS}
_TOTALS = None


def _totals():
    """Live registry totals for the footer's state-of-the-registry strip (same on every page ->
    footer stays byte-identical). Computed once from out/site-data.json (zero-fab)."""
    global _TOTALS
    if _TOTALS is None:
        try:
            s = json.loads((_ROOT / "out" / "site-data.json").read_bytes())
            uavs = [e for e in s["entities"] if e.get("entity_type", "uav") == "uav"]
            countries = len({(e.get("manufacturer_country") or {}).get("value") for e in uavs
                             if (e.get("manufacturer_country") or {}).get("value")})
            makers = len({(e.get("manufacturer") or {}).get("value") for e in uavs
                          if (e.get("manufacturer") or {}).get("value")})
            fill = s["aggregates"]["spec_fill_rate"]
            pres = sum(d["present"] for d in fill.values())
            tot = sum(d["total"] for d in fill.values())
            _TOTALS = {"uav": len(uavs), "makers": makers, "countries": countries,
                       "cov": round(100 * pres / tot) if tot else 0}
        except Exception:
            _TOTALS = {"uav": "—", "makers": "—", "countries": "—", "cov": "—"}
    return _TOTALS


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


def _lnk(prefix, key):
    fn, en, vn = _BY[key]
    return f'<a href="{prefix}{fn}">{bilingual(en, vn)}</a>'


def _fstat(value, en, vn):
    return (f'<div class="fstat"><b>{esc(value)}</b>'
            f'<span class="fstat-k">{bilingual(en, vn)}</span></div>')


def footer(prefix=""):
    """Single global instrument-panel footer (byte-identical per surface bar the ../ prefix). A top
    band (brand + live state-of-the-registry strip), hairline-divided link cells, and a provenance bar."""
    home = f"{prefix}index.html"
    t = _totals()
    soc = "".join(_icon(k, lbl) for k, lbl in _SOC_META)
    explore = "".join(_lnk(prefix, k) for k in ("reference", "compare", "data", "monitor"))
    read = "".join(_lnk(prefix, k) for k in ("newsroom", "review", "knowledge"))
    return (
        '<footer class="sfoot sec plate" data-audit="footer"><div class="wrap">'
        # TOP — brand + live registry strip (state of the platform)
        '<div class="sfoot-top">'
        '<div class="sfoot-brand">'
        f'<a class="sfoot-wm" href="{home}" aria-label="Drone Review, home">'
        f'<img class="brandmark" src="{prefix}base/brand-shield.png" alt="Drone Review" width="44" height="44">'
        '<span class="sfoot-id"><span class="sfoot-name">Vietnam UAV Intelligence Platform</span>'
        f'<span class="sfoot-pub">{bilingual("Published by Uncrewed Systems Review", "Xuất bản bởi Uncrewed Systems Review")}</span></span></a>'
        '</div>'
        '<div class="sfoot-stats" data-audit="fstats">'
        + _fstat(t["uav"], "systems", "hệ thống")
        + _fstat(t["makers"], "manufacturers", "nhà sản xuất")
        + _fstat(t["countries"], "countries", "quốc gia")
        + _fstat(f'{t["cov"]}%', "spec coverage", "độ phủ spec")
        + '<div class="fstat fstat-live"><span class="live-dot"></span>'
        f'<span class="fstat-k">{bilingual("Live · audited", "Sống · đã kiểm")}</span></div>'
        '</div></div>'
        # MID — hairline-divided link cells
        '<div class="sfoot-cols">'
        '<div class="sfoot-col">'
        f'<div class="sfoot-h">{bilingual("Explore", "Tra cứu")}</div>'
        f'<nav class="sfoot-nav">{explore}</nav></div>'
        '<div class="sfoot-col">'
        f'<div class="sfoot-h">{bilingual("Read", "Nội dung")}</div>'
        f'<nav class="sfoot-nav">{read}</nav>'
        f'<div class="sfoot-soon">{bilingual("Solutions · Community · soon", "Giải pháp · Cộng đồng · sắp có")}</div></div>'
        '<div class="sfoot-col">'
        f'<div class="sfoot-h">{bilingual("Connect", "Kết nối")}</div>'
        f'<div class="sfoot-soc">{soc}</div>'
        f'<p class="sfoot-prov">{bilingual("Every figure traces to a cited source and tier.", "Mọi con số truy về nguồn dẫn và tier.")}</p></div>'
        '</div>'
        # BOTTOM — provenance bar + trust/legal links
        '<div class="sfoot-bar">'
        '<span>© 2026 Drone Review · Uncrewed Systems Review</span>'
        '<nav class="sfoot-legal">'
        f'<a href="{prefix}about.html">{bilingual("About", "Về USR")}</a>'
        f'<a href="{prefix}methodology.html">{bilingual("Methodology", "Phương pháp")}</a>'
        f'<a href="{prefix}contact.html">{bilingual("Contact", "Liên hệ")}</a>'
        f'<a href="{prefix}terms.html">{bilingual("Terms", "Điều khoản")}</a>'
        f'<a href="{prefix}privacy.html">{bilingual("Privacy", "Quyền riêng tư")}</a>'
        '</nav>'
        f'<span>{bilingual("Static, audited pipeline · provenance-forward", "Pipeline tĩnh, đã kiểm · ưu-tiên nguồn dẫn")}</span>'
        '</div>'
        '</div></footer>'
    )
