# X-RAY — USR Portal (rtr-news) · handover, cập-nhật sau **P2 (đóng đủ)**

> Mục-đích: phiên Chủ thầu/Thợ mới đọc file này là tiếp được liền (P3 Editorial), không dò lại cả chuỗi.
> Working dir: `/Users/os/RtR/rtr-news/portal`. Tất cả lệnh chạy từ đây. Verify: `./build_all.sh` → "build_all: OK".

## 1 · Vai & giao-thức
- **Chủ thầu** (người) ra design-language/spec (Contract + TIP) + VERIFY engine-checked. **Thợ** (agent ở env có data) wire vào pipeline, trả Completion Report. Có lúc Chủ thầu ủy Thợ author TIP ("proceed per proposal") — gate độc-lập + VERIFY vẫn là hai nhân-chứng.
- Kỷ-luật: **only-trust-engine** (xác bằng chạy code, không bằng lời; khung-xem-ảnh không trả hình thì xác bằng DOM/đếm, KHÔNG tự-nhận đã thấy pixel) · **conflict → REPORT, không tự-quyết** · một-TIP-một-đợt, gates xanh mới qua đợt sau · **no-pipe khi đọc exit code** · cwd persist giữa Bash call (dùng `cd` tuyệt-đối).

## 2 · Bất-biến (non-negotiable, đứng vững P0→P2)
- **Zero-fabrication**: chỉ render giá-trị thật; unverified/absent → null; KHÔNG bịa số/rotor/bài/từ-khoá. Kéo vào tận **JSON-LD** (search engine chỉ thấy số có nguồn).
- **Honest-null hai-chiều**: null → "—"/dashed/pip-rỗng/bucket-riêng ở mọi mặt; site-null ⇔ render-null (auditor canh hai chiều). honest-null là showpiece, KHÔNG giấu.
- **Bất-biến #10 — disputed giữ TẤT CẢ claim**, không lặng-lẽ chọn (vd Switchblade-300 mtow). Áp mọi type + cả company sourced + giữ NGOÀI structured data.
- **Provenance là sản-phẩm**: mọi số truy URL nguồn + tier A/B/C. company sourced field = `{value,source,tier}` | `{disputed:[…]}` | honest-null; cấm value-trần-không-nguồn.
- **Aggregate/phân-bố/index tính SỐNG** mỗi build (GLOBAL CONSTRAINT). **Một-nguồn-sự-thật** = `out/site-data.json`; mọi data-file phụ là **chiếu sống** của nó, KHÔNG nguồn thứ-hai (auditor *_DRIFT canh).
- **E → D một chiều**: biên-tập tham-chiếu dữ-liệu; dữ-liệu KHÔNG BAO GIỜ phái-sinh từ claim bài viết.
- **Gates + teeth fail-loud · idempotent** (mọi data-file build 2 lần = byte-identical, có gate).

## 3 · Kiến-trúc dữ-liệu (schema/2 đa-thực-thể, một chiều)
`wave2b/code/.../master_registry.json` (302 UAV, nguồn registry — seeds NGOÀI repo portal) → `build_site_data.py` →
**`out/site-data.json`** (`schema:"site-data/2"`, **một-nguồn-sự-thật**):
- `entities[]` = **302 uav + 140 company** (discriminator `entity_type`). Company **derived-first**: promote từ manufacturer, rollup SỐNG (uav_count/country/segment mix/Blue/NDAA) + sourced-attrs (4/140 có nguồn, còn lại honest-null).
- `canon.py` = single-source **alias-map** (Anduril←Anduril Industries; IAI←Israel Aerospace Industries; Boeing/Insitu KHÔNG gộp) + **country normalize** EN ({US,USA}→United States; {UK,United Kingdom}→United Kingdom).
- aggregates UAV-scoped (headline "302" bất-biến). `frame_glyph` derived. `company_slug`/re-point qua canon.

Các data-file phụ (đều chiếu sống, sorted+idempotent, có auditor riêng):
`out/graph.json` (494 node/882 edge) · `out/search-index.json` (483) · `out/compare-data.json` (302) · `out/data-overview.json` · `sitemap.xml` (494 url).

