#!/usr/bin/env python3
"""TIP-006 — Detail layer. One static, citable page per REAL entity at entity/<slug>.html.

This is where the rich/detailed primitive belongs (the index is light rows; see build_reference).
Every number carries a footnote to its real source URL + tier (A/B/C) — the provenance promise made
visible. Honest-null renders "— / unverified", never hidden. Disputed keeps BOTH claimed values.
Reuses the shared design system + the chip()/friendly() renderers from build_reference. N-agnostic.
"""
import json, pathlib, shutil, re
from build_reference import chip, friendly, bilingual, esc, SPEC_FIELDS
from footer import footer
from glyphs import glyph_svg
import media_lib as ML

_MEDIA = ML.Media()


def _entity_media(slug, rel="../"):
    """TIP-MEDIA-UPGRADE — lead product photo for an entity (binding entity:<slug>), standalone only.
    Empty string when no bound asset → the page keeps its line-glyph (honest-null, site-null two-way)."""
    a = _MEDIA.first(f"entity:{slug}")
    if not a:
        return ""
    cap = esc(a.get("caption") or "")
    return (f'<figure class="dmedia" data-audit="dmedia">{ML.img_html(a, "dmedia-img", rel)}'
            f'<figcaption class="dmedia-cap">{cap}</figcaption></figure>')
from nav import nav
from header import header
from pagenav import pagenav
from seo import meta, product_ld

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
OUTDIR = ROOT / "entity"

IDENTITY = ["manufacturer", "manufacturer_country", "family", "variant",
            "airframe_type", "propulsion", "market_segment", "live_status"]
# numeric specs get a log-scaled micro-track; units for the always-on label
NUMERIC_SPEC = ["mtow_kg", "max_payload_kg", "endurance_min", "max_range_km",
                "max_link_km", "max_speed_ms", "service_ceiling_m"]
UNIT = {"mtow_kg": "kg", "max_payload_kg": "kg", "endurance_min": "min", "max_range_km": "km",
        "max_link_km": "km", "max_speed_ms": "m/s", "service_ceiling_m": "m"}


