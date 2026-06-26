#!/usr/bin/env python3
"""build_registry_cards.py — TIP-FP1 (path 1): Mode-D registry-card generator.

Renders the LAE registry (content/lae-registry.json) as field-rendered cards on a standalone Registry
surface — NO prose body, every title/meta traced to a real field. Two QUALIFY thresholds: an entity
with an event signal (date/status/incident) + source + tier becomes an EVENT card; a thin entity stays
a row (no card). UAV/company are NOT re-listed here (that is reference.html, the existing browse) —
this surface POINTS to it. Cards are NOT injected into the newsroom feed: the 30 LAE E articles cover
the same subjects, so feed-mixing + de-dup is FP2's assembly job (flagged in the report).

Mode D, not E: titles are field concatenations, never authored sentences. figure from data (honest-null
glyph when no datum). The wall holds: D is built from the registry, never from the E articles.
"""
import json, pathlib, html as _html
from build_reference import bilingual, esc
from footer import footer
from header import header
from seo import meta as seo_meta
from graphic import feed_figure

ROOT = pathlib.Path(__file__).resolve().parent
LAE = ROOT / "content" / "lae-registry.json"
OUT = ROOT / "registry.html"

# entity_type -> desk (policy + standard merge into Policy)
DESK = {"policy": ("Policy", "Chính sách"), "standard": ("Policy", "Chính sách"),
        "market_claim": ("Market", "Thị trường"), "player": ("Systems", "Hệ thống"),
        "infrastructure": ("Infrastructure", "Hạ tầng"), "use_case": ("Use case", "Ứng dụng"),
        "incident": ("Incident", "Sự cố")}
DESK_ORDER = ["Chính sách", "Thị trường", "Hệ thống", "Hạ tầng", "Ứng dụng", "Sự cố"]
STRATUM = {"vietnam": ("VN", "Việt Nam"), "world": ("World", "Thế giới"), "china": ("China", "Trung Quốc")}
# entity_type -> honest-null glyph kind (graphic._glyph_inner vocabulary)
GLYPH = {"policy": "policy", "standard": "standard", "player": "company-profile",
         "market_claim": "data-note", "infrastructure": "data-report", "use_case": "explainer",
         "incident": "data-note"}


def qualify(e):
    """EVENT (→ card) | row (thin, no card). Two thresholds; thin entities never become empty cards."""
    sourced = any(c.get("tier") for c in (e.get("fields") or {}).values())
    if not sourced:
        return "row"
    if e.get("date") or e.get("status") or e.get("entity_type") == "incident":
        return "event"
    return "row"


def _src(e):
    """Representative source (host + tier + url) — from the name field's sources, else any sourced field."""
    fields = e.get("fields") or {}
    for key in ["name", *fields.keys()]:
        srcs = (fields.get(key) or {}).get("sources") or []
        if srcs:
            s = srcs[0]
            return {"source": s.get("source"), "tier": s.get("tier"), "url": s.get("url")}
    return {}


def _is_target(e):
    st = (e.get("status") or "").lower()
    return any(k in st for k in ("mục tiêu", "dự báo", "dự kiến", "kế hoạch", "target"))


def _figure(e):
    """figure from data: a count when the entity carries a clean value; otherwise an honest-null glyph."""
    if e.get("value") is not None:
        val = f'{e["value"]}'
        unit = e.get("unit")
        fm = {"graphic": {"kind": "count", "value": (str(val) + (" " + unit if unit else ""))[:14],
                          "label": "", "status": e.get("status"), "target": _is_target(e)}}
    else:
        fm = {"type": GLYPH.get(e.get("entity_type"), "data-note")}
    return feed_figure(fm, "thumb")


def _meta(e):
    s = _src(e)
    out = ""
    if s.get("source"):
        tcls = "tier" if str(s.get("tier", "")).startswith("A") else "tier bb"
        out += f'<span class="src">{bilingual("Source", "Nguồn")} {esc(s["source"])}</span>'
        out += f'<span class="{tcls}">✓{esc(s.get("tier") or "?")}</span>'
    if e.get("scope"):
        out += f'<span class="rscope">{esc(e["scope"])}</span>'
    if e.get("status"):
        cls = "tag-target" if _is_target(e) else "tag-actual"
        out += f'<span class="{cls}">{esc(e["status"])[:36]}</span>'
    if e.get("date"):
        out += f'<span class="rdate">{esc(e["date"])}</span>'
    return out


