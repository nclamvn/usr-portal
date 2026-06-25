#!/usr/bin/env python3
"""graphic.py — newsroom lead-graphic CORE. Generates a distinct, on-brand, theme-aware INLINE svg
card per article from its frontmatter (no external file, no repetition). Two paths:
  · explicit `graphic: {kind: compare, rows: [...], caption}` → a comparison card (e.g. disputed numbers);
  · otherwise an AUTO card built from type + title + (optional headline/status/date).
Theme-aware: every paint is a design token (var(--ink)/--brass/--bg-2/...), so the card flips with the
theme. Root <svg fill="none"> + explicit fills → passes verify_svg. The svg has no DOM background, so
THEME_PURITY (which reads container background-color) is unaffected. Leaf module (no builder imports)."""
import html as _html

TYPE_VN = {"data-note": "GHI CHÚ DỮ LIỆU", "explainer": "GIẢI THÍCH", "company-profile": "HỒ SƠ",
           "uav-profile": "HỒ SƠ", "data-report": "BÁO CÁO DỮ LIỆU"}


def _e(s):
    return _html.escape(str(s), quote=True)


def _wrap(text, width=26, maxlines=3):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur); cur = w
            if len(lines) == maxlines - 1:
                break
    if cur:
        lines.append(cur)
    rest = " ".join(words[sum(len(l.split()) for l in lines):])
    if rest and lines:
        lines[-1] = (lines[-1] + " " + rest).strip()
    if lines and len(lines[-1]) > width + 8:
        lines[-1] = lines[-1][:width + 5].rstrip() + "…"
    return lines[:maxlines]


_REG = ('<path d="M28 28h26 M28 28v26" stroke="var(--brass)" stroke-width="1.5" opacity=".7"/>'
        '<path d="M732 292h-26 M732 292v-26" stroke="var(--brass)" stroke-width="1.5" opacity=".7"/>')


def _frame(inner, h=300):
    return (f'<svg viewBox="0 0 760 {h}" width="760" height="{h}" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg" role="img">'
            f'<rect x="1" y="1" width="758" height="{h-2}" rx="6" fill="var(--bg-2)" stroke="var(--hair-strong)"/>'
            f'{_REG}{inner}</svg>')


def _auto_card(fm):
    g = fm.get("graphic") or {}
    eyebrow = TYPE_VN.get(fm.get("type"), str(fm.get("type", "")).upper())
    headline = g.get("headline")
    status = g.get("status")
    date = fm.get("date", "")
    s = (f'<text x="44" y="78" font-family="ui-monospace, monospace" font-size="12" '
         f'letter-spacing="2" fill="var(--brass)">{_e(eyebrow)}</text>')
    if status:
        w = 14 + len(str(status)) * 7
        s += (f'<g transform="translate({716 - w} 62)">'
              f'<rect x="0" y="0" width="{w}" height="22" rx="11" fill="none" stroke="var(--brass)"/>'
              f'<text x="{w/2}" y="15" text-anchor="middle" font-family="ui-monospace, monospace" '
              f'font-size="10" letter-spacing="1" fill="var(--brass)">{_e(str(status).upper())}</text></g>')
    if headline:
        s += (f'<text x="44" y="168" font-family="Georgia, serif" font-weight="600" font-size="58" '
              f'letter-spacing="-1" fill="var(--ink)">{_e(headline)}</text>')
        y = 210
        for ln in _wrap(fm.get("title", ""), 44, 2):
            s += (f'<text x="44" y="{y}" font-family="Georgia, serif" font-size="17" '
                  f'fill="var(--ink-soft)">{_e(ln)}</text>'); y += 24
    else:
        y = 128
        for ln in _wrap(fm.get("title", ""), 30, 3):
            s += (f'<text x="44" y="{y}" font-family="Georgia, serif" font-weight="600" font-size="34" '
                  f'letter-spacing="-.5" fill="var(--ink)">{_e(ln)}</text>'); y += 44
    s += ('<line x1="44" y1="258" x2="716" y2="258" stroke="var(--hair-strong)"/>'
          f'<text x="44" y="282" font-family="ui-monospace, monospace" font-size="11" '
          f'fill="var(--muted)">{_e(date)}</text>'
          '<text x="716" y="282" text-anchor="end" font-family="ui-monospace, monospace" '
          'font-size="10" letter-spacing="1" fill="var(--faint)">USR · ĐỒ-HOẠ GỐC</text>')
    return _frame(s, 300)


