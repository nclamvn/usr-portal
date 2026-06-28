#!/usr/bin/env python3
"""build_aggregation.py — TIP-NEWS-REALTIME Task 2 (render dòng A) + trang đọc in-site.

Aggregation card = link + tóm-tắt-GỐC + outlet + tier. KHÔNG nhúng body/ảnh người ta.
- aggregation_block(): section "Tin nhanh" cho trang chủ (tiêu-đề → trang in-site, không nhảy ra ngoài).
- main(): ghi news-card/<id>.html — trang đọc TRONG SITE mỗi card (tóm-tắt của ta + provenance + nút
  'đọc bản gốc ↗'). Tường bản-quyền: trang in-site chỉ là nội-dung CỦA TA, bản đầy-đủ ở nguồn.
Gác bởi verify_aggregation.py (7 teeth); trang vào sitemap (build_sitemap/verify_seo DIRS += news-card)."""
import json
from pathlib import Path
from build_reference import bilingual, esc
from header import header
from footer import footer
from seo import meta as seo_meta

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "content" / "news-cards.json"
OUTDIR = ROOT / "news-card"


def load_cards():
    if not CARDS.exists():
        return []
    return json.loads(CARDS.read_text(encoding="utf-8")).get("cards", [])


def _sorted(cards):
    return sorted(cards, key=lambda c: (c.get("date") or "0000-00-00"), reverse=True)


def _tierlbl(tier):
    t = esc(str(tier or "?"))
    return f'<span class="tier{"" if t.startswith("A") else " bb"}">tier {t}</span>'


def _card_html(c, prefix=""):
    cid = esc(c.get("id", ""))
    date = esc(c.get("date") or "")
    datespan = f'<span class="agg-date">{date}</span> · ' if date else ""
    # media-forward: thumbnail from the card's LOCAL open-licensed image (cc/cc0), credit overlaid.
    # Only images/content/ (gated open-licensed) ever render here — never a pending third-party hotlink.
    img = c.get("image")
    thumb = ""
    if img and str(img).lstrip("/").startswith("images/content/"):
        thumb = (f'<a class="agg-thumb" href="{prefix}news-card/{cid}.html">'
                 f'<img src="{prefix}{esc(str(img).lstrip("/"))}" alt="" loading="lazy">'
                 f'<span class="agg-cred">{esc(c.get("image_credit",""))}</span></a>')
    return (
        '<article class="agg-card">'
        f'{thumb}'
        f'<span class="agg-field">{esc(c.get("field",""))}</span>'
        f'<h4 class="agg-ttl"><a href="{prefix}news-card/{cid}.html">{esc(c.get("source_title",""))}</a></h4>'
        f'<p class="agg-sum">{esc(c.get("summary",""))}</p>'
        f'<div class="agg-meta"><span class="agg-outlet">{esc(c.get("outlet",""))}</span> · {_tierlbl(c.get("tier"))} · '
        f'{datespan}<a class="agg-src" href="{prefix}news-card/{cid}.html">{bilingual("read","đọc")} →</a></div>'
        '</article>')


def aggregation_block(prefix="", limit=12):
    allcards = _sorted(load_cards())
    cards = allcards[:limit]
    if not cards:
        return ""
    items = "".join(_card_html(c, prefix) for c in cards)
    more = ""
    if len(allcards) > len(cards):
        more = (f'<a class="agg-all" href="{prefix}news-card/index.html">'
                f'{bilingual("See all", "Xem tất cả")} {len(allcards)} →</a>')
    return (
        '<section class="aggwrap" data-audit="agg">'
        '<div class="agg-head">'
        f'<b class="agg-kicker">{bilingual("Quick headlines · link + sourced summary", "Tin nhanh · link + tóm-tắt có nguồn")}</b>'
        f'<span class="agg-count">{len(cards)}</span>{more}</div>'
        f'<div class="agg-grid">{items}</div></section>')


def _index_item(c):
    """Card item trên trang liệt-kê (trong news-card/), link tới sibling <id>.html."""
    cid = esc(c.get("id", ""))
    date = esc(c.get("date") or "")
    datespan = f'<span class="agg-date">{date}</span> · ' if date else ""
    return (
        '<article class="agg-card">'
        f'<span class="agg-field">{esc(c.get("field",""))} · {esc(c.get("stratum",""))}</span>'
        f'<h4 class="agg-ttl"><a href="{cid}.html">{esc(c.get("source_title",""))}</a></h4>'
        f'<p class="agg-sum">{esc(c.get("summary",""))}</p>'
        f'<div class="agg-meta"><span class="agg-outlet">{esc(c.get("outlet",""))}</span> · {_tierlbl(c.get("tier"))} · '
        f'{datespan}<a class="agg-src" href="{cid}.html">{bilingual("read","đọc")} →</a></div>'
        '</article>')


