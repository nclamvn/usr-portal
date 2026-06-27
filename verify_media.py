#!/usr/bin/env python3
"""verify_media.py — TIP-MEDIA-UPGRADE Task 3 (gate, fail-loud exit 2).

Cổng quyền-media tự-động. Manifest content/media.json PHẢI sạch tuyệt-đối: mỗi asset khai đúng
quyền, đúng sở-hữu, src thật, license đủ khi wire; mỗi binding trỏ surface THẬT. Vi-phạm → exit 2.

Bảy răng (Contract §4):
  MEDIA_RIGHTS_MISSING   rights ngoài enum §2 (mặc-định không-phân-loại = chặn)
  MEDIA_RIGHTS_BLOCKED   third_party_in_article có mặt renderable, hoặc wire_licensed active=false (token đã điền)
  MEDIA_LICENSE_REQUIRED wire_licensed mà token=null hoặc đã expires
  MEDIA_CREDIT_ORPHAN    wire_licensed mà credit=null (mua quyền thì phải biết credit ai)
  MEDIA_OWNER_MISSING    rtr_owned / rtr_distributed mà owner rỗng (buộc khẳng-định sở-hữu)
  MEDIA_DANGLING_SRC     src (image/video) trỏ file không tồn-tại trong portal/
  MEDIA_TAG_DANGLING     binding trỏ surface (hoặc asset-id) không tồn-tại trong graph/disk

Bất-biến phụ: idempotent metadata (media.json sort-stable, byte-identical hai lần đọc-ghi);
site-null hai chiều do render-layer + auditor canh (Task 4/§8.4).
"""
import json, sys
from pathlib import Path
import media_lib as ML

ROOT = Path(__file__).resolve().parent


class GateError(Exception):
    def __init__(self, gate, msg):
        self.gate = gate
        super().__init__(f"{gate}: {msg}")


def _src_path(src):
    return ROOT / src.lstrip("/")


def _binding_target_exists(key):
    """Surface thật trên disk cho một binding key '<kind>:<id>'."""
    if ":" not in key:
        return False
    kind, ident = key.split(":", 1)
    if kind == "hero":
        return (ROOT / "index.html").exists()           # hero sống trên trang chủ
    if kind == "company":
        return (ROOT / "company" / f"{ident}.html").exists()
    if kind == "entity":
        return (ROOT / "entity" / f"{ident}.html").exists()
    if kind == "person":
        return (ROOT / "person" / f"{ident}.html").exists()
    if kind == "article":
        return (ROOT / "news" / f"{ident}.html").exists() or (ROOT / "analysis" / f"{ident}.html").exists()
    return False                                          # kind lạ → coi như dangling


def check(doc):
    assets = doc.get("assets", {})
    bindings = doc.get("bindings", {})

    for mid, a in assets.items():
        tag = f"asset {mid!r}"
        r = a.get("rights")
        if r not in ML.ENUM:
            raise GateError("MEDIA_RIGHTS_MISSING", f"{tag}: rights {r!r} ngoài enum §2")

        if r == "third_party_in_article":
            raise GateError("MEDIA_RIGHTS_BLOCKED",
                f"{tag}: ảnh bên-thứ-ba-trong-bài không được nằm renderable trong manifest (share link thay vì đăng-lại-ảnh)")

        if r in ("rtr_owned", "rtr_distributed") and not a.get("owner"):
            raise GateError("MEDIA_OWNER_MISSING", f"{tag}: rights={r} mà owner rỗng — buộc khẳng-định sở-hữu")

        if r == "wire_licensed":
            lic = a.get("license") or {}
            if not lic.get("token") or lic.get("expires") == "EXPIRED":
                raise GateError("MEDIA_LICENSE_REQUIRED", f"{tag}: wire_licensed mà token=null/đã hết-hạn — chặn render")
            if a.get("credit") in (None, ""):
                raise GateError("MEDIA_CREDIT_ORPHAN", f"{tag}: wire_licensed mà credit=null — phải biết credit ai")
            if lic.get("active") is not True:
                raise GateError("MEDIA_RIGHTS_BLOCKED", f"{tag}: wire_licensed có token nhưng active=false — slot off")

        typ = a.get("type")
        if typ in ("image", "video"):
            src = a.get("src", "")
            if not src or not _src_path(src).exists():
                raise GateError("MEDIA_DANGLING_SRC", f"{tag}: src {src!r} không tồn-tại trong portal/")
        elif typ == "link":
            if not a.get("source_url") or not a.get("quote"):
                raise GateError("MEDIA_DANGLING_SRC", f"{tag}: type=link thiếu source_url/quote")

    # bindings: target surface + asset-id phải thật
    for key, ids in bindings.items():
        if not _binding_target_exists(key):
            raise GateError("MEDIA_TAG_DANGLING", f"binding {key!r}: surface không tồn-tại trong graph/disk")
        for mid in ids:
            if mid not in assets:
                raise GateError("MEDIA_TAG_DANGLING", f"binding {key!r}: asset-id {mid!r} không có trong assets")


def main():
    doc = ML.load()
    n = len(doc.get("assets", {}))
    try:
        check(doc)
    except GateError as e:
        print(f"\nMEDIA FAIL:\n  - {e}")
        sys.exit(2)
    # idempotent metadata: re-serialize sort-stable phải khớp file trên disk
    canon = json.dumps({"schema": doc.get("schema", "media/1"),
                        "assets": {k: doc["assets"][k] for k in sorted(doc["assets"])},
                        "bindings": {k: doc["bindings"][k] for k in sorted(doc["bindings"])}},
                       ensure_ascii=False, indent=2) + "\n"
    on_disk = (ROOT / "content" / "media.json").read_text(encoding="utf-8")
    if canon != on_disk:
        print("\nMEDIA FAIL:\n  - MEDIA_METADATA_UNSORTED: media.json không ở dạng canonical sort-stable (chạy optimize_media.py để chuẩn-hoá)")
        sys.exit(2)
    print(f"MEDIA PASS: {n} asset · enum-quyền hợp-lệ · owner/license/src/binding thật · metadata canonical.")


if __name__ == "__main__":
    main()
