#!/usr/bin/env python3
"""TIP-P1.1 — Company layer. One page per company entity at company/<slug>.html.

Two registers, kept strictly apart:
  · ROLLUP  — a LIVE view derived from the UAV registry (fleet list, country/segment mix, Blue/NDAA,
              coverage). Zero new sourcing; never a claim.
  · SOURCED — manufacturer attributes (HQ, founded, website…). Each is honest-null until a golden
              record is loaded (P1.2); when loaded it carries {value,source,tier} or a disputed set,
              rendered with the same provenance apparatus as the UAV detail page.
Design-system-of-record only — no new aesthetic. Bilingual (en/vn) throughout.
"""
import json, pathlib, shutil
from build_reference import friendly, bilingual, esc, render_row, fleet_log_ranges, spec_table_head
from footer import footer
from nav import nav
from header import header
import media_lib as ML

_MEDIA = ML.Media()
from seo import meta, org_ld, breadcrumb_ld
from build_newsroom import articles_for

# TIP-NEWS-CONNECT nhịp A: aggregation cards (dòng A) that tag an entity surface on its page (two-way).
_NEWS = json.loads((pathlib.Path(__file__).resolve().parent / "content" / "news-cards.json")
                   .read_text(encoding="utf-8")).get("cards", [])
_NEWS_BY_TAG = {}
for _c in _NEWS:
    for _t in _c.get("entity_tags") or []:
        _NEWS_BY_TAG.setdefault(_t, []).append(_c)


def cards_for(tag):
    return sorted(_NEWS_BY_TAG.get(tag, []), key=lambda c: c.get("date") or "", reverse=True)

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
OUTDIR = ROOT / "company"

SOURCED_BASE = [  # (key, en, vn) — always shown (honest-null "—" if absent)
    ("legal_name", "Legal name", "Tên pháp lý"),
    ("founded_year", "Founded", "Năm thành lập"),
    ("hq_country", "HQ country", "Quốc gia trụ sở"),
    ("hq_city", "HQ city", "Thành phố trụ sở"),
    ("hq_address", "HQ address", "Địa chỉ trụ sở"),
    ("website", "Website", "Website"),
    ("founder", "Founder", "Người sáng lập"),
    ("contact_email", "Email", "Email"),
    ("contact_phone", "Phone", "Điện thoại"),
]
SOURCED_EXTRA = [  # company-specific — rendered only when present
    ("parent_company", "Parent company", "Công ty mẹ"),
    ("stock", "Stock", "Mã cổ phiếu"),
]

COMPANY_CSS = """
  .cwrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3rem}
  .cwrap>*{max-width:var(--w-read)}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1.4rem}
  .back{font-family:var(--font-mono);font-size:.74rem;color:var(--brass);text-decoration:none;cursor:pointer}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  .chead{border-bottom:1px solid var(--hair);padding-bottom:1rem;margin-bottom:.4rem}
  .chead h1{margin:0}
  .chead .meta{font-size:.8rem;color:var(--muted);margin-top:.3rem;font-family:var(--font-mono)}
  .csec-h{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:1.9rem 0 .7rem;display:flex;gap:.6rem;align-items:center}
  .csec-h::after{content:"";flex:1;height:1px;background:var(--hair)}
  .crow{display:grid;grid-template-columns:13rem 1fr auto;align-items:baseline;gap:.7rem;font-size:.85rem;padding:.42rem 0;border-bottom:1px solid var(--hair)}
  .crow .k{color:var(--ink-soft)}
  .crow .v{font-family:var(--font-mono);color:var(--ink);font-variant-numeric:tabular-nums}
  .crow .v.null{color:var(--muted)}
  .crow .src{font-family:var(--font-mono);font-size:.7rem;color:var(--muted)}
  .crow .ri-tier{margin-left:.4em}   /* source-tier badge: shared .ri-tier (A brass, B/C muted) from design-system.css */
  .mix{display:flex;flex-wrap:wrap;gap:.4rem}
  .mix .ck{font-family:var(--font-mono);font-size:.72rem;color:var(--ink-soft);border:1px solid var(--hair-strong);border-radius:3px;padding:.1rem .42rem}
  .mix .ck b{color:var(--brass);font-weight:500}
  .fleet{list-style:none;margin:.3rem 0 0;padding:0;columns:2;column-gap:1.4rem}
  @media(max-width:640px){.fleet{columns:1}}
  .fleet li{font-size:.82rem;padding:.18rem 0;break-inside:avoid}
  .fleet a{color:inherit}
  .news-list .csrc{font-family:var(--font-mono);font-size:.66rem;color:var(--muted);margin-left:.4rem;white-space:nowrap}
  .note{font-size:.72rem;color:var(--muted);margin-top:1.4rem}
  .disp{display:block;font-size:.78rem;margin:.1rem 0;padding-left:.6rem;border-left:2px solid var(--hair-strong)}
"""


