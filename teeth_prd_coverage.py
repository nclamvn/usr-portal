#!/usr/bin/env python3
"""Teeth cho verify_prd_coverage — chứng 3 răng CẮN. Tiêm lỗi vào bản sao sổ phủ → kỳ-vọng đúng gate.
KHÔNG đụng ../prd-coverage.yaml thật; chạy gate trên doc đã chế-biến trong bộ nhớ."""
import sys, pathlib, copy
import yaml
import verify_prd_coverage as V

LEDGER = pathlib.Path(__file__).resolve().parent / "prd-coverage.yaml"


def run_on(doc):
    """Lặp lại logic gate trên doc cho sẵn → trả danh sách fail (không gọi sys.exit)."""
    fails = []
    rows = list(doc.get("entity_types", [])) + list(doc.get("acceptance", []))
    ent = {r["id"] for r in doc.get("entity_types", [])}
    acc = {r["id"] for r in doc.get("acceptance", [])}
    roles = set(doc.get("roles_required", []))
    for m in V.EXPECT_ENT - ent: fails.append("PRD_MISSING_ID:ent:" + m)
    for m in V.EXPECT_ACC - acc: fails.append("PRD_MISSING_ID:acc:" + m)
    for m in V.EXPECT_ROLES - roles: fails.append("PRD_MISSING_ID:role:" + m)
    for r in rows:
        st, proof = r.get("status"), (r.get("gate_proof") or "").strip()
        if st not in V.VALID_STATUS: fails.append("PRD_BAD_STATUS:" + str(r.get("id"))); continue
        if st == "done":
            if not proof: fails.append("PRD_DONE_NO_PROOF:" + str(r.get("id")))
            elif not (V.ROOT / (proof + ".py")).exists(): fails.append("PRD_PROOF_GHOST:" + str(r.get("id")))
    return fails


def main():
    base = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
    ok = True

    def case(name, doc, want):
        nonlocal ok
        fails = run_on(doc)
        bit = any(f.startswith(want) for f in fails) if want else not fails
        ok = ok and bit
        tag = "PASS" if (want is None and not fails) else ("CẮN ✓" if bit else "KHÔNG CẮN ✗ " + str(fails[:1]))
        print(f"{name:24s} : {tag}")

    case("CLEAN", base, None)

    # (a) done suông — gỡ gate_proof của một mục done
    d = copy.deepcopy(base)
    for r in d["acceptance"]:
        if r["status"] == "done": r["gate_proof"] = ""; break
    case("PRD_DONE_NO_PROOF", d, "PRD_DONE_NO_PROOF")

    # (b) thiếu mục — xoá một tiêu chí §8
    d = copy.deepcopy(base); d["acceptance"] = d["acceptance"][:-1]
    case("PRD_MISSING_ID (acc)", d, "PRD_MISSING_ID")

    # (c) thiếu entity type — xoá một entity
    d = copy.deepcopy(base); d["entity_types"] = d["entity_types"][:-1]
    case("PRD_MISSING_ID (ent)", d, "PRD_MISSING_ID")

    # (d) proof ma — done trỏ verify không tồn tại
    d = copy.deepcopy(base)
    for r in d["acceptance"]:
        if r["status"] == "done": r["gate_proof"] = "verify_khong_co_that"; break
    case("PRD_PROOF_GHOST", d, "PRD_PROOF_GHOST")

    # (e) status lạ
    d = copy.deepcopy(base); d["acceptance"][0]["status"] = "almost"
    case("PRD_BAD_STATUS", d, "PRD_BAD_STATUS")

    print("-" * 52)
    print("PRD-COVERAGE TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
