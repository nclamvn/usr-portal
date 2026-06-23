# X-RAY — USR Portal (rtr-news) · handover, cập-nhật sau P04

> Mục-đích: phiên Chủ thầu/Thợ mới đọc file này là tiếp được liền, không dò lại cả chuỗi.
> Working dir: `/Users/os/RtR/rtr-news/portal`. Tất cả lệnh chạy từ đây.

## 1 · Vai & giao-thức
- **Chủ thầu** (người) ra design-language/spec (TIP) + VERIFY engine-checked. **Thợ** (agent ở env có data) wire vào pipeline, trả Completion Report.
- Kỷ-luật: **only-trust-engine** (xác bằng chạy code, không bằng lời) · **conflict → REPORT, không tự-quyết** · một-TIP-một-đợt, gates xanh mới qua đợt sau.

## 2 · Bất-biến (non-negotiable, đứng vững qua mọi đợt)
- **Zero-fabrication**: chỉ render giá-trị thật; unverified/absent → null; KHÔNG bịa số/rotor/bài.
- **Honest-null hai-chiều**: null hiển-thị "—"/dashed/pip-rỗng ở mọi mặt; site-null ⇔ render-null (auditor canh).
- **Disputed giữ mở**: giữ cả claim, không lặng-lẽ chọn (vd Switchblade mtow 1.6/3.6/2.3).
- **Provenance là sản-phẩm**: mọi số truy URL nguồn + tier A/B/C.
- **Aggregate tính SỐNG** mỗi build (GLOBAL CONSTRAINT) · **một-nguồn-sự-thật** `out/site-data.json`.
- **Gates + teeth fail-loud · idempotent** (build 2 lần = byte-identical).

## 3 · Kiến-trúc dữ-liệu (một chiều)
`out/master_registry.json` (200 real entity, nguồn gốc registry) → `build_site_data.py` → **`out/site-data.json`** (adapter, single source: field-cells {value,status,source_tier,sources}, labels song-ngữ, field_groups, aggregates{status_counts,tier_counts,spec_fill_rate,**spec_range**}, frame_glyph) → mọi builder đọc site-data.

## 4 · Design language
- **`base/portal-in-action.html`** = design-system-of-record cho app shell (hero/card/blueprint).
- **`base/newsroom-specimen.html`** = record cho News/Analysis idiom.
- **`base/visual-language-specimen.html`** (ở `/Users/os/Downloads/`, KHÔNG trong repo) = specimen P01–P03 (khung/glyph/track).
- Token canonical ở `base/design-system.css`; alias `--serif/--sans/--mono/--card/--wm/--maxw` để specimen resolve. `.tg` base canonical (facet = `[aria-pressed]`); `.ghost` chỉ dark (`.card/.feat .ghost`); cream-figure = `.statfig`.

## 5 · Surfaces & builder (pipeline `build_all.sh`, 8 nhóm/13 lệnh)
1. `build_site_data.py` → site-data (+idempotent sha)
2. `verify_site_data.py` (honest-null hai chiều · aggregates live · **frame_glyph no-leak** · **spec_range live** · coverage)
3. `build_reference.py` (reference.html — light rows: glyph + meta + **7-pip** + chips) + `build_detail.py` (200 `entity/<slug>.html`: glyph lớn tự-vẽ + **micro-track log** + nguồn tier + honest-null + disputed range)
4. `build_news.py` (news-front trên home + `news/<slug>`) + `build_analysis.py` (`analysis/<slug>` long-form: 4-câu-hỏi + figure-live + rail)
5. `build_index.py` (home: bar → hero → newsroom → analysis feature → **plate tối record-status + ma-trận coverage 11×200** → browse) + `build_bundle.py` (**bundle.html** một-file)
6. `verify_content.py` (analysis: 4Q/entity-tag/tier-A · figure trace registry · style-guide)
7. `check_i18n.py` (en==vn) · reduced-motion/focus static check
8. `audit_headless.js` (Chrome CDP: 8 base + hero + filtered<100ms + 2 detail + track-two-way + 3 editorial + **teeth**)

