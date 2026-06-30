# X-RAY · USR Portal (Uncrewed Systems Review) · handover gửi Chủ thầu

> Handover + báo-cáo dataset/kiến-trúc, đo SỐNG từ engine (không từ trí nhớ).
> HEAD `75a55f0b` · nhánh `main` · **148 commit** · repo PUBLIC `github.com/nclamvn/usr-portal` · prod `usr-portal.vercel.app` (auto-deploy khi push `main`).
> Working dir: `/Users/os/RtR/rtr-news/portal`. Một lệnh verify: `./build_all.sh` → "build_all: OK".
>
> **Snapshot:** static-gen, zero-runtime · **444 UAV / 433 family / 186 hãng (derived, alias-merged) / 33 nước** ·
> 860 trang HTML · 20 builder + 27 verifier + 26 teeth · ~11K LOC Python + 864 dòng design-system.css.

---

## 1 · Vai & giao-thức
- **Chủ thầu** ra Contract/TIP có cổng; **Thợ** thực-thi → chạy gate fail-loud → secret-scan → commit → push → báo cáo; Chủ thầu **VERIFY độc-lập** ("chỉ tin engine").
- Một lệnh: `./build_all.sh` (exit≠0 = chặn; idempotent, sha-check build hai lần). Push `main` = deploy production.
- Luật nhà: zero-fabrication · KHÔNG em-dash trong commit/newsroom · "Real-time Robotics" t thường · secret-scan trước push · commit kết `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## 2 · Bất-biến (iron rules, không được phá)
- **Zero-fabrication**: mọi số hoặc recompute-sống từ registry, hoặc dẫn nguồn + tier.
- **honest-null hai chiều**: thiếu nguồn → để trống; ô trống ≠ "đã xác nhận không". ~44% cell là honest-null (cố-ý phơi).
- **disputed-keep-all** (#10): nguồn lệch → giữ TẤT CẢ claim + xuất-xứ, không ép một số.
- **figure-trace recompute-live**: số trong bài = giá-trị tính sống; registry đổi → `CONTENT_FIGURE_DRIFT` bắt drift.
- **một-chiều E→D**: registry nuôi mọi bề-mặt; bài tham-chiếu dữ-liệu, dữ-liệu không suy từ bài.
- Còn lại: index≠detail · brass-restraint · bilingual EN/VN · light/dark theme-pure · ảnh chỉ CC/owned + credit + `license_status`.

## 3 · DATASET (provenance is the product)
- **`out/master_registry.json`** (schema 1.1.0, git-tracked, NGUỒN GỐC đọc-chỉ-đọc): **433 family · 444 variant**
  (đơn-vị đếm = variant). Mỗi thuộc-tính là một **cell**:
  `{value, status, confidence, sources:[{url, tier(A/B/C), retrieved, claimed_value}], last_verified, inherited_from}`.
  Family mang thuộc-tính chung (maker/country/airframe/propulsion); variant override + spec.
- **`out/site-data.json`** (schema 2): phóng-chiếu SỐNG = **444 uav + 186 company** (company derive từ manufacturer,
  alias-merged, không sourcing mới) + aggregates. Sha256 chốt idempotent.
- **field_status (~8.9K cell):** verified 2.905 · sourced 1.700 · derived 267 · unverified 37 · disputed 6 · honest-null (None) 3.965.
- **source_tier:** A 2.345 · B 1.549 · C 586 · derived 267 (sàn tin-cậy nghiêng A).
- **Độ-phủ spec (~32% tb, sparse-is-a-feature):** mtow **64%** (284) · endurance **64%** (282) · speed 53% (236) ·
  payload 52% (232) · range 48% (212) · ceiling 37% (164) · link 16% (69) · ndaa 8% (35) · blue 7% (33).
- **Phân-bố:** 33 nước (US 144 · China 114 · Israel 29 · Germany 23 · Turkey 17 · Russia 16 …) · 13 phân-khúc
  (military_tactical 188 · enterprise 39 · consumer 32 · loitering_munition 26 · delivery 25 …) ·
  airframe (fixed-wing 177 · multirotor 82 · vtol_fixedwing 65 · quadcopter 47 …) · Blue UAS 26 · NDAA 28.
- **HQ trụ-sở (TIP-MAP nhịp D):** **99 / 186 hãng có `hq_city` kèm nguồn + tier** (top-102 maker = ~80% hệ-thống);
  87 còn lại honest-null. Toạ-độ qua gazetteer Public-Domain `CITY_COORD` (key = chuỗi `hq_city` đúng nguyên-văn).
- **Kho `content/` (sự-thật viết tay):** newsroom 54 bài `.md` (data-note/company-profile/explainer/data-report) ·
  news-cards 61 thẻ (dòng A: link ngoài + tóm-tắt USR, copyright-safe) · media 52 asset CC/owned (rights-gated) ·
  glossary 5 · LAE registry riêng (`content/lae-registry.json`, 50 entity, chiến-dịch refinery, tách khỏi registry UAV) ·
  `company_aliases.json` (6 merge tường-minh) · `companies.json` (99 golden record sourced).

## 4 · KIẾN-TRÚC

### 4.1 Luồng dữ-liệu (một chiều)
```
content/ (viết tay: companies · company_aliases · media · news-cards · articles · glossary · lae-registry)
      │  curate →
 out/master_registry.json     ← NGUỒN GỐC (cell có provenance, git-tracked)
      │  build_site_data.py    (derive company · canon country/slug/alias · aggregates LIVE)
 out/site-data.json           ← phóng-chiếu sống (entities + aggregates)
      │  20 builder đọc-chỉ-đọc
 860 trang .html tĩnh          → push GitHub → Vercel deploy
