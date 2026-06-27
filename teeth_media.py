#!/usr/bin/env python3
"""Teeth cho verify_media — chứng cả 7 răng đều CẮN. Doctrine: cổng chưa chứng biết cắn thì chưa được tin.
Mỗi bite: deepcopy manifest sạch → tiêm đúng một lỗi loại cổng đó canh → kỳ-vọng GateError đúng tên gate."""
import copy, sys
import media_lib as ML
import verify_media as V


def _img_asset(doc):
    """một asset image rtr_owned có src thật để biến-thể (giữ src hợp-lệ, chỉ đổi đúng trường cần test)."""
    for mid, a in doc["assets"].items():
        if a.get("type") == "image" and a.get("rights") == "rtr_owned":
            return mid
    return next(iter(doc["assets"]))


def _bite(doc, want):
    try:
        V.check(doc)
        return False, "NO BITE"
    except V.GateError as e:
        return e.gate == want, e.gate


def main():
    clean = ML.load()
    ok = True
    try:
        V.check(clean); print(f"{'CLEAN (positive control)':34s} : PASS")
    except V.GateError as e:
        print(f"{'CLEAN (positive control)':34s} : !! {e}"); ok = False

    cases = []

    # 1 · RIGHTS_MISSING — rights ngoài enum
    d = copy.deepcopy(clean); d["assets"][_img_asset(d)]["rights"] = "zzz_unknown"
    cases.append(("MEDIA_RIGHTS_MISSING", d))

    # 2 · RIGHTS_BLOCKED — ảnh bên-thứ-ba renderable trong manifest
    d = copy.deepcopy(clean); d["assets"][_img_asset(d)]["rights"] = "third_party_in_article"
    cases.append(("MEDIA_RIGHTS_BLOCKED", d))

    # 3 · LICENSE_REQUIRED — wire_licensed mà token=null
    d = copy.deepcopy(clean); a = d["assets"][_img_asset(d)]
    a["rights"] = "wire_licensed"; a["credit"] = "Reuters"; a["license"] = {"token": None, "active": False, "expires": None}
    cases.append(("MEDIA_LICENSE_REQUIRED", d))

    # 4 · CREDIT_ORPHAN — wire_licensed có token+active nhưng credit=null
    d = copy.deepcopy(clean); a = d["assets"][_img_asset(d)]
    a["rights"] = "wire_licensed"; a["credit"] = None; a["license"] = {"token": "LIC-123", "active": True, "expires": "2030-01"}
    cases.append(("MEDIA_CREDIT_ORPHAN", d))

    # 5 · OWNER_MISSING — rtr_owned mà owner rỗng
    d = copy.deepcopy(clean); d["assets"][_img_asset(d)]["owner"] = ""
    cases.append(("MEDIA_OWNER_MISSING", d))

    # 6 · DANGLING_SRC — src trỏ file không tồn-tại
    d = copy.deepcopy(clean); d["assets"][_img_asset(d)]["src"] = "/images/content/none/khong-co.webp"
    cases.append(("MEDIA_DANGLING_SRC", d))

    # 7 · TAG_DANGLING — binding trỏ surface không tồn-tại
    d = copy.deepcopy(clean); d["bindings"]["entity:khong-ton-tai-xyz"] = [_img_asset(d)]
    cases.append(("MEDIA_TAG_DANGLING", d))

    # 8 · IDENTITY_UNSOURCED (Addendum A) — leadership-bound người thật mà thiếu nguồn danh-tính
    d = copy.deepcopy(clean)
    lid = next((ids[0] for k, ids in d["bindings"].items() if k.startswith("leadership:") and ids), None)
    if lid:
        d["assets"][lid].pop("identity_source", None)
        cases.append(("MEDIA_IDENTITY_UNSOURCED", d))

    for want, d in cases:
        bit, got = _bite(d, want)
        ok = ok and bit
        print(f"{want:34s} : {'CẮN ✓ (build dừng)' if bit else 'KHÔNG CẮN ✗ ['+got+']'}")

    print("-" * 60)
    print("MEDIA TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