def _compare_card(fm):
    g = fm["graphic"]
    rows = g.get("rows", [])
    n = max(1, len(rows))
    s = (f'<text x="44" y="58" font-family="Georgia, serif" font-weight="600" font-size="22" '
         f'fill="var(--ink)">{_e(g.get("title", fm.get("title","")))}</text>'
         '<line x1="44" y1="80" x2="716" y2="80" stroke="var(--brass)" stroke-width="1.5"/>')
    colw = (716 - 44) / n
    for i, r in enumerate(rows):
        x = 44 + i * colw
        if i:
            s += (f'<text x="{x-12:.0f}" y="172" font-family="Georgia, serif" font-size="30" '
                  f'fill="var(--brass)">≠</text>')
        s += (f'<text x="{x:.0f}" y="124" font-family="ui-monospace, monospace" font-size="11" '
              f'letter-spacing="1" fill="var(--brass)">{_e(r.get("label",""))}</text>'
              f'<text x="{x:.0f}" y="170" font-family="Georgia, serif" font-weight="600" font-size="38" '
              f'letter-spacing="-1" fill="var(--ink)">{_e(r.get("value",""))}</text>'
              f'<text x="{x:.0f}" y="194" font-family="ui-monospace, monospace" font-size="11" '
              f'fill="var(--muted)">{_e(r.get("sub",""))}</text>')
    s += '<line x1="44" y1="250" x2="716" y2="250" stroke="var(--hair-strong)"/>'
    cap = _wrap(g.get("caption", ""), 92, 2)
    y = 276
    for ln in cap:
        s += (f'<text x="44" y="{y}" font-family="Georgia, serif" font-size="14" '
              f'fill="var(--ink-soft)">{_e(ln)}</text>'); y += 20
    s += ('<text x="716" y="316" text-anchor="end" font-family="ui-monospace, monospace" '
          'font-size="10" letter-spacing="1" fill="var(--faint)">USR · ĐỒ-HOẠ GỐC</text>')
    return _frame(s, 340)


def lead_graphic(fm):
    """Return a full <figure> with an inline, theme-aware, data-driven svg card. Used when an article
    has no source photo. Distinct per article (no shared file)."""
    g = fm.get("graphic") or {}
    svg = _compare_card(fm) if g.get("kind") == "compare" else _auto_card(fm)
    return (f'<figure class="nfig nfig-graphic">{svg}'
            f'<figcaption>Đồ-hoạ gốc: USR · dữ-liệu từ registry'
            f' <span class="lic">đồ-hoạ gốc</span></figcaption></figure>')


# ─────────────────────────────────────────────────────────────────────────────
# TIP-NEWSROOM — FEED figures. Sized for the editorial frame: lead aside / secondary
# thumb / stream brief. HONEST-NULL: an article with no graphic-data gets a TYPE glyph
# (generic technical motif, labelled "minh hoạ"), NEVER a fabricated chart and NEVER a
# borrowed image. Charts/counts render ONLY from the article's own sourced numbers. Every
# paint is a design token → theme-aware; root fill="none" + explicit fills → verify_svg-safe.
# ─────────────────────────────────────────────────────────────────────────────
BOX = {"lead": (236, 168), "thumb": (118, 90), "brief": (30, 30)}


def _num_vn(v):
    s = str(v)
    return s.replace(".", ",") if isinstance(v, float) else s


def _svgwrap(w, h, inner):
    return (f'<svg class="nf-svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg" role="img" preserveAspectRatio="xMidYMid meet">{inner}</svg>')


def _fig_chart(g, w, h):
    bars = g.get("bars", [])
    if not bars:
        return _fig_glyph("data-note", w, h)
    pl, pr, pt, pb = 20, 16, 26, 20
    base = h - pb
    plot = base - pt
    n = len(bars)
    slot = (w - pl - pr) / n
    bw = min(46, slot * 0.46)
    mx = max(float(b["value"]) for b in bars) or 1
    s = f'<line x1="{pl}" y1="{base}" x2="{w-pr}" y2="{base}" stroke="var(--hair-strong)" stroke-width="1"/>'
    for gy in (0.34, 0.67, 1.0):
        y = base - plot * gy
        s += (f'<line x1="{pl}" y1="{y:.1f}" x2="{w-pr}" y2="{y:.1f}" stroke="var(--hair)" '
              f'stroke-width="0.75" stroke-dasharray="2 3"/>')
    for i, b in enumerate(bars):
        v = float(b["value"]); bh = plot * (v / mx); cx = pl + slot * (i + 0.5); x = cx - bw / 2; y = base - bh
        disp = b.get("disp") or _num_vn(b.get("value"))
        if b.get("kind") == "target":
            s += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="none" '
                  f'stroke="var(--brass)" stroke-width="1.5" stroke-dasharray="4 3"/>')
            tc = "var(--brass)"
        else:
            s += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="var(--brass)"/>'
            tc = "var(--ink)"
        s += (f'<text x="{cx:.1f}" y="{y-6:.1f}" font-family="ui-monospace, monospace" font-size="12" '
              f'fill="{tc}" text-anchor="middle" font-weight="600">{_e(disp)}</text>')
        s += (f'<text x="{cx:.1f}" y="{base+14:.1f}" font-family="ui-monospace, monospace" font-size="9" '
              f'fill="var(--muted)" text-anchor="middle" letter-spacing="1">{_e(b.get("label",""))}</text>')
    return _svgwrap(w, h, s)


