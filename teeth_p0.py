#!/usr/bin/env python3
"""TIP-P0.1 teeth — prove verify_site_data bites on schema/2 violations.
Mutates ONLY in-memory copies written to temp files; out/site-data.json is never touched.
Exit 0 only if all three teeth bite (auditor exit 2 with the right message) AND the clean
file still passes (exit 0). Idempotent — safe to run every build."""
import json, subprocess, sys, tempfile, os, copy, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
MASTER = ROOT / "out" / "master_registry.json"
SITE = ROOT / "out" / "site-data.json"

def run(site_obj):
    fd, path = tempfile.mkstemp(suffix=".json", dir="/tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(site_obj, f, ensure_ascii=False)
    r = subprocess.run([sys.executable, str(ROOT / "verify_site_data.py"), str(MASTER), path],
                       capture_output=True, text=True)
    os.unlink(path)
    return r.returncode, r.stdout + r.stderr

base = json.load(open(SITE))
results = []

# (a) unknown entity_type -> ENTITY_TYPE (+ uav count drops) -> exit 2
a = copy.deepcopy(base)
a["entities"][0] = dict(a["entities"][0]); a["entities"][0]["entity_type"] = "alien"
rc, out = run(a); results.append(("a · unknown entity_type", rc == 2 and "ENTITY_TYPE" in out, rc))

# (b) company entity missing a required field (name) -> COMPANY_REQUIRED -> exit 2
b = copy.deepcopy(base)
b["entities"].append({"entity_type": "company", "slug": "acme-uav"})  # no name
rc, out = run(b); results.append(("b · company missing name", rc == 2 and "COMPANY_REQUIRED" in out, rc))

# (c) disputed cell collapsed to a single claim -> DISPUTED_CLAIM_DROP -> exit 2 (invariant #10)
c = copy.deepcopy(base); hit = False
for e in c["entities"]:
    for k, v in e.items():
        if isinstance(v, dict) and (v.get("disputed") or v.get("status") == "disputed") \
                and len(v.get("claims") or []) >= 2:
            v["claims"] = v["claims"][:1]; hit = True; break
    if hit:
        break
if not hit:
    print("TEETH (c) SETUP FAIL: no disputed cell with >=2 claims in site-data"); sys.exit(3)
rc, out = run(c); results.append(("c · disputed claim drop", rc == 2 and "DISPUTED_CLAIM_DROP" in out, rc))

# restore — the unmutated file must still PASS (exit 0)
rc, out = run(base); results.append(("restore · clean file passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for name, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {name}  (auditor exit {rc})")
print("TEETH-P0.1:", "PASS — auditor has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