def sourced_row(key, en, vn, val):
    """Render one sourced attribute: honest-null '—', a sourced {value,source,tier}, or a disputed
    set (all claims kept — invariant #10). Same provenance discipline as the UAV detail page."""
    label = f'<span class="k">{bilingual(en, vn)}</span>'
    if val is None:
        return (f'<div class="crow">{label}<span class="v null">—</span>'
                f'<span class="src">{bilingual("no source yet", "chưa có nguồn")}</span></div>')
    if isinstance(val, dict) and "disputed" in val:
        claims = val.get("disputed") or []
        body = "".join(
            f'<span class="disp">{esc(str(c.get("value")))}'
            f'<span class="ri-tier" data-t="{esc(c.get("tier") or "")}">{esc(c.get("tier") or "—")}</span> '
            f'<span class="src">{esc(c.get("source") or "")}</span></span>'
            for c in claims)
        return (f'<div class="crow">{label}<span class="v">{body}</span>'
                f'<span class="src">{bilingual("disputed", "tranh chấp")}</span></div>')
    if isinstance(val, dict) and "value" in val:
        return (f'<div class="crow">{label}'
                f'<span class="v">{esc(str(val.get("value")))}'
                f'<span class="ri-tier" data-t="{esc(val.get("tier") or "")}">{esc(val.get("tier") or "—")}</span></span>'
                f'<span class="src">{esc(val.get("source") or "")}</span></div>')
    return (f'<div class="crow">{label}<span class="v null">—</span>'
            f'<span class="src">{bilingual("invalid", "không hợp lệ")}</span></div>')