def _fig_count(g, w, h):
    val = g.get("value", "")
    target = g.get("target")
    # faint dot grid backdrop (a "field of points", not data — purely textural, generic)
    s = ""
    cols, rows = 6, 4
    gx0, gy0, gxs, gys = w * 0.12, h * 0.2, (w * 0.76) / (cols - 1), (h * 0.5) / (rows - 1)
    for r in range(rows):
        for c in range(cols):
            s += f'<circle cx="{gx0+c*gxs:.1f}" cy="{gy0+r*gys:.1f}" r="1.6" fill="var(--hair-strong)"/>'
    nb = "var(--brass)" if target else "var(--ink)"
    s += (f'<text x="{w/2:.1f}" y="{h*0.6:.1f}" font-family="ui-monospace, monospace" '
          f'font-size="{min(40, w*0.18):.0f}" font-weight="600" fill="{nb}" text-anchor="middle">{_e(val)}</text>')
    if target:
        s += (f'<rect x="{w/2-26:.1f}" y="{h*0.72:.1f}" width="52" height="14" rx="7" fill="none" '
              f'stroke="var(--brass)" stroke-width="1" stroke-dasharray="3 2"/>')
    return _svgwrap(w, h, s)


def _fig_compare_mini(fm, w, h):
    g = fm.get("graphic") or {}
    rows = g.get("rows", [])[:3]
    if not rows:
        return _fig_glyph(fm.get("type"), w, h)
    s = ""
    n = max(1, len(rows))
    colw = (w - 24) / n
    for i, r in enumerate(rows):
        x = 16 + i * colw
        if i:
            s += (f'<text x="{x-9:.0f}" y="{h*0.55:.0f}" font-family="Georgia, serif" font-size="16" '
                  f'fill="var(--brass)">≠</text>')
        s += (f'<text x="{x:.0f}" y="{h*0.3:.0f}" font-family="ui-monospace, monospace" font-size="8" '
              f'letter-spacing="1" fill="var(--brass)">{_e(r.get("label",""))[:10]}</text>'
              f'<text x="{x:.0f}" y="{h*0.58:.0f}" font-family="Georgia, serif" font-weight="600" '
              f'font-size="{min(22,w*0.1):.0f}" fill="var(--ink)">{_e(r.get("value",""))}</text>'
              f'<text x="{x:.0f}" y="{h*0.78:.0f}" font-family="ui-monospace, monospace" font-size="7.5" '
              f'fill="var(--muted)">{_e(r.get("sub",""))[:16]}</text>')
    return _svgwrap(w, h, s)


