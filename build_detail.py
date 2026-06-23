#!/usr/bin/env python3
"""TIP-006 — Detail layer. One static, citable page per REAL entity at entity/<slug>.html.

This is where the rich/detailed primitive belongs (the index is light rows; see build_reference).
Every number carries a footnote to its real source URL + tier (A/B/C) — the provenance promise made
visible. Honest-null renders "— / unverified", never hidden. Disputed keeps BOTH claimed values.
Reuses the shared design system + the chip()/friendly() renderers from build_reference. N-agnostic.
"""
import json, pathlib, shutil
from build_reference import chip, friendly, bilingual, esc, SPEC_FIELDS
from glyphs import glyph_svg

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
OUTDIR = ROOT / "entity"

IDENTITY = ["manufacturer", "manufacturer_country", "family", "variant",
            "airframe_type", "propulsion", "market_segment", "live_status"]


def srcrefs(fo, ledger):
    """Register a field's sources (and disputed claims) in the page footnote ledger; return its
    footnote numbers in first-seen order. Ledger is an ordered dict url -> {num, tier}."""
    refs = []
    pool = list(fo.get("sources") or [])
    pool += [{"url": c.get("url"), "tier": c.get("tier")} for c in (fo.get("claims") or [])]
    for s in pool:
        url = s.get("url")
        # only real, citable web URLs become footnotes; derived/taxonomy pseudo-refs
        # (e.g. "taxonomy:...") are conveyed by the "derived" chip, not a fake link.
        if not url or not url.startswith("http"):
            continue
        if url not in ledger:
            ledger[url] = {"num": len(ledger) + 1, "tier": s.get("tier")}
        refs.append(ledger[url]["num"])
    seen, out = set(), []
    for n in refs:
        if n not in seen:
            seen.add(n); out.append(n)
    return out


def field_row(e, field, labels, ledger):
    fo = e[field]
    lab = labels["field"].get(field, {"en": field, "vn": field})
    disp, ch = chip(fo, labels)
    if field == "market_segment" and fo.get("value"):
        disp = friendly("segment", fo.get("value"), labels)   # friendly enum, not the raw key
    sup = "".join(f'<sup><a href="#s{n}">{n}</a></sup>' for n in srcrefs(fo, ledger))
    return (f'<div class="drow"><span class="k">{bilingual(lab["en"], lab["vn"])}</span>'
            f'<span class="v" data-audit="dval">{disp}{sup}</span>{ch}</div>')


# detail-layer CSS — shared by the standalone detail page AND the single-file bundle (build_bundle).
DETAIL_CSS = """
  .dwrap{max-width:820px;margin:0 auto;padding:1.6rem 1.4rem 3rem}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1.4rem}
  .back{font-family:var(--font-mono);font-size:.74rem;color:var(--brass);text-decoration:none;cursor:pointer}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  .dhead{border-bottom:1px solid var(--hair);padding-bottom:1rem;margin-bottom:.4rem}
  .dhead h1{margin:0} .dhead .model{color:var(--brass)}
  .dhead .meta{font-size:.8rem;color:var(--muted);margin-top:.3rem}
  .dsec-h{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:1.9rem 0 .7rem;display:flex;gap:.6rem;align-items:center}
  .dsec-h::after{content:"";flex:1;height:1px;background:var(--hair)}
  .drows{display:grid;gap:0}
  .drow{display:grid;grid-template-columns:13rem 1fr auto;align-items:baseline;gap:.7rem;font-size:.85rem;padding:.42rem 0;border-bottom:1px solid var(--hair)}
  .drow .k{color:var(--ink-soft)}
  .drow .v{font-family:var(--font-mono);color:var(--ink);font-variant-numeric:tabular-nums}
  .drow .v sup a{color:var(--brass);text-decoration:none;font-size:.72em;padding:0 .12em}
  .sources ol{margin:0;padding-left:1.5rem}
  .sources li{font-family:var(--font-mono);font-size:.72rem;color:var(--ink-soft);margin:.35rem 0;overflow-wrap:anywhere}
  .sources li.nosrc{list-style:none;margin-left:-1.5rem;color:var(--muted)}
  .sources .tierbadge{display:inline-block;border:1px solid var(--brass);color:var(--brass);border-radius:3px;font-size:.85em;padding:0 .32em;margin-right:.45em;font-weight:600}
  .sources a{color:inherit}
  .note{font-size:.72rem;color:var(--muted);margin-top:1.4rem}
  .dglyph{display:flex;align-items:center;gap:18px;margin:1rem 0 .2rem}
  .dglyph-lab{font-family:var(--font-mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
"""