def render_company(c, labels, uav_by_slug, rng):
    roll = c.get("rollup") or {}
    name = c.get("name") or "—"
    hq = c.get("hq_city")
    hq_txt = hq["value"] if isinstance(hq, dict) and "value" in hq else None
    countries = " ".join(f'<span class="ck">{esc(k)} <b>{v}</b></span>'
                         for k, v in roll.get("countries", {}).items())
    segments = " ".join(f'<span class="ck">{friendly("segment", k, labels)} <b>{v}</b></span>'
                        for k, v in roll.get("segments", {}).items())
    # Models = the same spec-analytics table as reference.html (sparkbars positioned against the WHOLE
    # 444-fleet range so "this maker's MTOW vs the field" reads straight), honest-null dashed, tier badge.
    fleet_rows = "\n".join(render_row(uav_by_slug[s], labels, rng, rel="../")
                           for s in roll.get("uav_slugs", []) if s in uav_by_slug)
    fleet = (f'{spec_table_head()}\n  <div class="index-list">{fleet_rows}</div>') if fleet_rows else \
            f'<p class="note">{bilingual("No models in registry.", "Chưa có mẫu trong registry.")}</p>'
    rows = [sourced_row(k, en, vn, c.get(k)) for k, en, vn in SOURCED_BASE]
    rows += [sourced_row(k, en, vn, c[k]) for k, en, vn in SOURCED_EXTRA if k in c]  # extras only when present
    sourced = "".join(rows)
    # E->D cross-link: newsroom articles that tag this company surface here automatically
    arts = articles_for("company:" + c["slug"])
    rel = ""
    if arts:
        items = "".join(f'<li><a href="../news/{esc(fm["slug"])}.html">{esc(fm["title"])}</a></li>' for fm in arts)
        rel = f'<div class="csec-h">{bilingual("Coverage", "Bài viết liên quan")}</div><ul class="fleet">{items}</ul>'
    # E->D cross-link: aggregation news cards (dòng A) that tag this company surface here automatically
    news = ""
    ncards = cards_for("company:" + c["slug"])
    if ncards:
        nitems = "".join(
            f'<li><a href="../news-card/{esc(k["id"])}.html">{esc(k.get("source_title", ""))}</a>'
            f'<span class="csrc">{esc(k.get("outlet", ""))} · {esc(k.get("date", ""))}</span></li>'
            for k in ncards)
        news = (f'<div class="csec-h">{bilingual("In the news", "Điểm tin liên quan")}</div>'
                f'<ul class="fleet news-list" data-audit="entnews">{nitems}</ul>')
    # TIP-MEDIA-UPGRADE — rtr_owned lead photo for this company (binding company:<slug>); empty → keep text-only.
    _cm = _MEDIA.first("company:" + c["slug"])
    cmedia = (f'\n  <figure class="cmedia" data-audit="cmedia">{ML.img_html(_cm, "cmedia-img", "../")}'
              f'<figcaption class="cmedia-cap">{esc(_cm.get("caption") or "")}</figcaption></figure>') if _cm else ""
    # Addendum A — slot Lãnh đạo cuối trang (binding leadership:<slug>); generic, fallback-safe.
    # Tên/chức danh là claim người-thật → gate MEDIA_IDENTITY_UNSOURCED buộc kèm nguồn (in ngay trên trang).
    _ld = _MEDIA.first("leadership:" + c["slug"])
    leadership = (f'\n\n  <div class="csec-h">{bilingual("Leadership", "Lãnh đạo")}</div>'
                  f'\n  <figure class="lead-card" data-audit="leadcard">{ML.img_html(_ld, "lead-portrait", "../")}'
                  f'<figcaption class="lead-meta"><span class="lead-name">{esc(_ld.get("name") or "")}</span>'
                  f'<span class="lead-title">{esc(_ld.get("title") or "")}</span>'
                  f'<span class="lead-src">{esc(_ld.get("identity_source") or "")} · tier {esc(_ld.get("identity_tier") or "—")}</span>'
                  f'</figcaption></figure>') if _ld else ""
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name)} — USR</title>
{meta(f"{esc(name)} — USR", f"{esc(name)}: fleet rollup and sourced company profile.", f'company/{c["slug"]}.html')}
{org_ld(c, f'company/{c["slug"]}.html')}
{breadcrumb_ld([("Uncrewed Systems Review", "index.html"), (name, f'company/{c["slug"]}.html')])}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
<style>{COMPANY_CSS}</style>
</head>
<body>
{header("../")}
<main class="cwrap">
  <header class="chead">
    <h1>{esc(name)}</h1>
    <div class="meta">{bilingual("Manufacturer", "Nhà sản xuất")} · {esc(hq_txt) if hq_txt else bilingual("HQ unverified", "trụ sở chưa rõ")}</div>
  </header>{cmedia}

  <div class="csec-h">{bilingual("Fleet in registry (derived)", "Đội bay trong registry (suy ra)")}</div>
  <div class="crow"><span class="k">{bilingual("UAV count", "Số UAV")}</span><span class="v">{roll.get("uav_count", 0)}</span><span></span></div>
  <div class="crow"><span class="k">{bilingual("Blue UAS", "Blue UAS")}</span><span class="v">{roll.get("blue_uas_count", 0)}</span><span></span></div>
  <div class="crow"><span class="k">{bilingual("NDAA", "NDAA")}</span><span class="v">{roll.get("ndaa_count", 0)}</span><span></span></div>
  <div class="crow"><span class="k">{bilingual("Countries", "Quốc gia")}</span><span class="v"><span class="mix">{countries or "—"}</span></span><span></span></div>
  <div class="crow"><span class="k">{bilingual("Segments", "Phân khúc")}</span><span class="v"><span class="mix">{segments or "—"}</span></span><span></span></div>

  <div class="csec-h">{bilingual("Models", "Các mẫu")}</div>
  {fleet}

  <div class="csec-h">{bilingual("Company profile (sourced)", "Hồ sơ công ty (có nguồn)")}</div>
  {sourced}
  {rel}{news}{leadership}

  <p class="note">{bilingual(
    "Fleet figures are derived live from the UAV registry. Profile attributes carry a source and "
    "tier (A manufacturer · B reputable secondary · C directory) or are shown null until sourced — "
    "never invented. Disputed attributes keep every claim.",
    "Số đội bay suy ra trực tiếp từ registry UAV. Thuộc tính hồ sơ mang nguồn và tier "
    "(A nhà sản xuất · B thứ cấp uy tín · C danh bạ) hoặc hiển thị null tới khi có nguồn — "
    "không bịa. Thuộc tính tranh chấp giữ mọi claim.")}</p>
</main>
{footer("../")}
<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  USRBase.initReveal();
  USRBase.initRegistry({{ grid: ".index-list", item: ".row-item" }});
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""


def main():
    site = json.loads(SITE.read_bytes())
    labels = site["labels"]
    companies = [e for e in site["entities"] if e.get("entity_type") == "company"]
    uav_ents = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    uav_by_slug = {e["slug"]: e for e in uav_ents}
    rng = fleet_log_ranges(uav_ents)                  # global fleet range → cross-company comparable
    if OUTDIR.exists():
        shutil.rmtree(OUTDIR)
    OUTDIR.mkdir(parents=True)
    for c in companies:
        (OUTDIR / f'{c["slug"]}.html').write_text(render_company(c, labels, uav_by_slug, rng))
    print(f"company/: {len(companies)} company pages written")


if __name__ == "__main__":
    main()