```

### 4.2 Pipeline `build_all.sh` (fail-loud `set -e`, idempotent sha-check, ~87 lượt python/node)
site-data + verify → reference/detail/company/taxonomy → newsroom/analysis/knowledge →
monitor/home/registry-cards/compare/search/data/review/aggregation/sitemap/bundle → **toàn-bộ cổng gate**.

### 4.3 Bề-mặt (860 .html)
`uav/444 · company/186 · country/34 · segment/14 · airframe/9 · compliance/3 · news/59 · news-card/62 ·
knowledge/5 · weight/7 · flight-time/6 · analysis/2` + top-level
(`index · reference · compare · data · review · search · knowledge · news · monitor · registry · bundle`).

### 4.4 Hệ-thống gate (răng = chứng-cứ tự-bites)
**27 verifier + 26 teeth.** Mỗi verifier có teeth song-hành: tiêm lỗi → buộc exit 2 → restore → real-data pass.
Triết-lý: cổng không có răng là cổng giả.
- **data-integrity:** site_data (honest-null hai chiều · aggregates-live), home, data (+ drift `spec_range`).
- **provenance:** media rights (enum quyền · owner/license thật), media ledger.
- **graph/SEO/nav:** graph (0 dangling) · taxonomy · breadcrumb · redirects · seo (sitemap + JSON-LD) · search · prd_coverage.
- **zero-fab viz:** graphics (số trong SVG recompute · 0 hex) · frontpage.
- **content:** newsroom (figure-trace + format + sources + disclosure) · newsroom_feed · aggregation (8 răng) · knowledge · review.
- **chrome khoá:** header + footer (byte-identical mọi trang) · ux1.
- **trình-bày:** check_i18n (en==vn cân) · THEME_PURITY (luminance polarity light/dark) · svg (fill governance).
- **bản-đồ (TIP-MAP):** `verify_map` + `teeth_map` (8 răng) · xem §5.
- **headless (`audit_headless.js`):** overlap=0 ×4 theme/lang · filtered-state (<100ms + URL) · mobile-390 no-overflow.

### 4.5 Design system
`base/design-system.css` (864 dòng, token light/dark) + `base/base.js` (312 dòng: theme/i18n/registry-sort/reveal).
Editorial-industrial: cream/dark, serif (Source Serif 4) + mono (IBM Plex) + brass `#9B6B1C` chỉ cho ACTIVE; hairline; reg-frame.
Width token `--w-wide 1180` / `--w-read 760`. `data-lang` = `vn`/`en` (KHÔNG `vi`).
**Spec-table language (đã lan toàn-site):** `.ri-spark` thanh amber `--bp` (fleet-position log) · `.ri-tier[data-t]`
badge (A brass, B/C muted) · honest-null = rail gạch-đứt · bảng 5 spec sortable (MTOW/Range/Endurance/Payload/Ceiling).
**Luật màu một-ngôn-ngữ:** amber `--bp` = MỌI thanh độ-lớn; brass = tier-A + cột active + accent đơn.