def _card(e):
    st_en, st_vn = STRATUM.get(e.get("stratum"), ("", ""))
    title = e.get("name") or e["entity"]                 # title = the registry NAME field (0 prose)
    s = _src(e)
    href = s.get("url") or "#"
    link_o = f'<a href="{esc(href)}" target="_blank" rel="noopener">' if href != "#" else "<span>"
    link_c = "</a>" if href != "#" else "</span>"
    return (
        f'<article class="rcard" data-desk="{esc(DESK.get(e.get("entity_type"), ("", ""))[1])}" '
        f'data-stratum="{esc(e.get("stratum") or "")}" data-kind="event">'
        f'<div class="rcard-fig">{_figure(e)}</div>'
        f'<div class="rcard-body">'
        f'<div class="rcard-tags"><span class="rtag rtag-st">{bilingual(st_en, st_vn)}</span>'
        f'<span class="rtag">{bilingual("Registry record", "Hồ sơ registry")}</span></div>'
        f'<h3 class="rcard-t">{link_o}{esc(title)}{link_c}</h3>'
        f'<div class="rcard-meta">{_meta(e)}</div>'
        f'</div></article>')


def main():
    doc = json.loads(LAE.read_bytes())
    ents = doc["entities"]
    events = [e for e in ents if qualify(e) == "event"]
    rows = [e for e in ents if qualify(e) == "row"]
    # group events by desk
    by_desk = {d: [] for d in DESK_ORDER}
    for e in events:
        d = DESK.get(e.get("entity_type"), (None, "—"))[1]
        by_desk.setdefault(d, []).append(e)
    sections = ""
    for d in DESK_ORDER:
        cs = sorted(by_desk.get(d, []), key=lambda e: (e.get("stratum") or "", e["entity"]))
        if not cs:
            continue                                     # honest-null: an empty desk is NOT scaffolded
        cards = "".join(_card(e) for e in cs)
        sections += (f'<section class="rdesk"><div class="rdesk-h"><h2>{esc(d)}</h2>'
                     f'<span class="rdesk-n">{len(cs)}</span></div>'
                     f'<div class="rgrid">{cards}</div></section>')
    head = seo_meta("Registry — USR",
                    "Field-rendered registry records (Mode D): every card built from real fields, with source and tier.",
                    "registry.html")
    body = f"""{header("", None)}
<main class="rsurf">
  <header class="rsurf-h">
    <span class="rsurf-k">{bilingual("Registry · Mode D", "Hồ sơ · Mode D")}</span>
    <h1>{bilingual("Registry records", "Hồ sơ dữ liệu")}</h1>
    <p class="rsurf-lede">{bilingual(
        f"{len(events)} records rendered straight from the low-altitude-economy registry — every title is a "
        "field, every card carries its source and tier. No prose, nothing authored.",
        f"{len(events)} hồ sơ render thẳng từ registry kinh tế tầm thấp — mỗi tiêu đề là một field, mỗi thẻ "
        "mang nguồn và tier. Không văn xuôi, không bài viết.")}</p>
  </header>
  {sections}
  <section class="rbrowse">
    <div class="rdesk-h"><h2>{bilingual("Systems", "Hệ thống")}</h2></div>
    <p class="rsurf-lede">{bilingual(
        "302 uncrewed systems with full spec sheets live in the reference browse — this surface points there "
        "rather than re-listing them.",
        "302 hệ thống không người lái với bảng thông số đầy đủ nằm ở trang tra cứu — mặt này trỏ sang đó, "
        "không liệt kê lại.")}</p>
    <a class="rbrowse-cta" href="reference.html">{bilingual("Browse the systems registry", "Duyệt kho hệ thống")} →</a>
  </section>
</main>
{footer("")}
<script src="base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>"""
    OUT.write_text(f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Registry — USR</title>
{head}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
</head>
<body>
{body}
</body>
</html>
""")
    from collections import Counter
    mat = Counter((DESK.get(e["entity_type"], ("", "—"))[1], e["stratum"]) for e in events)
    print(f"registry.html: {len(events)} event-cards · {len(rows)} rows (thin, no card)")
    for (d, st), n in sorted(mat.items()):
        print(f"   {d:12} {st:9} {n}")


if __name__ == "__main__":
    main()
