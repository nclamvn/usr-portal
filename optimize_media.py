#!/usr/bin/env python3
"""optimize_media.py — TIP-MEDIA-UPGRADE Task 2.

Lệnh CHẠY TAY (ngoài build_all.sh). Một ảnh nguồn từ rtr-website vào → một webp đã-grade ra
trong portal/images/content/<bucket>/<id>.webp → một entry ghi/cập-nhật vào content/media.json.

Chốt kiến-trúc (đã duyệt):
  - grade `rtr-warm-v1`: full-color, ấm, hằng-số khoá cứng, BAKED tại optimize-time (build KHÔNG grade lại).
  - commit artifact: webp đã grade được commit; build không re-encode → idempotency áp lên media.json metadata,
    KHÔNG lên webp blob (webp encoder không tất-định).
  - một-nguồn: rtr-website/{content,STUDIO,public} là GỐC; portal/images/content là CHIẾU. source_origin truy về gốc.

Dùng:
  python3 optimize_media.py <source> --id <media_id> --bucket hera --rights rtr_owned \
        --owner RtR --type image --tags rtr,hera --caption "..." [--captured 2026-04] \
        [--source-label "RtR Media · ..."] [--bind entity:hera]
  python3 optimize_media.py <source.mp4> --id <id> --bucket video --type video --rights rtr_owned --owner RtR ...
"""
import argparse, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent                 # portal/
WEBSITE = Path("/Users/os/RtR/rtr-website")            # kho gốc
MEDIA_JSON = ROOT / "content" / "media.json"
OUT_BASE = ROOT / "images" / "content"                 # chiếu web-optimize

GRADE = "rtr-warm-v1"                                   # bump tên nếu đổi constants — KHÔNG sửa lặng-lẽ


def rtr_warm_v1(im):
    """Grade ấm full-color, hằng-số cố-định → cùng input ra cùng output (tái lập được)."""
    from PIL import Image, ImageEnhance, ImageOps
    im = im.convert("RGB")
    im = ImageOps.exif_transpose(im)                   # tôn trọng orientation gốc
    im.thumbnail((1920, 1920), Image.LANCZOS)          # cạnh dài tối đa 1920
    r, g, b = im.split()                               # warm shift nhẹ
    r = r.point(lambda v: min(255, int(v * 1.03)))
    b = b.point(lambda v: int(v * 0.98))
    im = Image.merge("RGB", (r, g, b))
    im = ImageEnhance.Color(im).enhance(1.06)          # saturation +6%
    im = ImageEnhance.Contrast(im).enhance(1.05)       # contrast  +5%
    im = ImageEnhance.Brightness(im).enhance(1.01)     # bright    +1%
    return im


def load_media():
    if MEDIA_JSON.exists():
        return json.loads(MEDIA_JSON.read_text(encoding="utf-8"))
    return {"schema": "media/1", "assets": {}, "bindings": {}}


def write_media(doc):
    # ordering ổn-định → idempotent metadata (Task 3 canh byte-identical)
    doc["assets"] = {k: doc["assets"][k] for k in sorted(doc["assets"])}
    doc["bindings"] = {k: doc["bindings"][k] for k in sorted(doc["bindings"])}
    MEDIA_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
                          encoding="utf-8")


def resolve_src(source):
    p = Path(source)
    if p.is_absolute():
        return p
    cand = WEBSITE / source
    return cand if cand.exists() else p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="đường-dẫn ảnh/video nguồn (tương-đối rtr-website hoặc tuyệt-đối)")
    ap.add_argument("--id", required=True)
    ap.add_argument("--bucket", default="misc")
    ap.add_argument("--type", default="image", choices=["image", "video"])
    ap.add_argument("--rights", required=True)
    ap.add_argument("--owner", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--caption", default=None)
    ap.add_argument("--captured", default=None)
    ap.add_argument("--source-label", dest="source_label", default=None)
    ap.add_argument("--credit", default=None)
    ap.add_argument("--grade", default=GRADE)               # 'none' = trung-tính (open_licensed, không warm-grade RtR)
    ap.add_argument("--open-license", dest="open_license", default=None)  # vd 'CC BY-SA 4.0' / 'Unsplash License'
    ap.add_argument("--bind", action="append", default=[])
    a = ap.parse_args()

    src = resolve_src(a.source)
    if not src.exists():
        sys.exit(f"optimize_media: source không tồn-tại: {src}")

    ext = "webp" if a.type == "image" else src.suffix.lstrip(".").lower()
    rel = f"/images/content/{a.bucket}/{a.id}.{ext}"
    out = OUT_BASE / a.bucket / f"{a.id}.{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)

    if a.type == "image":
        from PIL import Image, ImageOps
        src_im = Image.open(src)
        if a.grade == "none":                          # open_licensed: chỉ resize+webp, không grade thương-hiệu
            im = src_im.convert("RGB"); im = ImageOps.exif_transpose(im); im.thumbnail((1920, 1920), Image.LANCZOS)
        else:
            im = rtr_warm_v1(src_im)
        im.save(out, "WEBP", quality=82, method=6)     # strip metadata mặc-định
        grade = a.grade
        before = src.stat().st_size
        after = out.stat().st_size
        print(f"  optimized {src.name} → {rel}  ({before//1024}K → {after//1024}K, grade={grade})")
    else:                                               # video: copy nguyên, KHÔNG grade
        shutil.copyfile(src, out)
        grade = None
        print(f"  copied {src.name} → {rel}  (video, grade=null)")

    try:
        origin = str(src.relative_to(WEBSITE))
    except ValueError:
        origin = str(src)

    doc = load_media()
    asset = {
        "type": a.type,
        "src": rel,
        "rights": a.rights,
        "owner": a.owner or None,
        "source": a.source_label or f"RtR Media · {origin}",
        "source_origin": f"rtr-website/{origin}",
        "credit": a.credit,
        "open_license": a.open_license,
        "license": {"token": None, "active": False, "expires": None},
        "grade": grade,
        "caption": a.caption,
        "captured_at": a.captured,
        "entity_tags": [t for t in a.tags.split(",") if t],
    }
    doc["assets"][a.id] = asset
    for key in a.bind:
        lst = doc["bindings"].setdefault(key, [])
        if a.id not in lst:
            lst.append(a.id)
    write_media(doc)
    print(f"  media.json ← asset {a.id!r}" + (f" · bind {a.bind}" if a.bind else ""))


if __name__ == "__main__":
    main()