## 5 · TIP-MAP (bản-đồ phân-bố nhà sản-xuất, đã đủ nhịp A→D)
Engine `geo_map.py` (equirectangular `_proj`, token-only paint, nhãn HTML bilingual) + asset Public-Domain
`base/world-countries.json` (Natural Earth 110m admin-0) · `base/world-land.json` (coastline). Gate `verify_map` + `teeth_map`.
- **A · `/data` hybrid:** choropleth tint (33 nước) + chấm tỉ-lệ (`CENTROID`), placed 444/444.
- **B · hero + locator:** mini-map "chữ-ký" trang chủ (link `/data`) + locator một-chấm mỗi `/country`.
- **C · filter map:** mỗi trang `/segment`, `/airframe`, `/compliance` mang bản-đồ phân-bố-nước CỦA subset đó
  (`data-filter="segment:.."`); gate recompute subset từ site-data.
- **D · HQ pins:** 99 pin hình-thoi tại trụ-sở hãng trên `/data` (mục 02), to theo fleet, link `/company`; chỉ vẽ khi
  `hq_city` resolve trong `CITY_COORD`, còn lại honest-null. Caption sống: "99 of 186 makers mappable".
- **6 loại gate:** `MAP_FIGURE_DRIFT` · `MAP_FILTER_DRIFT` · `MAP_UNPLACED` · `MAP_NULL_FAKED` · `MAP_DANGLING` ·
  `MAP_THEME_LEAK` + `MAP_PIN_FAKED` (Tier-3). `teeth_map` chứng **8 răng** đều cắn.
- **Dedup alias entity** (cùng cơ-chế `company_aliases.json`): đã gộp **autel · freefly · qods · insitu**
  (Textron giữ riêng = parent/subsidiary thật). 6 alias tổng.

## 6 · Số liệu hiện-trạng (snapshot, sống)
- Registry: **444 UAV · 186 hãng · 33 nước · 13 phân-khúc** · độ-phủ spec ~32%.
- Nguồn: **2.345 A · 1.549 B · 586 C · 267 derived**. Ô: **2.905 verified · 1.700 sourced · 6 disputed (giữ cả) · 37 unverified · 3.965 honest-null**.
- HQ: **99/186 hãng có trụ-sở kèm nguồn** (top-102 ~80% hệ-thống) · 99 pin trên `/data`.
- Nội-dung: 54 bài newsroom · 61 card · 50 entity LAE · 5 thuật-ngữ · 52 media asset.

## 7 · Mở · chờ Chủ thầu/Chủ nhà quyết
- **HQ đuôi dài**: 87/186 hãng còn honest-null HQ (rank 103+, obscure). Mở-rộng tiếp hay dừng ở ~80%.
- **Skydio X10 endurance** (40 vs 65, disputed): có value 40 tier-A có thể resolve, Thợ KHÔNG tự gộp, chờ quyết.
- **DJI fetch bị block** (JS nặng) → pool DJI gap khoá; cần Chủ thầu cào rồi Thợ wire.
- **Refinery** (`usr-refinery`, private): chờ scope token để push (việc Chủ nhà; Thợ không xử token).
- Lane gợi-ý: lô spec tiếp · làm-sắc compare/filter · mẻ nội-dung tiếp.

## 8 · Verify lại (bất-kỳ lúc nào)
```
cd portal && ./build_all.sh                                              # exit 0 = mọi cổng + teeth + headless xanh
git rev-parse --short HEAD                                               # 75a55f0b
curl -s -o /dev/null -w "%{http_code}" https://usr-portal.vercel.app/    # 200
```
Bất-biến khi sửa tiếp: không bịa số · không đè ô disputed · không copy ảnh chưa-phép vào repo public ·
figure trong bài phải recompute-khớp · giữ header byte-identical + THEME_PURITY · `build_all` xanh + secret-scan trước mỗi push.