def log_pos(v, lo, hi):
    """Position % on a log10 min–max scale (D-2: linear would crush the low end into a lie)."""
    import math
    lo = max(lo, 1e-9)
    if hi <= lo or v <= 0:
        return 50.0
    p = (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * 100
    return max(2.0, min(98.0, p))


def _num(v):
    return ("%g" % v)


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


def _tslug(v):
    return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


def field_row(e, field, labels, ledger, ranges=None, taxlinks=False):
    fo = e[field]
    lab = labels["field"].get(field, {"en": field, "vn": field})
    disp, ch = chip(fo, labels)
    if field == "market_segment" and fo.get("value"):
        disp = friendly("segment", fo.get("value"), labels)   # friendly enum, not the raw key
    sup = "".join(f'<sup><a href="#s{n}">{n}</a></sup>' for n in srcrefs(fo, ledger))
    klabel = f'<span class="k">{bilingual(lab["en"], lab["vn"])}</span>'

    # micro-track for numeric specs (log scale; honest-null = dashed rail, no tick)
    if ranges is not None and field in NUMERIC_SPEC:
        rng = ranges.get(field)
        v = fo.get("value")
        if isinstance(v, (int, float)) and not isinstance(v, bool) and rng:
            pos = log_pos(v, rng["min"], rng["max"])
            rail = f'<span class="trk"><i class="tick" style="left:{pos:.0f}%"></i></span>'
            vlab = f'{esc(_num(v))} {esc(UNIT.get(field, ""))}'
        elif fo.get("status") == "disputed":
            cl = [c.get("claimed_value") for c in (fo.get("claims") or [])
                  if isinstance(c.get("claimed_value"), (int, float)) and not isinstance(c.get("claimed_value"), bool)]
            if cl and rng:
                a, b = log_pos(min(cl), rng["min"], rng["max"]), log_pos(max(cl), rng["min"], rng["max"])
                rail = f'<span class="trk"><span class="rng" style="left:{a:.0f}%;width:{max(b-a,1):.0f}%"></span></span>'
            else:
                rail = '<span class="trk null"></span>'
            vlab = " / ".join(esc(_num(c)) for c in cl) + " " + esc(UNIT.get(field, ""))
        else:  # null / unverified — honest-null, no tick
            rail, vlab = '<span class="trk null"></span>', '—'
        return (f'<div class="drow spec">{klabel}'
                f'<div class="vt"><div class="track">{rail}</div>'
                f'<span class="v" data-audit="dval">{vlab}{sup}</span></div>{ch}</div>')

    # taxonomy cross-link: country / segment value -> its index page (standalone page only;
    # the offline bundle passes taxlinks=False so its fragments carry no dead links).
    val = fo.get("value")
    if taxlinks and val and field in ("manufacturer_country", "market_segment"):
        d = "country" if field == "manufacturer_country" else "segment"
        disp = f'<a href="../{d}/{_tslug(val)}.html">{disp}</a>'
    return (f'<div class="drow">{klabel}'
            f'<span class="v" data-audit="dval">{disp}{sup}</span>{ch}</div>')


# detail-layer CSS — shared by the standalone detail page AND the single-file bundle (build_bundle).
DETAIL_CSS = """
  .dwrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3rem}
  .dwrap>*{max-width:var(--w-read)}
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
  .drow.spec{align-items:center}
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
  /* TIP-GRAPHICS — status strip: compliance badges + profile completeness (honest-null as info) */
  .dstatus{display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center;justify-content:space-between;margin:14px 0 4px;padding:10px 0;border-top:1px solid var(--hair);border-bottom:1px solid var(--hair)}
  .cbadges{display:flex;gap:8px;flex-wrap:wrap}
  .cbadge{font-family:var(--font-mono);font-size:.66rem;letter-spacing:.03em;border:1px solid var(--hair-strong);border-radius:3px;padding:2px 7px;color:var(--muted);display:inline-flex;gap:5px;align-items:center}
  .cbadge b{font-weight:700} .cbadge i{font-style:normal;color:var(--faint)}
  .cbadge.yes,.cbadge.yes b,.cbadge.yes i{border-color:var(--brass);color:var(--brass)}
  .cbadge.unk{border-style:dashed}
  .pfill{display:inline-flex;align-items:center;gap:9px}
  .pfill-lab{font-family:var(--font-mono);font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
  .pfill-bar{position:relative;width:120px;height:5px;background:var(--hair);border-radius:3px;overflow:hidden}
  .pfill-bar i{position:absolute;left:0;top:0;bottom:0;background:var(--brass);border-radius:3px}
  .pfill-n{font-family:var(--font-mono);font-size:.72rem;font-variant-numeric:tabular-nums;color:var(--ink)}
  .dglyph-lab{font-family:var(--font-mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
"""


def _cell(e, f):
    c = e.get(f)
    return c if isinstance(c, dict) else {}


def status_strip(e):
    """TIP-GRAPHICS 2.1 — turn honest-null into information: compliance badges (✓ brass / ✗ / — chưa rõ)
    + a profile-completeness bar (filled/total). Reads cells directly (no fabrication); '—' = honest-null."""
    bdg = ""
    for f, lab in (("ndaa_compliant", "NDAA"), ("blue_uas", "Blue UAS")):
        v = _cell(e, f).get("value")
        if v is True:
            cls, mk, txt = "yes", "✓", bilingual("yes", "có")
        elif v is False:
            cls, mk, txt = "no", "✗", bilingual("no", "không")
        else:
            cls, mk, txt = "unk", "—", bilingual("unverified", "chưa rõ")
        bdg += f'<span class="cbadge {cls}"><b>{mk}</b> {lab} <i>{txt}</i></span>'
    attrs = IDENTITY + SPEC_FIELDS
    present = sum(1 for f in attrs if _cell(e, f).get("value") is not None)
    total = len(attrs)
    pct = round(100 * present / total) if total else 0
    fill = (f'<div class="pfill"><span class="pfill-lab">{bilingual("Profile filled", "Độ đầy hồ sơ")}</span>'
            f'<span class="pfill-bar"><i style="width:{pct}%"></i></span>'
            f'<span class="pfill-n">{present}/{total}</span></div>')
    return f'<div class="dstatus" data-audit="dstatus"><div class="cbadges">{bdg}</div>{fill}</div>'


def detail_fragment(e, labels, ranges=None, draw=False, company=None, taxlinks=False, media_html=""):
    """Inner detail content (header + identity + specs + sources + note) — NO page chrome.
    Reused verbatim by the standalone page and the single-file bundle, so honest-null / disputed /
    tier rendering can never drift between the two. `company` (slug+name) adds a manufacturer-profile
    link on the standalone page only; the bundle passes None (offline single-file) -> byte-stable."""
    ledger = {}
    maker = e["manufacturer"].get("value") or "—"
    model = e["name"].get("value") or "—"
    country = e["manufacturer_country"].get("value") or "—"
    seg = friendly("segment", e["market_segment"].get("value"), labels)
    pclass = friendly("klass", e.get("provenance_class"), labels)
    ident = "".join(field_row(e, f, labels, ledger, taxlinks=taxlinks) for f in IDENTITY)
    ident += (f'<div class="drow"><span class="k">{bilingual("Class", "Lớp")}</span>'
              f'<span class="v">{pclass}</span><span></span></div>')
    specs = "".join(field_row(e, f, labels, ledger, ranges) for f in SPEC_FIELDS)
    foot = "".join(
        f'<li id="s{m["num"]}"><span class="tierbadge">{esc(m["tier"] or "—")}</span>'
        f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(url)}</a></li>'
        for url, m in ledger.items())
    if not foot:
        foot = f'<li class="nosrc">{bilingual("No source on record yet.", "Chưa có nguồn ghi nhận.")}</li>'
    # company link — standalone page only; empty string when absent so the bundle (company=None)
    # stays byte-identical (the link is appended right after the dglyph </div>, no stray line).
    clink = ('\n  <div class="dcompany"><a class="back" href="../company/%s.html">%s · %s &rarr;</a></div>'
             % (esc(company["slug"]), bilingual("Manufacturer profile", "Hồ sơ nhà sản xuất"),
                esc(company["name"]))) if company else ""
    return f"""<header class="dhead reg-frame" data-audit="dhead">
    <span class="reg-tr"></span><span class="reg-bl"></span>
    <h1 data-audit="dtitle">{esc(maker)} <span class="model">{esc(model)}</span></h1>
    <div class="meta mono">{esc(country)} · {seg} · {pclass}</div>
  </header>
  <div class="dglyph">{glyph_svg(e.get("frame_glyph", "unknown"), "glyph-lg", draw=draw)}
    <span class="dglyph-lab">{bilingual("config", "cấu hình")} · {esc(e["airframe_type"].get("value") or "—")}</span></div>{clink}{media_html}
  {status_strip(e)}
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


def render_detail(e, labels, ranges=None, company=None, taxlinks=True, prev=None, next=None):
    maker = e["manufacturer"].get("value") or "—"
    model = e["name"].get("value") or "—"
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(maker)} {esc(model)} — USR</title>
{meta(f"{esc(maker)} {esc(model)} — USR", f"{esc(maker)} {esc(model)}: specifications traced to cited sources and tiers.", f'entity/{e["slug"]}.html')}
{product_ld(e, f'entity/{e["slug"]}.html')}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<style>{DETAIL_CSS}</style>
</head>
<body>
{header("../")}
{pagenav(prev, next)}
<main class="dwrap">
  {detail_fragment(e, labels, ranges, draw=True, company=company, taxlinks=taxlinks, media_html=_entity_media(e["slug"]))}
</main>
{footer("../")}
<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.mountArrows();
  USRBase.initDraw();
  USRBase.initReveal();
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]  # schema/2: UAV detail pages only
    company_slugs = {e["slug"] for e in site["entities"] if e.get("entity_type") == "company"}
    ranges = site["aggregates"].get("spec_range", {})
    if OUTDIR.exists():
        shutil.rmtree(OUTDIR)          # clean regen — no stale slugs linger
    OUTDIR.mkdir(parents=True)
    from canon import canonical_slug, canonical_name
    for i, e in enumerate(ents):
        mfr = (e.get("manufacturer") or {}).get("value")
        cslug = canonical_slug(mfr)                      # alias-merged canonical company
        company = {"slug": cslug, "name": canonical_name(mfr)} if mfr and cslug in company_slugs else None
        prev = f'{ents[i-1]["slug"]}.html' if i > 0 else None              # edge prev/next (canonical order)
        nxt = f'{ents[i+1]["slug"]}.html' if i < len(ents) - 1 else None
        (OUTDIR / f'{e["slug"]}.html').write_text(render_detail(e, labels, ranges, company=company, prev=prev, next=nxt))
    print(f"entity/: {len(ents)} detail pages written")


if __name__ == "__main__":
    main()
