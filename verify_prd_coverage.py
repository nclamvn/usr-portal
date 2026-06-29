#!/usr/bin/env python3
"""CONTRACT-CMS §9 / TIP-CMS-01 Task 7 — cổng phủ PRD, chống bỏ-sót + chống khai-done-suông.
Đọc ../prd-coverage.yaml (sổ phủ do Chủ thầu maintain) và CƯỠNG CHẾ:
  · PRD_MISSING_ID   — thiếu bất kỳ id PRD chuẩn nào (10 entity type · 35 §8 · 8 vai trò) → exit 2.
  · PRD_DONE_NO_PROOF— status: done mà gate_proof rỗng → exit 2 (không khai done suông).
  · PRD_PROOF_GHOST  — gate_proof của một 'done' trỏ verify_*.py KHÔNG tồn tại → exit 2.
  · PRD_BAD_STATUS   — status ∉ {done, partial, missing}.
Fail-loud exit 2. KHÔNG đỏ trên partial/missing (đó là việc thật còn lại, khai trung thực).
"""
import sys, pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent
LEDGER = ROOT / "prd-coverage.yaml"   # single source, in-repo (committed + reproducible trên fresh checkout)

EXPECT_ENT = {"ENT.uav", "ENT.company", "ENT.software", "ENT.camera", "ENT.sensor",
              "ENT.battery", "ENT.motor", "ENT.payload", "ENT.accessory", "ENT.distributor"}
EXPECT_ACC = {  # §8 — 35 tiêu chí nghiệm thu (spec of record; thiếu một là bỏ sót PRD)
    "8.1.1", "8.1.2", "8.1.3", "8.1.4", "8.1.5", "8.2.1", "8.2.2", "8.2.3", "8.2.4",
    "8.3.1", "8.3.2", "8.3.3", "8.4.1", "8.4.2", "8.4.3", "8.5.1", "8.5.2", "8.5.3",
    "8.6.1", "8.6.2", "8.7.1", "8.7.2", "8.7.3", "8.8.1", "8.8.2", "8.9.1", "8.9.2",
    "8.10.1", "8.10.2", "8.10.3", "8.10.4", "8.11.1", "8.12.1", "8.12.2", "8.12.3"}
EXPECT_ROLES = {"super_admin", "managing_editor", "editor", "contributor",
                "data_editor", "reviewer", "seo_manager", "guest_author"}
VALID_STATUS = {"done", "partial", "missing"}


def main():
    if not LEDGER.exists():
        print("\nPRD COVERAGE FAIL:\n  - PRD_LEDGER_MISSING: %s không tồn tại" % LEDGER); sys.exit(2)
    doc = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
    fails = []
    rows = list(doc.get("entity_types", [])) + list(doc.get("acceptance", []))

    ent_ids = {r["id"] for r in doc.get("entity_types", [])}
    acc_ids = {r["id"] for r in doc.get("acceptance", [])}
    roles = set(doc.get("roles_required", []))
    for miss in sorted(EXPECT_ENT - ent_ids):
        fails.append("PRD_MISSING_ID: entity type %s không có trong sổ phủ" % miss)
    for miss in sorted(EXPECT_ACC - acc_ids):
        fails.append("PRD_MISSING_ID: tiêu chí §%s không có trong sổ phủ" % miss)
    for miss in sorted(EXPECT_ROLES - roles):
        fails.append("PRD_MISSING_ID: vai trò %s không có trong roles_required" % miss)

    for r in rows:
        rid, st, proof = r.get("id"), r.get("status"), (r.get("gate_proof") or "").strip()
        if st not in VALID_STATUS:
            fails.append("PRD_BAD_STATUS: %s status=%r ∉ done/partial/missing" % (rid, st)); continue
        if st == "done":
            if not proof:
                fails.append("PRD_DONE_NO_PROOF: %s khai done nhưng gate_proof rỗng" % rid)
            elif not (ROOT / (proof + ".py")).exists():
                fails.append("PRD_PROOF_GHOST: %s done · gate_proof %r trỏ %s.py không tồn tại" % (rid, proof, proof))

    from collections import Counter
    c = Counter(r.get("status") for r in rows)
    print("prd-coverage: %d entity + %d acceptance · done %d · partial %d · missing %d · roles %d/8"
          % (len(ent_ids), len(acc_ids), c["done"], c["partial"], c["missing"], len(roles & EXPECT_ROLES)))
    if fails:
        print("\nPRD COVERAGE FAIL (%d):" % len(fails))
        for f in fails[:30]:
            print("  -", f)
        sys.exit(2)
    print("PRD COVERAGE PASS: đủ 10 entity + 35 §8 + 8 vai trò · 0 done-suông · proof trỏ gate thật.")


if __name__ == "__main__":
    main()
