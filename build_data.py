#!/usr/bin/env python3
"""TIP-P2.3 — Data overview /data. Live distributions (country · manufacturer · segment · industry
standards) + coverage matrix, all COMPUTED AT BUILD TIME from site-data (GLOBAL CONSTRAINT — never
hardcoded). honest-null is its own visible bucket, never folded into "false". The long-tail "other"
bucket is COUNTED (sums still equal the total). Static-baked HTML + data-overview.json; verify_data
re-derives independently (OVERVIEW_DRIFT). Reuses design-system + the P03 coverage idiom.
"""
import json, pathlib
from build_reference import friendly, bilingual, esc
from canon import canon_country, canonical_slug, canonical_name
from nav import nav
from seo import meta as seo_meta, collection_ld

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
DATA = ROOT / "out" / "data-overview.json"
PAGE = ROOT / "data.html"

import re
def tslug(v): return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")

SPEC_FIELDS = ["mtow_kg", "max_payload_kg", "endurance_min", "max_range_km", "max_link_km",
               "max_speed_ms", "service_ceiling_m", "encryption", "blue_uas", "ndaa_compliant",
               "gps_denied_capable"]
SPEC_LABEL = {"mtow_kg": ("MTOW", "MTOW"), "max_payload_kg": ("Payload", "Tải trọng"),
              "endurance_min": ("Endurance", "Thời gian bay"), "max_range_km": ("Range", "Tầm bay"),
              "max_link_km": ("Datalink", "Datalink"), "max_speed_ms": ("Speed", "Tốc độ"),
              "service_ceiling_m": ("Ceiling", "Trần bay"), "encryption": ("Encryption", "Mã hoá"),
              "blue_uas": ("Blue UAS", "Blue UAS"), "ndaa_compliant": ("NDAA", "NDAA"),
              "gps_denied_capable": ("GPS-denied", "GPS-denied")}
TOPN = 12


def compute(site):
    labels = site["labels"]
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    companies = [e for e in site["entities"] if e.get("entity_type") == "company"]
    from collections import Counter
    total = len(uavs)

    def ranked(counter, slug_of, top=TOPN, other_en="more", other_vn="khác"):
        items = counter.most_common()
        out = [{"n": k, "v": v, "slug": slug_of(k)} for k, v in items[:top]]
        rest = sum(v for _, v in items[top:])
        if rest:
            out.append({"n": "%d %s" % (len(items) - top, other_vn), "n_en": "%d %s" % (len(items) - top, other_en),
                        "v": rest, "other": True})
        return out

    country = Counter(canon_country((e.get("manufacturer_country") or {}).get("value")) for e in uavs
                      if (e.get("manufacturer_country") or {}).get("value"))
    maker = Counter(canonical_name((e.get("manufacturer") or {}).get("value")) for e in uavs
                    if (e.get("manufacturer") or {}).get("value"))
    seg = Counter()
    seg_null = 0
    for e in uavs:
        s = (e.get("market_segment") or {}).get("value")
        if s:
            seg[s] += 1
        else:
            seg_null += 1

    country_d = ranked(country, lambda k: tslug(k), other_en="countries", other_vn="nước khác")
    maker_d = ranked(maker, lambda k: canonical_slug(k), other_en="makers", other_vn="hãng khác")
    seg_d = [{"n_en": labels["segment"].get(k, {}).get("en", k), "n": labels["segment"].get(k, {}).get("vn", k),
              "v": v, "slug": tslug(k)} for k, v in seg.most_common()]
    if seg_null:
        seg_d.append({"n_en": "Unclassified", "n": "Chưa phân loại", "v": seg_null, "null": True})

    standards = []
    for key in ("blue_uas", "ndaa_compliant"):
        yes = sum(1 for e in uavs if (e.get(key) or {}).get("value") is True)
        standards.append({"key": key, "yes": yes, "total": total})  # unverified = total - yes (no "false")

    fill = site["aggregates"]["spec_fill_rate"]
    coverage = [{"key": k, "pct": round(100 * fill[k]["present"] / fill[k]["total"]) if fill.get(k) else 0,
                 "present": fill[k]["present"], "total": fill[k]["total"]} for k in SPEC_FIELDS]
    cov_present = sum(c["present"] for c in coverage)
    cov_total = sum(c["total"] for c in coverage)

    totals = {"uav": total, "company": len(companies), "country": len(country), "segment": len(seg),
              "coverage_pct": round(100 * cov_present / cov_total) if cov_total else 0,
              "disputed": site["aggregates"]["field_status_counts"].get("disputed", 0)}
    return {"schema": "data-overview/1", "totals": totals, "country": country_d, "maker": maker_d,
            "segment": seg_d, "standards": standards, "coverage": coverage}