## 6 · Staging thị-giác (ĐÓNG — P01→P04, tất cả VERIFY xanh)
- **P01** `c30cdb1` — plate light/dark (band tối viền tách) + divider registration + hierarchy. Presentation thuần (site-data sha bất-biến).
- **P02** `95b0fa3` — 9 frame-glyph bám `airframe_type` thật, map toàn-phần, **cấm multirotor→quad** (teeth: inject→exit 2). 200/200 glyph.
- **P03** `83c5c74` — micro-track **log** (đáy-thang 0.073kg→tick 2%) + ma-trận coverage thật (541/2200=25%, ==aggregate) + glyph tự-vẽ (gate `:root.js`, no-JS→solid). teeth: tamper spec_range→exit 2.
- **P04** `5f43e58` — 7-pip record-fullness/row (filled 464==numeric-present 464). Presentation thuần.
- Quyết-định kiến-trúc giữ: **rows = light index; micro-track ở DETAIL** (không đảo index≠detail). D-1 (glyph map) + D-2 (log scale) thực-thi bằng engine.

## 7 · Commits (full hash, oldest→newest; nhánh `main`, HEAD `5f43e58`, tree sạch)
```
3d48bda  portal đầy đủ (200 entity, reference/detail/home/newsroom)
e07a929  bundle.html một-file + detail_fragment dùng chung
5c3010d  uav-200.xlsx export từ site-data
c30cdb1  TIP-P01 plate/divider/hierarchy
95b0fa3  TIP-P02 frame glyphs + P01 dark-band polish
83c5c74  TIP-P03 micro-track log + coverage matrix + glyph self-draw
5f43e58  TIP-P04 record-fullness pip strip
```

## 8 · Deliverables @ `portal/`
- **Web**: `index.html`, `reference.html`, `entity/*.html` (200), `analysis/*.html` (1 sample), `news/*.html` (5 sample). Phục-vụ: `python3 -m http.server 8011 --bind 127.0.0.1` → http://127.0.0.1:8011/
- **Gửi đội**: `bundle.html` (một-file tự-chứa, 200 thật, mở từ ổ-đĩa/email) · `uav-200.xlsx` (4 sheet: UAV 200 honest-null=ô-trống · Nguồn&tier · Tranh-chấp · Tổng-sống công-thức).
- **Code**: 12 `build_*.py`/`verify_*.py`/`glyphs.py`/`make_xlsx.py` · `base/` (css/js/specimens) · `content/` (articles.json, glossary.json — **sample seed**, người viết thay nội-dung thật).

## 9 · Nội-dung biên-tập (quyết-định (b) đã chốt)
News/Analysis là vỏ tuân-chuẩn + **bài seed đánh-dấu** (`sample:true` → banner "nội dung mẫu"). Figure số THẬT từ registry; văn xuôi là mẫu. Bài thật là việc người viết: sửa `content/articles.json`. Xem [[newsroom-pillar]].

## 10 · Push status
- remote `origin = https://github.com/nclamvn/usr-portal.git` (đã set) · **CHƯA push** (no upstream).
- Bước của Chủ thầu (Thợ không cầm token). Lệnh một-dòng (thay PAT, scope repo):
  ```
  curl -s -H "Authorization: token PAT" https://api.github.com/user/repos -d '{"name":"usr-portal","private":true}' >/dev/null && git push -u https://PAT@github.com/nclamvn/usr-portal.git main
  ```

## 11 · Mở (chờ Chủ thầu)
- Pip dày/nhạt, nét glyph, độ-đậm track/ma-trận trên cream+dark = **mắt Chủ thầu** (engine chỉ xác cấu-trúc/overlap, không pixel).
- Push (#10).

## 12 · Cách verify lại (bất-kỳ lúc nào)
`cd portal && ./build_all.sh` → exit 0 + "build_all: OK". Teeth có thật: tamper `out/site-data.json` (frame_glyph multirotor→quad, hoặc spec_range min) → `verify_site_data.py` exit 2; khôi-phục bằng `build_site_data.py`.

## 13 · Bất-biến tuyệt-đối khi sửa tiếp
KHÔNG bịa · KHÔNG hardcode aggregate/min-max/coverage · KHÔNG đổi dataset trong lớp trình-bày · KHÔNG redefine token canonical · giữ static-gen + gates + teeth + idempotent · conflict với quyết-định cũ (index≠detail…) → REPORT, không tự-quyết. Xem [[portal-design-ethos]].