def render_index(cards):
    """Trang liệt-kê TẤT CẢ tin nhanh (news-card/index.html) — toàn-bộ card, không giới-hạn."""
    cards = _sorted(cards)
    items = "".join(_index_item(c) for c in cards)
    title = bilingual("All quick headlines", "Tất cả tin nhanh")
    return f"""<!DOCTYPE html>
<html lang="vi" data-theme="light" data-lang="vn">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — USR</title>
{seo_meta(title + " — USR", "Tổng-hợp tin nhanh có nguồn về UAV và kinh-tế tầm thấp.", "news-card/index.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
</head>
<body>
{header("../")}
<main class="ncard-list">
  <a class="ncard-back" href="../index.html">← {bilingual("Home","Trang chủ")}</a>
  <h1 class="ncard-ttl">{title}</h1>
  <section class="aggwrap" data-audit="agg">
    <div class="agg-head"><b class="agg-kicker">{bilingual("Quick headlines · link + sourced summary","Tin nhanh · link + tóm-tắt có nguồn")}</b><span class="agg-count">{len(cards)}</span></div>
    <div class="agg-grid">{items}</div>
  </section>
</main>
{footer("../")}
<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""


def render_card_page(c):
    """Trang đọc IN-SITE một card. Card 'quick' = tóm-tắt + link. Card 'nâng' (có body) = bài data-note
    đầy-đủ DO TA VIẾT (lời của ta, ground từ nguồn, KHÔNG chép bài gốc) + ảnh open-licensed (có credit)."""
    cid = c.get("id", "")
    title = esc(c.get("source_title", ""))
    url = esc(c.get("source_url", ""))
    outlet = esc(c.get("outlet", ""))
    date = esc(c.get("date") or "—")
    # media: chỉ ảnh local open-licensed (đã gated) + credit; KHÔNG ảnh http ngoài (verify_aggregation chặn)
    img = c.get("image")
    image_html = ""
    if img:
        image_html = (f'<figure class="ncard-fig"><img src="../{esc(img.lstrip("/"))}" alt="{title}" loading="lazy">'
                      f'<figcaption>{esc(c.get("image_credit",""))}</figcaption></figure>')
    # body: bài gốc của ta (list đoạn). Không có body → chỉ tóm-tắt (card quick).
    body = c.get("body") or []
    if body:
        body_html = f'<p class="ncard-sum">{esc(c.get("summary",""))}</p>' + "".join(
            f'<p class="ncard-body">{esc(p)}</p>' for p in body)
        note = bilingual(
            "Original write-up by USR from the cited source (our words, not a reproduction). Read the source for the full original.",
            "Bài do USR viết từ nguồn dẫn (lời của ta, không tái-bản). Đọc bản gốc tại nguồn để xem đầy-đủ.")
    else:
        body_html = f'<p class="ncard-sum">{esc(c.get("summary",""))}</p>'
        note = bilingual(
            "Quick headline: original title + a USR-written one-line summary + a link. We do not reproduce the source article — read it in full at the source.",
            "Tin nhanh: tiêu-đề gốc + một câu tóm-tắt do USR viết + link. Chúng tôi KHÔNG tái-bản bài gốc — đọc đầy-đủ tại nguồn.")
    return f"""<!DOCTYPE html>
<html lang="vi" data-theme="light" data-lang="vn">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — USR Tin nhanh</title>
{seo_meta(title + " — USR", esc(c.get("summary",""))[:150], f"news-card/{cid}.html")}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base/design-system.css">
</head>
<body>
{header("../")}
<main class="ncard-wrap">
  <a class="ncard-back" href="index.html">← {bilingual("All quick headlines","Tất cả tin nhanh")}</a>
  <span class="ncard-field">{esc(c.get("field",""))} · {esc(c.get("stratum",""))}</span>
  <h1 class="ncard-ttl">{title}</h1>
  {image_html}
  {body_html}
  <div class="ncard-meta">
    <span>{bilingual("Source","Nguồn")}: <b>{outlet}</b></span> · {_tierlbl(c.get("tier"))} · <span>{date}</span>
  </div>
  <a class="ncard-orig" href="{url}" target="_blank" rel="noopener">{bilingual("Read the original at","Đọc bản gốc tại")} {outlet} ↗</a>
  <p class="ncard-note">{note}</p>
</main>
{footer("../")}
<script src="../base/base.js"></script>
<script>
  USRBase.initTheme(document.getElementById("theme"));
  USRBase.initI18n(document.getElementById("lang"));
  document.documentElement.dataset.audit = "ready";
</script>
</body>
</html>
"""


def main():
    cards = load_cards()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for c in cards:
        if c.get("id"):
            (OUTDIR / f'{c["id"]}.html').write_text(render_card_page(c), encoding="utf-8")
    (OUTDIR / "index.html").write_text(render_index(cards), encoding="utf-8")
    print(f"aggregation: {len(cards)} card · {len(cards)} trang đọc + 1 trang liệt-kê (index) → news-card/")


if __name__ == "__main__":
    main()