def _glyph_inner(kind, w, h):
    """Generic technical motif per article type — a CLASSIFICATION mark, not a depiction of any
    specific entity. Stroke-only, brass + faint."""
    cx, cy = w / 2, h / 2
    B, F = "var(--brass)", "var(--hair-strong)"
    if kind == "company-profile":   # craft silhouette (winged + rotor) — generic, labelled "hồ sơ"
        return (f'<line x1="{cx-30}" y1="{cy-6}" x2="{cx+30}" y2="{cy-6}" stroke="{B}" stroke-width="1.5"/>'
                f'<ellipse cx="{cx}" cy="{cy+6}" rx="16" ry="6" stroke="{B}" stroke-width="1.5"/>'
                f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-6}" stroke="{B}" stroke-width="1.25"/>'
                f'<ellipse cx="{cx-22}" cy="{cy-6}" rx="8" ry="2.4" stroke="{F}" stroke-width="1"/>'
                f'<ellipse cx="{cx+22}" cy="{cy-6}" rx="8" ry="2.4" stroke="{F}" stroke-width="1"/>')
    if kind in ("policy", "standard"):   # document
        return (f'<rect x="{cx-13}" y="{cy-18}" width="26" height="36" stroke="{B}" stroke-width="1.25"/>'
                f'<line x1="{cx-7}" y1="{cy-10}" x2="{cx+7}" y2="{cy-10}" stroke="{F}" stroke-width="1"/>'
                f'<line x1="{cx-7}" y1="{cy-3}" x2="{cx+7}" y2="{cy-3}" stroke="{F}" stroke-width="1"/>'
                f'<line x1="{cx-7}" y1="{cy+4}" x2="{cx+2}" y2="{cy+4}" stroke="{F}" stroke-width="1"/>'
                f'<circle cx="{cx+6}" cy="{cy+11}" r="4" stroke="{B}" stroke-width="1"/>')
    if kind == "explainer":   # concept nodes + links
        return (f'<circle cx="{cx-22}" cy="{cy}" r="5" stroke="{B}" stroke-width="1.5"/>'
                f'<circle cx="{cx+10}" cy="{cy-12}" r="5" stroke="{B}" stroke-width="1.5"/>'
                f'<circle cx="{cx+14}" cy="{cy+12}" r="5" stroke="{F}" stroke-width="1.5"/>'
                f'<line x1="{cx-17}" y1="{cy}" x2="{cx+5}" y2="{cy-11}" stroke="{F}" stroke-width="1"/>'
                f'<line x1="{cx-17}" y1="{cy+1}" x2="{cx+9}" y2="{cy+11}" stroke="{F}" stroke-width="1"/>')
    if kind == "data-report":   # bars
        bx = cx - 24
        out = ""
        for i, bh in enumerate((10, 22, 14, 28)):
            paint = ('fill="var(--brass)"' if i % 2 == 0
                     else 'fill="none" stroke="var(--brass)" stroke-width="1.25"')
            out += f'<rect x="{bx+i*13:.0f}" y="{cy+14-bh}" width="8" height="{bh}" {paint}/>'
        return out
    if kind == "compare":   # two unequal bars + ≠  (a "values differ" mark; no text → overlap-safe)
        return (f'<rect x="{cx-28}" y="{cy}" width="13" height="16" fill="var(--brass)"/>'
                f'<rect x="{cx+15}" y="{cy-16}" width="13" height="32" fill="none" stroke="var(--brass)" '
                f'stroke-width="1.5" stroke-dasharray="4 3"/>'
                f'<line x1="{cx-6}" y1="{cy-1}" x2="{cx+6}" y2="{cy-1}" stroke="{F}" stroke-width="1.25"/>'
                f'<line x1="{cx-6}" y1="{cy+4}" x2="{cx+6}" y2="{cy+4}" stroke="{F}" stroke-width="1.25"/>'
                f'<line x1="{cx+6}" y1="{cy-5}" x2="{cx-6}" y2="{cy+9}" stroke="{B}" stroke-width="1.25"/>')
    # default data-note → chart axes + rising line
    return (f'<line x1="{cx-26}" y1="{cy-16}" x2="{cx-26}" y2="{cy+16}" stroke="{F}" stroke-width="1"/>'
            f'<line x1="{cx-26}" y1="{cy+16}" x2="{cx+26}" y2="{cy+16}" stroke="{F}" stroke-width="1"/>'
            f'<path d="M{cx-22} {cy+8} L{cx-8} {cy-2} L{cx+4} {cy+4} L{cx+22} {cy-14}" '
            f'stroke="{B}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')


def _fig_glyph(kind, w, h):
    return _svgwrap(w, h, _glyph_inner(kind, w, h))


def feed_figure(fm, box="thumb"):
    """Return inline SVG for an article in the feed. box ∈ {lead, thumb, brief}. Picks chart/count/
    compare from the article's own graphic-data; otherwise an honest-null TYPE glyph."""
    w, h = BOX.get(box, BOX["thumb"])
    g = fm.get("graphic") or {}
    kind = g.get("kind")
    if box == "brief":                      # 30x30 — always a small type/kind icon, never chart text
        ic = ("data-note" if kind in ("chart", "count") else "compare" if kind == "compare"
              else (fm.get("type") or "data-note"))
        return _fig_glyph(ic, w, h)
    if kind == "chart":   return _fig_chart(g, w, h)
    if kind == "count":   return _fig_count(g, w, h)
    if kind == "compare": return _fig_glyph("compare", w, h)   # mark, not crammed text (overlap-safe)
    if kind == "compare": return _fig_compare_mini(fm, w, h)
    return _fig_glyph(fm.get("type"), w, h)


def figure_is_data(fm):
    """True if the article carries real sourced figure-data (chart/count/compare) vs an honest-null glyph."""
    return (fm.get("graphic") or {}).get("kind") in ("chart", "count", "compare")