## 4 · Design language
- `base/portal-in-action.html` = design-system-of-record (app shell). `base/newsroom-specimen.html` = News/Analysis idiom.
- Token canonical `base/design-system.css`; alias `--serif/--sans/--mono/--card/--wm/--maxw`. `.tg`(facet=`[aria-pressed]`); `.ghost` chỉ dark; cream-figure=`.statfig`; `.crumb` = global nav.
- **`nav.py`** = breadcrumb dùng chung MỌI trang: **USR · Reference · Search · Compare · Data** (USR→home), depth-aware (`../`). Hết ngõ-cụt.
- Component-CSS đặt trong từng builder (DETAIL_CSS/COMPANY_CSS/TAX_CSS/COMPARE_CSS/SEARCH_CSS/DATA_CSS). **Class collision cảnh-báo**: `.spec`/`.rail` từng đụng newsroom — đã rename `.smpl`/`.trk`; build_bundle có teeth chặn tái-diễn.

## 5 · Surfaces & pipeline (`build_all.sh` — fail-loud, idempotent-gated)
**Surfaces** (phục-vụ `python3 -m http.server 8011 --bind 127.0.0.1`):
`index` · `reference` · `search` · `compare` · `data` · `bundle` (một-file offline) · `entity/`×302 · `company/`×140 · `country/`×28 · `segment/`×13 · `news/`×5 · `analysis/`×1 · `sitemap.xml`.
**Builder**: build_site_data · build_reference · build_detail · build_company · build_taxonomy · build_news · build_analysis · build_index · build_compare · build_search · build_data · build_sitemap · build_bundle.
**Auditor độc-lập + teeth** (mỗi cái tự-bơm-restore, fail-loud exit 2):
verify_site_data (honest-null 2 chiều · #10 · company rollup-two-way/sourced-shape · ALIAS_ORPHAN · frame_glyph no-leak · spec_range live · `teeth_p0`+`teeth_p11`) · verify_graph (DANGLING/STALE · `teeth_p02`) · verify_taxonomy (bijection · `teeth_p14`) · verify_compare (DRIFT · `teeth_p13`) · verify_search (DRIFT/ORPHAN/MISSING · `teeth_p21`) · verify_data (OVERVIEW_DRIFT/SUM + honest-null 2 chiều · `teeth_p23`) · verify_seo (SEO_FABRICATED + sitemap bijection · `teeth_p22`) · verify_content · check_i18n (en==vn) · audit_headless.js (Chrome CDP, overlap=0 mọi surface + perf + teeth).

## 6 · Phase đã đóng
- **P0 Móng** (`f315765` P0.1 · `b947ac8` P0.2): schema/1→/2 đa-thực-thể + discriminator (render byte-bất-biến, teeth chứng) · bất-biến #10 · `crosslink.py` graph + dangling-gate.
- **P1 Khung D** (đóng đủ): P1.1 Company derived-first 140 (`e858988`) · P1.2 sourced loader + alias + country-normalize + **4 golden record** DJI/Autel/AeroVironment/RtR (`61cc787`/`00a3f15`/`abcc3b3`) · P1.4 Taxonomy 28+13 bijection (`63dddf2`) · P1.3 Compare 2–4 (`c591905`).
- **P2 Lưu-thông** (đóng đủ): P2.1 Search đa-loại 483 (`d1ad2a1`) · P2.3 Data overview /data live (`f3c4f56`) · P2.2 SEO/JSON-LD/sitemap (`57035f2`).
- **UX polish**: header reference (bỏ raw "None"→honest-null) · global nav breadcrumb (`a331a45`) · Compare gợi-ý-khi-mở (`e6a2209`).
- *(Lịch-sử P01–P04 visual staging + data-growth 200→302 nằm trong commit cũ; vẫn còn hiệu-lực: glyph map D-1, micro-track log D-2, coverage matrix, rows=light-index/track=DETAIL.)*

## 7 · Commits (nhánh `main`, tree sạch — **HEAD `57035f2`, tổng 35 commit**)
P0→P2 (mới→cũ): `57035f2`(P2.2) · `f3c4f56`(P2.3) · `e6a2209`(compare-gợi-ý) · `a331a45`(nav) · `6a5c53c`(reference-header) · `d1ad2a1`(P2.1) · `c591905`(P1.3) · `63dddf2`(P1.4) · `abcc3b3`+`00a3f15`+`61cc787`(P1.2) · `e858988`(P1.1) · `b947ac8`(P0.2) · `f315765`(P0.1). Trước đó: data-growth 200→302 + visual P01–P04 (xem `git log`).

## 8 · Deliverables @ `portal/`
- **Web** (15 loại surface, xem §5) + `sitemap.xml`. **Gửi đội**: `bundle.html` (offline 302) · `uav-300.xlsx`.
- **Data-file sống** (out/): site-data · graph · search-index · compare-data · data-overview (+ sitemap.xml ở root).
- **Code**: ~13 `build_*` · ~10 `verify_*`/`teeth_*` · `canon.py`/`nav.py`/`seo.py`/`glyphs.py` · `base/` (css/js: base/compare/search) · `content/` (companies.json + company_aliases.json = golden record; articles.json/glossary.json = editorial sample).

## 9 · Nội-dung biên-tập & P3 (chế-độ E — phase kế)
News/Analysis hiện = **vỏ + 1 analysis + 5 news seed** (`sample:true` → banner mẫu; figure THẬT từ registry, văn xuôi mẫu). **P3 Editorial** dựng được *vỏ* (template News/Knowledge/Review + linter Quy-tắc biên-tập + auditor) nhưng **bài thật do người viết** — Chủ nhà/đội là nguồn. **Nút thắt KHÔNG kỹ-thuật**: cần **kế-hoạch content** (bao nhiêu bài, ai viết, chủ-đề) trước khi mở P3. KHÔNG bịa nội-dung để "đủ trang". Xem [[newsroom-pillar]] [[blueprint-usr]].

## 10 · Push & domain (việc Chủ nhà)
- **CHƯA push** (no upstream). 35 commit local. Đẩy: cần PAT (Thợ không cầm token):
  `git push -u https://PAT@github.com/nclamvn/usr-portal.git main`
- **`seo.py BASE = "https://nclamvn.github.io/usr-portal"`** = đoán (Pages mặc-định; KHÔNG có CNAME). Chủ nhà sở-hữu `rtrobotics.com` → có thể muốn custom domain (vd `usr.rtrobotics.com`). Trước khi public: xác-nhận domain → đổi `BASE` + thêm `CNAME` (1 commit). Gate độc-lập domain nên không chặn build.

## 11 · Mở (chờ Chủ thầu/Chủ nhà)
- Nét/độ-đậm trên cream+dark = **mắt Chủ thầu** (engine chỉ xác cấu-trúc/overlap). · Push + BASE domain (§10). · Kế-hoạch content P3 (§9). · Sourcing batch hãng (General Atomics/Baykar/IAI/CASC/HESA + mẩu RtR còn) → nạp `content/companies.json` commit nhỏ.

## 12 · Verify lại (bất-kỳ lúc nào)
`cd portal && ./build_all.sh` → exit 0 + "build_all: OK" (mọi gate + teeth + idempotent + headless overlap=0). Teeth có thật, vd: sửa một cột `out/data-overview.json` → `verify_data.py` exit 2; tamper JSON-LD value → `verify_seo.py` exit 2; khôi-phục bằng chạy lại builder.

## 13 · Bất-biến tuyệt-đối khi sửa tiếp
KHÔNG bịa (kể cả JSON-LD/từ-khoá) · KHÔNG hardcode aggregate/phân-bố/min-max/coverage/index · KHÔNG đẻ nguồn-dữ-liệu thứ-hai (mọi data-file chiếu site-data) · KHÔNG đổi dataset ở lớp trình-bày · KHÔNG redefine token canonical / token mới · KHÔNG tự gộp cụm country/company mơ-hồ (FLAG → Chủ thầu rule) · giữ static-gen + gates + teeth + idempotent + nav-mọi-trang · conflict với quyết-định cũ (index≠detail · E→D · derived-first · honest-null-visible) → REPORT, không tự-quyết. Xem [[portal-design-ethos]] [[blueprint-usr]].