def detail_fragment(e, labels):
    """Inner detail content (header + identity + specs + sources + note) — NO page chrome.
    Reused verbatim by the standalone page and the single-file bundle, so honest-null / disputed /
    tier rendering can never drift between the two."""
    ledger = {}
    maker = e["manufacturer"].get("value") or "—"
    model = e["name"].get("value") or "—"
    country = e["manufacturer_country"].get("value") or "—"
    seg = friendly("segment", e["market_segment"].get("value"), labels)
    pclass = friendly("klass", e.get("provenance_class"), labels)
    ident = "".join(field_row(e, f, labels, ledger) for f in IDENTITY)
    ident += (f'<div class="drow"><span class="k">{bilingual("Class", "Lớp")}</span>'
              f'<span class="v">{pclass}</span><span></span></div>')
    specs = "".join(field_row(e, f, labels, ledger) for f in SPEC_FIELDS)
    foot = "".join(
        f'<li id="s{m["num"]}"><span class="tierbadge">{esc(m["tier"] or "—")}</span>'
        f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(url)}</a></li>'
        for url, m in ledger.items())
    if not foot:
        foot = f'<li class="nosrc">{bilingual("No source on record yet.", "Chưa có nguồn ghi nhận.")}</li>'
    return f"""<header class="dhead reg-frame" data-audit="dhead">
    <span class="reg-tr"></span><span class="reg-bl"></span>
    <h1 data-audit="dtitle">{esc(maker)} <span class="model">{esc(model)}</span></h1>
    <div class="meta mono">{esc(country)} · {seg} · {pclass}</div>
  </header>
  <div class="dglyph">{glyph_svg(e.get("frame_glyph", "unknown"), "glyph-lg")}
    <span class="dglyph-lab">{bilingual("config", "cấu hình")} · {esc(e["airframe_type"].get("value") or "—")}</span></div>
  <div class="dsec-h">{bilingual("Identity", "Định danh")}</div>
  <div class="drows">{ident}</div>
  <div class="dsec-h">{bilingual("Specifications", "Thông số")}</div>
  <div class="drows">{specs}</div>
  <div class="dsec-h">{bilingual("Sources", "Nguồn")}</div>
  <div class="sources" data-audit="sources"><ol>{foot}</ol></div>
  <p class="note">{bilingual(
    "Every value traces to a cited source and tier (A manufacturer · B official retailer · C aggregator). "
    "Unverified or absent fields are shown as null — never invented. Disputed fields keep both claimed values.",
    "Mọi giá trị truy về nguồn dẫn và tier (A nhà sản xuất · B bán lẻ chính thức · C tổng hợp). "
    "Field chưa kiểm chứng hoặc thiếu hiển thị null — không bịa. Field tranh chấp giữ cả hai giá trị.")}</p>"""


def render_detail(e, labels):
    maker = e["manufacturer"].get("value") or "—"
    model = e["name"].get("value") or "—"
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(maker)} {esc(model)} — USR</title>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<style>{DETAIL_CSS}</style>
</head>
<body>
<main class="dwrap">
  <div class="topbar">
    <a class="back" href="../reference.html">← {bilingual("Reference", "Tham chiếu")}</a>
    <div class="ctrl">
      <button id="lang"><span data-lang-en>VN</span><span data-lang-vn>EN</span></button>
      <button id="theme"><span data-lang-en>Dark</span><span data-lang-vn>Tối</span></button>
    </div>
  </div>
  {detail_fragment(e, labels)}
</main>
<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.mountArrows();
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    ents = site["entities"]
    if OUTDIR.exists():
        shutil.rmtree(OUTDIR)          # clean regen — no stale slugs linger
    OUTDIR.mkdir(parents=True)
    for e in ents:
        (OUTDIR / f'{e["slug"]}.html').write_text(render_detail(e, labels))
    print(f"entity/: {len(ents)} detail pages written")


if __name__ == "__main__":
    main()
