# X-RAY — USR Portal (rtr-news) · handover gửi Chủ thầu

> Cập-nhật sau **P3 (biên-tập) + media-staging + re-skin + sprint chiều-sâu spec + DEPLOY LIVE**.
> HEAD `0a645ac` · nhánh `main` · tree sạch · **99 commit** · **đã công-khai** tại `usr-portal.vercel.app`.
> Phát-hành: 29/06/2026. Đọc file này để tiếp việc; mọi số dưới đây tính SỐNG từ engine, không từ trí nhớ.
> Working dir: `/Users/os/RtR/rtr-news/portal`. Verify: `./build_all.sh` → "build_all: OK".

---

## 1 · Vai & giao-thức
- **Chủ thầu** ra Contract/TIP có cổng; **Thợ** thực-thi → chạy gate fail-loud → commit → push → báo cáo; Chủ thầu **VERIFY độc-lập** ("chỉ tin engine").
- Repo PUBLIC `github.com/nclamvn/usr-portal`. Build dir: `portal/`. Một lệnh: `./build_all.sh` (exit≠0 = chặn, idempotent-gated).
- Luật nhà: zero-fabrication · KHÔNG em-dash · "Real-time Robotics" t thường · secret-scan trước push · commit kết `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## 2 · Bất-biến (đứng vững P0→P3, không được phá)
- **Zero-fabrication**: mọi số hoặc recompute-sống từ registry, hoặc dẫn nguồn + tier.
- **honest-null hai chiều**: thiếu nguồn → để trống; ô trống ≠ "đã xác nhận không".
- **disputed-keep-all** (invariant #10): nguồn lệch → giữ TẤT CẢ phiên-bản + xuất-xứ, không ép một số.
- **figure-trace recompute-live**: số trong bài = giá-trị tính sống; registry đổi → gate bắt drift (`CONTENT_FIGURE_DRIFT`).
- **một-chiều E→D**: registry nuôi mọi bề-mặt; bài tham-chiếu dữ-liệu, dữ-liệu không suy từ bài.
- **provenance ảnh = sổ-license** (không phải rào): mọi ảnh hiển-thị có credit + `license_status`.

## 3 · Kiến-trúc dữ-liệu (schema/2, cell có provenance)
- **`out/master_registry.json`** (schema 1.1.0, git-tracked, build đọc chỉ-đọc): **302 variant / 291 family**. Mỗi thuộc-tính = cell:
  `{value, status(verified|derived|disputed|unverified|None), confidence, sources:[{url,tier,retrieved,claimed_value}], last_verified, inherited_from}`.
- **`out/site-data.json`**: phóng-chiếu sống (entities + aggregates) → 302 uav, 140 company.
- Tier nguồn: **A** chính-chủ · **B** thứ-cấp đối-chiếu · **C** tổng-hợp · **derived** suy nội-bộ.
- Kho khác: `content/lae-registry.json` (50 entity LAE) · `news-cards.json` (48) · `newsroom/*.md` (54) · `articles.json` (7) · `glossary.json` (5) · `media.json` (52 asset) + `out/media-ledger.json` (93 ảnh).

## 4 · Design language
- Editorial-industrial: cream/dark, serif (Source Serif 4) + mono (IBM Plex) + brass `#9B6B1C` chỉ cho ACTIVE; hairline; reg-frame góc brass.
- Width token `--w-wide 1180` / `--w-read 760` (không raw px). `data-lang` = `vn`/`en` (KHÔNG `vi`). Theme + i18n toggle khoá ở header byte-identical.
- Register "instrument/cockpit" (Monitor) đã lan sang **Compare** (bảng điều khiển khoang) + **Knowledge** (lưới card) + **Data** (showcase).

## 5 · Surfaces & pipeline (`build_all.sh`, ~40 cổng + teeth)
- **Top**: index · reference · search (→ hộp tìm trên header) · compare · data · knowledge · review · news · monitor · bundle.
- **Dir**: entity/302 · company/140 · country/28 · segment/13 · news/59 · analysis/2 · knowledge/5 · **news-card/49** (48 card + index liệt-kê).
- Builders **20** · verify **21** · teeth **21**. Headless audit (Chrome CDP): overlap=0 + THEME_PURITY mọi trang × theme × lang. Idempotent (sha khớp 2 lần).

## 6 · Đã đóng từ P2 → nay
1. **P3 biên-tập**: 13 bài gốc dày (Thợ viết, grounded) — cả hai provenance: recompute-sống (data-report registry) + sourced-fact (explainer/data-note cào nguồn). Sạch Sổ tay (0 em-dash, lead ≤40).
2. **Tin nhanh (dòng A)**: 48 card aggregation (9/9 lĩnh-vực), trang đọc in-site + trang liệt-kê, gate `verify_aggregation` (8 răng, gồm AGG_NO_EMDASH).
3. **Media-staging (TIP-NEWS-VISUAL)**: `license_status` (owned|cc|licensed|pending) + `build_media_ledger.py` → `out/media-ledger.json` (cầu sang đội license). **Hybrid**: ảnh `pending` GIỮ hotlink (không copy bản-sao chưa-phép vào repo public), chỉ ledger.
4. **Ảnh trang chủ**: 28 ảnh CC/CC0/PD distinct, **mỗi card một ảnh riêng + ĐÚNG thực-thể** (sửa lỗi Kerala-Police-gắn-Viettel → relevance-first), card không ảnh → **sinh SVG data-figure**.
5. **Re-skin**: Compare console reg-frame + rack 4 khoang + lưới card glyph; Knowledge lưới card + readout sống; **Data showcase** "Tình hình bản đăng ký UAV" + Section 06 **Phổ năng-lực** (min→max envelope).
6. **Sprint chiều-sâu spec (lô 1-6)**: **~90 ô tier-A** trên ~31 UAV (DJI/Autel/AeroVironment/Skydio/Freefly/Wingcopter/Shield AI/General Atomics/AgEagle…). Gap-fill 0 đè + skip disputed.
7. **Gate hardening**: `verify_data` thêm drift-check `spec_range`; `verify_newsroom` `CONTENT_FIGURE_DRIFT` đổi sang **khớp ranh-giới-số** (hết lọt substring "6" trong "267").
8. **DEPLOY LIVE**: Vercel `usr-portal.vercel.app`, **auto-deploy khi push `main`**, canonical khớp `seo.py BASE`.

## 7 · Số liệu hiện-trạng (snapshot, sống)
- Registry: **302 UAV · 140 hãng · 28 nước · 13 phân-khúc** · độ-phủ spec **31%**.
- Nguồn: **1.857 tier-A · 439 B · 638 C · 267 derived**. Trạng-thái ô: **2.917 verified · 6 disputed (giữ cả) · 37 unverified · 267 derived**.
- Phổ năng-lực: MTOW 0,073→25.000 kg · range 3,2→13.700 km · endurance 4→3.600 phút · trần 457→15.240 m.
- Media-ledger: **93 ảnh — 66 cc · 12 owned · 15 pending** (sổ `to_license` cho đội license).
- Nội-dung: 54 bài newsroom · 48 card · 50 entity LAE · 7 bài analysis · 5 thuật-ngữ.

## 8 · Commits gần nhất (HEAD `0a645ac`, tổng 99)
`0a645ac` data showcase (Phổ năng-lực) · `2d8ec25`..`cb0126a` registry lô 3-6 · `71e4c1a` fix gate word-boundary ·
`67e71b8` FIX phục-hồi disputed Skydio X10 · `2bf2d96` registry lô 1-2 · `d432e6c` SVG figure card · `1bf5b80`/`4d4283b`/`83cd47d` media ảnh distinct+relevance · `4bb7083`/`0c2d8cb`/`dd44d4b` newsroom mẻ2 + media stage · `763cebf`/`24d2caa` re-skin Knowledge/Compare.

## 9 · Deliverables ngoài-repo
- **`../USR-BaoCao-DuLieu-CauTruc-TieuChuan.pdf`** — báo-cáo team (4 trang: tài-nguyên/cấu-trúc/tiêu-chuẩn + snapshot). Sinh tự-động từ dữ-liệu sống. Nằm ngoài repo → không deploy.
- Manifests cào: `../registry-spec-enrich-batch{1..6}.json` (audit-trail lô spec). `../news-cards-batch*.seed.json` (seed tin).

## 10 · Mở — chờ Chủ thầu/Chủ nhà quyết
- **Skydio X10 endurance** (40 vs 65, disputed): có value 40 tier-A (skydio.com) CÓ THỂ resolve — Thợ KHÔNG tự gộp, chờ quyết.
- **DJI fetch bị block** (timeout 60s, JS nặng) → pool DJI ~40 mẫu gap đang khoá. Cần: Chủ thầu cào DJI rồi Thợ wire, hoặc tiếp đa-hãng (yield khá).
- **15 ảnh pending** (báo bên thứ ba, bài `lae-vn-*`/`lae-tg-*`) đang hiển-thị công-khai qua CDN nguồn → đội license mua phép rồi lật `pending→licensed` (`fetch_media.py` dựng đúng ca đó, chưa build vì chưa có license đầu-tiên).
- **Refinery** (`usr-refinery`, private): 4 commit chờ scope `repo` cho token để push (việc Chủ nhà, Thợ không xử token).
- Lane kế gợi-ý: lô 7 spec · làm-sắc compare/filter (nốt nhịp showcase) · mẻ nội-dung tiếp.

## 11 · Verify lại (bất-kỳ lúc nào)
```
cd portal && ./build_all.sh           # exit 0 = mọi cổng + teeth + headless audit xanh
git rev-parse --short HEAD            # 0a645ac
curl -s -o /dev/null -w "%{http_code}" https://usr-portal.vercel.app/   # 200
```

## 12 · Bất-biến tuyệt-đối khi sửa tiếp
Không bịa số · không đè ô disputed (skip status=disputed khi gap-fill) · không copy ảnh chưa-phép vào repo public ·
mọi figure trong bài phải recompute-khớp (sửa registry → re-sync prose) · giữ header byte-identical + THEME_PURITY ·
chạy `build_all` xanh + secret-scan trước mỗi push (push = auto-deploy production).
