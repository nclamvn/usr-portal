#!/usr/bin/env python3
"""TIP-P3.2 — Review engine (mode E, but SPEC-DERIVED = mechanism, not editorial judgment, so
zero-fab holds). Each capability dimension scores a UAV by the LOG-scaled position of its spec value
within the registry's range (0–100, same log idiom as the micro-track). A dimension with no value is
HONEST-NULL — not scored, NOT zero (never penalised for missing data). Total = mean of scored
dimensions; completeness (scored N/6) is shown so sparse-but-high is distinguishable. One source of
truth: review-data.json is a live projection of site-data (verify_review proves no drift). Ranked.
"""
import json, pathlib
from build_detail import log_pos
from footer import footer
from build_reference import bilingual, esc
from nav import nav
from header import header
from seo import meta as seo_meta, review_ld

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
DATA = ROOT / "out" / "review-data.json"
PAGE = ROOT / "review.html"

# capability dimensions — only specs where "higher = more capable" (mtow is size, excluded).
DIMS = [("max_payload_kg", "Payload", "Tải trọng"), ("endurance_min", "Endurance", "Thời gian bay"),
        ("max_range_km", "Range", "Tầm bay"), ("max_link_km", "Datalink", "Datalink"),
        ("max_speed_ms", "Speed", "Tốc độ"), ("service_ceiling_m", "Ceiling", "Trần bay")]
DKEYS = [k for k, _, _ in DIMS]


def build_data(site):
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    rng = site["aggregates"]["spec_range"]
    rows = []
    for e in uavs:
        scores = {}
        for k in DKEYS:
            v = (e.get(k) or {}).get("value")
            r = rng.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool) and r:
                scores[k] = round(log_pos(v, r["min"], r["max"]))
            else:
                scores[k] = None   # honest-null — not scored, NOT zero
        present = [s for s in scores.values() if s is not None]
        total = round(sum(present) / len(present)) if present else None
        rows.append({"slug": e["slug"], "name": (e.get("name") or {}).get("value") or e["slug"],
                     "maker": (e.get("manufacturer") or {}).get("value") or "—",
                     "scores": scores, "total": total, "scored": len(present), "of": len(DKEYS)})
    # rank by total desc; unscored (total None) sink to the bottom; stable by slug
    rows.sort(key=lambda x: (x["total"] is not None, x["total"] or 0, x["slug"]), reverse=True)
    return {"schema": "review-data/1",
            "dims": [{"key": k, "en": en, "vn": vn} for k, en, vn in DIMS],
            "spec_range": {k: rng[k] for k in DKEYS if k in rng}, "uavs": rows}


REVIEW_CSS = """
  .rwrap{max-width:var(--w-wide);margin:0 auto;padding:1.4rem 1.4rem 3rem}
  .topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:1rem}
  .ctrl{display:flex;gap:.5rem}
  .ctrl button{background:transparent;color:var(--ink);border:1px solid var(--hair);border-radius:var(--radius);padding:.35rem .6rem;font-family:var(--font-body);font-size:.8rem;cursor:pointer}
  h1{margin:0 0 .2rem;font-family:var(--font-head)}
  .lead{color:var(--muted);font-size:.85rem;margin-bottom:.8rem}
  .method{border:1px solid var(--hair-strong);border-radius:10px;padding:14px 16px;font-size:.78rem;color:var(--ink-soft);line-height:1.5;margin-bottom:1.4rem;background:color-mix(in srgb,var(--brass) 3%,transparent)}
  .method b{color:var(--brass)}
  table.rv{width:100%;border-collapse:collapse;font-size:.8rem}
  table.rv th,table.rv td{border-bottom:1px solid var(--hair);padding:.5rem .45rem;text-align:left;vertical-align:middle}
  table.rv thead th{font-family:var(--font-mono);font-size:.64rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);position:sticky;top:0;background:var(--bg)}
  table.rv td.nm a{color:inherit;text-decoration:none;font-weight:500}
  table.rv td.nm a:hover{color:var(--brass)} table.rv td.nm .mk{display:block;font-family:var(--font-mono);font-size:.66rem;color:var(--muted)}
  .dim{display:block;height:6px;border-radius:2px;background:var(--hair);position:relative;min-width:40px}
  .dim .f{position:absolute;left:0;top:0;height:100%;background:var(--brass);border-radius:2px}
  .dim.null{background:transparent;border-top:1px dashed var(--hair-strong);height:0;margin:.5rem 0}
  .sc{font-family:var(--font-mono);font-size:.66rem;color:var(--muted);display:block;text-align:right;margin-top:2px}
  .sc.null{color:var(--faint);font-style:italic}
  .tot{font-family:var(--font-head);font-weight:600;font-size:1rem}
  .tot.null{color:var(--muted);font-weight:400;font-size:.82rem;font-family:var(--font-mono)}
  .cmpl{font-family:var(--font-mono);font-size:.66rem;color:var(--muted)}
  .rank{font-family:var(--font-mono);font-size:.7rem;color:var(--faint);text-align:right}
"""