# --- render (static) ---
def _bars(arr, link_dir):
    mx = max(d["v"] for d in arr) if arr else 1
    out = []
    for d in arr:
        w = max(2, round(d["v"] / mx * 100))
        cls = "null" if d.get("null") else ("other" if d.get("other") else "")
        lab = bilingual(d.get("n_en", d["n"]), d["n"]) if ("n_en" in d) else esc(d["n"])
        inner = (f'<span class="lb">{lab}</span><div class="track"><div class="fill" style="width:{w}%"></div></div>'
                 f'<span class="ct">{d["v"]}</span>')
        if link_dir and d.get("slug") and not d.get("other") and not d.get("null"):
            out.append(f'<a class="brow" href="{link_dir}/{esc(d["slug"])}.html">{inner}</a>')
        else:
            out.append(f'<div class="brow {cls}">{inner}</div>')
    return "".join(out)


def _split(arr, link_dir):
    half = (len(arr) + 1) // 2
    return _bars(arr[:half], link_dir), _bars(arr[half:], link_dir)


def render(ov):
    t = ov["totals"]
    figs = [("uav", t["uav"], "", "UAV systems", "Hệ thống UAV"), ("company", t["company"], "", "Manufacturers", "Doanh nghiệp"),
            ("country", t["country"], "", "Countries", "Quốc gia"), ("segment", t["segment"], "", "Segments", "Phân khúc"),
            ("coverage", t["coverage_pct"], "%", "Spec coverage", "Độ phủ spec"), ("disputed", t["disputed"], "", "Disputed fields", "Trường tranh chấp")]
    figs_html = "".join(
        f'<div class="fig"><div class="v">{v}{f"<span class=u>{u}</span>" if u else ""}</div>'
        f'<div class="k">{bilingual(en, vn)}</div></div>' for _, v, u, en, vn in figs)

    c1, c2 = _split(ov["country"], "country")
    m1, m2 = _split(ov["maker"], "company")
    seg_html = _bars(ov["segment"], "segment")

    std_html = ""
    SD = {"blue_uas": ("Blue UAS", "DIU-approved list for US federal agencies.", "Danh sách DIU duyệt cho cơ quan liên bang Mỹ."),
          "ndaa_compliant": ("NDAA Section 848", "Restriction on covered foreign components.", "Hạn chế linh kiện nước ngoài thuộc diện covered.")}
    for s in ov["standards"]:
        nm, den, dvn = SD[s["key"]]
        unk = s["total"] - s["yes"]
        std_html += (f'<div class="stdcard"><div class="nm">{esc(nm)}</div>'
                     f'<div class="desc">{bilingual(den, dvn)}</div>'
                     f'<div class="big"><span class="n">{s["yes"]}</span><span class="of">/ {s["total"]} {bilingual("recorded in list", "ghi nhận trong danh sách")}</span></div>'
                     f'<div class="segbar"><div class="s yes" style="flex:{s["yes"]}"></div><div class="s unk" style="flex:{unk}"></div></div>'
                     f'<div class="leg"><span><span class="sw yes"></span>{bilingual("In list", "Có trong danh sách")} · {s["yes"]}</span>'
                     f'<span><span class="sw unk"></span>{bilingual("Unverified", "Chưa kiểm chứng")} · {unk}</span></div></div>')

    ROWS = 24
    cov_html = ""
    for c in ov["coverage"]:
        on = round(c["pct"] / 100 * ROWS)
        cells = "".join(f'<div class="c {"on" if i < on else "off"}"></div>' for i in range(ROWS - 1, -1, -1))
        en, vn = SPEC_LABEL[c["key"]]
        cov_html += (f'<div class="colstrip"><div class="nm">{bilingual(en, vn)}</div>'
                     f'<div class="bars">{cells}</div><div class="pct">{c["pct"]}%</div></div>')

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data overview — USR</title>
{seo_meta("Data overview — USR", "Live distributions by country, manufacturer, purpose and standard, with coverage.", "data.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{DATA_CSS}</style>
</head>
<body>
<main class="dwrap">
  <div class="topbar">{nav("", "data")}
    <div class="ctrl"><button id="lang"><span data-lang-en>VN</span><span data-lang-vn>EN</span></button>
    <button id="theme"><span data-lang-en>Dark</span><span data-lang-vn>Tối</span></button></div>
  </div>
  <section class="head">
    <span class="eyebrow">{bilingual("Data Overview", "Tổng quan dữ liệu")}</span>
    <h1>{bilingual("The whole registry, measured by its own data.", "Toàn cảnh đăng ký, đo bằng chính dữ liệu.")}</h1>
    <p class="sub">{bilingual(
      "Every figure below is computed live from the registry — distribution by country, manufacturer, purpose and industry standard. Unverified fields are shown as honest-null, never filled.",
      "Mọi con số tính sống từ tập đăng ký — phân bố theo quốc gia, nhà sản xuất, mục đích và tiêu chuẩn ngành. Phần chưa kiểm chứng hiển thị honest-null, không lấp.")}</p>
    <div class="figs">{figs_html}</div>
  </section>

  <div class="regdiv"><span class="num">01</span><span class="lab">{bilingual("By country", "Theo quốc gia")}</span><span class="ln"></span><span class="meta">{t["country"]} {bilingual("countries", "quốc gia")}</span></div>
  <div class="cols2"><div class="chart">{c1}</div><div class="chart">{c2}</div></div>

  <div class="regdiv"><span class="num">02</span><span class="lab">{bilingual("By manufacturer", "Theo nhà sản xuất")}</span><span class="ln"></span><span class="meta">{t["company"]} {bilingual("makers", "hãng")}</span></div>
  <div class="cols2"><div class="chart">{m1}</div><div class="chart">{m2}</div></div>
  <div class="note"><span class="b">▪</span> {bilingual("Long tail: most manufacturers have 1–2 systems and their attributes are still honest-null (derived-first).", "Đuôi dài: phần lớn hãng chỉ 1–2 hệ thống, thuộc tính còn honest-null (derived-first).")}</div>

  <div class="regdiv"><span class="num">03</span><span class="lab">{bilingual("By purpose", "Theo mục đích")}</span><span class="ln"></span><span class="meta">{t["segment"]} {bilingual("segments", "phân khúc")}</span></div>
  <div class="chart" style="max-width:760px">{seg_html}</div>
  <div class="note"><span class="b">▪</span> {bilingual("'Unclassified' is a real honest-null bucket — not forced into a label.", "'Chưa phân loại' là honest-null thật — không ép nhãn cho đẹp.")}</div>

  <div class="regdiv"><span class="num">04</span><span class="lab">{bilingual("By industry standard", "Theo tiêu chuẩn ngành")}</span><span class="ln"></span><span class="meta">Blue UAS · NDAA</span></div>
  <div class="std">{std_html}</div>
  <div class="note"><span class="b">▪</span> {bilingual("Most systems are not verified against these lists — shown honest-null (hatched), never inferred as 'compliant' or 'not'.", "Phần lớn hệ thống chưa kiểm chứng theo các danh sách này — hiển thị honest-null (gạch đứt), không suy 'tuân thủ' hay 'không'.")}</div>

  <div class="regdiv"><span class="num">05</span><span class="lab">{bilingual("Coverage & integrity", "Độ phủ & toàn vẹn")}</span><span class="ln"></span><span class="meta">11 spec × {t["uav"]}</span></div>
  <div class="cov"><div><div class="big">{t["coverage_pct"]}<span class="u">%</span></div>
    <div class="cap">{bilingual("spec coverage across the set — the empty parts are visible too", "độ phủ spec toàn tập — thấy được cả phần còn trống")}</div></div>
    <div class="spectrum">{cov_html}</div></div>

  <p class="foot mono">{bilingual("Live aggregate · honest-null shown · zero-fabrication · pure SVG/CSS",
                                   "Aggregate sống · honest-null hiện · zero-fabrication · SVG/CSS thuần")}</p>
</main>
<script src="base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


DATA_CSS = """
  .dwrap{max-width:1160px;margin:0 auto;padding:1.2rem 1.4rem 3rem}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1rem}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  .eyebrow{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--brass);font-weight:500}
  .head{padding:1.4rem 0 1rem}
  .head h1{font-family:var(--serif);font-weight:600;font-size:clamp(30px,4.2vw,46px);line-height:1.04;letter-spacing:-.02em;margin:.5rem 0 0}
  .head .sub{font-size:15px;color:var(--muted);max-width:62ch;margin-top:.8rem}
  .figs{display:grid;grid-template-columns:repeat(6,1fr);border-top:2px solid var(--ink);border-bottom:1px solid var(--hair);margin-top:1.6rem}
  @media(max-width:820px){.figs{grid-template-columns:repeat(3,1fr)}}
  @media(max-width:480px){.figs{grid-template-columns:repeat(2,1fr)}}
  .fig{padding:18px 16px;border-left:1px solid var(--hair)}
  .fig:first-child{border-left:none}
  .fig .v{font-family:var(--serif);font-weight:600;font-size:clamp(28px,3.6vw,42px);line-height:1;letter-spacing:-.02em}
  .fig .v .u{font-size:.4em;color:var(--brass);margin-left:3px;font-weight:500}
  .fig .k{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-top:9px;line-height:1.4}
  .regdiv{display:flex;align-items:center;gap:16px;margin:2.6rem 0 1.4rem}
  .regdiv .num{font-family:var(--font-mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--brass)}
  .regdiv .lab{font-family:var(--serif);font-weight:600;font-size:20px;letter-spacing:-.01em}
  .regdiv .ln{flex:1;height:1px;background:var(--hair-strong)}
  .regdiv .meta{font-family:var(--font-mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
  .cols2{display:grid;grid-template-columns:1fr 1fr;gap:40px}
  @media(max-width:820px){.cols2{grid-template-columns:1fr;gap:0}}
  .chart{display:flex;flex-direction:column}
  .brow{display:grid;grid-template-columns:148px 1fr 56px;gap:16px;align-items:center;padding:9px 0;border-top:1px solid var(--hair);text-decoration:none;color:inherit}
  .brow:first-child{border-top:none}
  a.brow:hover .lb{color:var(--brass)}
  @media(max-width:600px){.brow{grid-template-columns:108px 1fr 44px;gap:10px}}
  .brow .lb{font-size:13.5px;color:var(--ink-soft);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .brow .track{height:14px;position:relative}
  .brow .fill{position:absolute;left:0;top:0;height:100%;background:var(--brass);border-radius:2px;min-width:2px}
  .brow .ct{font-family:var(--font-mono);font-size:12.5px;color:var(--ink);text-align:right}
  .brow.other .lb,.brow.other .ct{color:var(--muted)} .brow.other .fill{background:var(--hair-strong)}
  .brow.null .lb{color:var(--faint);font-style:italic}
  .brow.null .track{border:1px dashed var(--hair-strong);border-radius:2px}
  .brow.null .fill{background:repeating-linear-gradient(45deg,var(--faint) 0 2px,transparent 2px 5px);opacity:.5}
  .brow.null .ct{color:var(--faint)}
  .note{font-family:var(--font-mono);font-size:11px;color:var(--muted);margin-top:14px;line-height:1.5}
  .note .b{color:var(--brass)}
  .std{display:grid;grid-template-columns:1fr 1fr;gap:24px}
  @media(max-width:680px){.std{grid-template-columns:1fr}}
  .stdcard{border:1px solid var(--hair-strong);border-radius:12px;padding:22px;background:var(--card-bg);color:var(--card-ink)}
  [data-theme="light"] .stdcard{background:var(--bg);color:var(--ink)}
  .stdcard .nm{font-family:var(--serif);font-weight:600;font-size:18px}
  .stdcard .desc{font-size:12.5px;color:var(--muted);margin:.3rem 0 1.1rem;line-height:1.4}
  .stdcard .big{display:flex;align-items:baseline;gap:8px}
  .stdcard .big .n{font-family:var(--serif);font-weight:600;font-size:40px;line-height:1;letter-spacing:-.02em}
  .stdcard .big .of{font-family:var(--font-mono);font-size:12px;color:var(--muted)}
  .segbar{display:flex;height:12px;border-radius:3px;overflow:hidden;margin-top:16px;gap:2px}
  .segbar .s{height:100%} .segbar .s.yes{background:var(--bp)}
  .segbar .s.unk{background:repeating-linear-gradient(45deg,var(--faint) 0 3px,transparent 3px 7px);border:1px dashed var(--hair-strong)}
  .leg{display:flex;gap:16px;margin-top:12px;flex-wrap:wrap}
  .leg span{font-family:var(--font-mono);font-size:10px;color:var(--muted);display:inline-flex;align-items:center;gap:6px}
  .leg .sw{width:11px;height:11px;border-radius:2px} .leg .sw.yes{background:var(--bp)}
  .leg .sw.unk{background:repeating-linear-gradient(45deg,var(--faint) 0 2px,transparent 2px 4px);border:1px dashed var(--hair-strong)}
  .cov{display:grid;grid-template-columns:auto 1fr;gap:36px;align-items:center}
  @media(max-width:760px){.cov{grid-template-columns:1fr;gap:24px}}
  .cov .big{font-family:var(--serif);font-weight:600;font-size:clamp(46px,7vw,72px);line-height:.9;letter-spacing:-.02em}
  .cov .big .u{font-size:.36em;color:var(--brass)}
  .cov .cap{font-family:var(--font-mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);max-width:34ch;line-height:1.55;margin-top:10px}
  .spectrum{display:grid;grid-template-columns:repeat(11,1fr);gap:9px;align-items:end}
  @media(max-width:680px){.spectrum{grid-template-columns:repeat(6,1fr);gap:7px}}
  .colstrip{display:flex;flex-direction:column;align-items:center;gap:8px}
  .colstrip .bars{width:100%;display:grid;grid-template-rows:repeat(24,1fr);gap:2px;height:150px}
  .colstrip .c.on{background:var(--brass);border-radius:1px} .colstrip .c.off{background:var(--hair);border-radius:1px}
  .colstrip .pct{font-family:var(--font-mono);font-size:10px;color:var(--ink)}
  .colstrip .nm{font-family:var(--font-mono);font-size:8px;color:var(--faint);text-align:center;line-height:1.2;height:22px;display:flex;align-items:center}
  .foot{border-top:1px solid var(--hair);margin-top:3rem;padding-top:1.2rem;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
"""


def main():
    site = json.loads(SITE.read_bytes())
    ov = compute(site)
    DATA.write_text(json.dumps(ov, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    PAGE.write_text(render(ov))
    print("data.html + data-overview.json: country %d · maker %d · segment %d · coverage %d%%"
          % (len(ov["country"]), len(ov["maker"]), len(ov["segment"]), ov["totals"]["coverage_pct"]))


if __name__ == "__main__":
    main()
