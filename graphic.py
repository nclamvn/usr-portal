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