def cell(score):
    if score is None:
        return f'<td><span class="dim null"></span><span class="sc null">—</span></td>'
    return (f'<td><span class="dim"><span class="f" style="width:{score}%"></span></span>'
            f'<span class="sc">{score}</span></td>')


def render(rv, labels):
    dim_th = "".join(f'<th>{bilingual(d["en"], d["vn"])}</th>' for d in rv["dims"])
    review_ld_blocks = "".join(review_ld(u["name"], u["total"], "review.html") for u in rv["uavs"])
    rows = ""
    for i, u in enumerate(rv["uavs"], 1):
        tot = (f'<span class="tot">{u["total"]}</span>' if u["total"] is not None
               else f'<span class="tot null">{bilingual("n/a", "—")}</span>')
        cells = "".join(cell(u["scores"][k]) for k in DKEYS)
        rows += (f'<tr><td class="rank">{i}</td>'
                 f'<td class="nm"><a href="uav/{esc(u["slug"])}.html">{esc(u["name"])}</a>'
                 f'<span class="mk">{esc(u["maker"])}</span></td>'
                 f'{cells}<td>{tot}</td><td class="cmpl">{u["scored"]}/{u["of"]}</td></tr>')
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Capability review — USR</title>
{seo_meta("Capability review — USR", "Spec-derived capability scores across the registry; missing specs are honest-null, never zero.", "review.html")}
{review_ld_blocks}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{REVIEW_CSS}</style>
</head>
<body>
{header("", "review")}
<main class="rwrap">
  <h1>{bilingual("Capability review", "Đánh giá năng lực")}</h1>
  <div class="lead">{bilingual("Spec-derived, ranked. No editorial judgement.", "Suy từ thông số, xếp hạng. Không phán đoán biên tập.")}</div>
  <div class="method"><span data-lang-en><b>Method:</b> each dimension scores a system by the log-scaled position of its spec within the registry's range (0–100) — the same scale as the micro-track. <b>Total</b> = mean of scored dimensions. A spec without a value is <b>honest-null</b> (—), not zero: a system is never penalised for data we don't have. 'Scored N/6' shows how complete the evidence is, so sparse-but-high is distinguishable.</span><span data-lang-vn><b>Phương pháp:</b> mỗi chiều chấm một hệ thống theo vị trí log của thông số trong dải dữ liệu (0–100) — cùng thang micro-track. <b>Tổng</b> = trung bình các chiều có điểm. Thông số không có giá trị là <b>honest-null</b> (—), không phải 0: không hệ thống nào bị phạt vì dữ liệu ta chưa có. 'Chấm N/6' cho thấy độ đầy bằng chứng, để phân biệt thưa-nhưng-cao.</span></div>
  <table class="rv"><thead><tr><th>#</th><th>{bilingual("System", "Hệ thống")}</th>{dim_th}<th>{bilingual("Total", "Tổng")}</th><th>{bilingual("Scored", "Chấm")}</th></tr></thead>
  <tbody>{rows}</tbody></table>
</main>
{footer("")}
<script src="base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


def main():
    site = json.loads(SITE.read_bytes())
    rv = build_data(site)
    DATA.write_text(json.dumps(rv, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    PAGE.write_text(render(rv, site["labels"]))
    scored = sum(1 for u in rv["uavs"] if u["total"] is not None)
    print(f"review.html + review-data.json: {len(rv['uavs'])} uav · {scored} scored · {len(DKEYS)} dims")


if __name__ == "__main__":
    main()
