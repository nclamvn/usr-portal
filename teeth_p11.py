#!/usr/bin/env python3
"""TIP-P1.1 teeth — prove verify_site_data bites on company violations. Mutates ONLY temp copies;
out/site-data.json is never touched. Exit 0 only if each tooth bites (exit 2, right message) and
the clean file passes."""
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


def first_company(obj):
    for e in obj["entities"]:
        if e.get("entity_type") == "company":
            return e
    return None


base = json.load(open(SITE))
results = []

# (a) company sourced attr as a BARE value (no source/tier) -> SOURCED_ATTR -> exit 2
a = copy.deepcopy(base)
first_company(a)["hq_city"] = {"value": "Shenzhen"}            # bare value, no source/tier
rc, out = run(a); results.append(("a · bare sourced value", rc == 2 and "SOURCED_ATTR" in out, rc))

# (b) rollup uav_count wrong -> ROLLUP -> exit 2
b = copy.deepcopy(base)
first_company(b)["rollup"]["uav_count"] = 9999
rc, out = run(b); results.append(("b · rollup count mismatch", rc == 2 and "ROLLUP" in out, rc))

# (c) company disputed attr collapsed to one claim -> DISPUTED_CLAIM_DROP -> exit 2 (#10 on company)
c = copy.deepcopy(base)
first_company(c)["hq_address"] = {"disputed": [{"value": "A St", "source": "x", "tier": "B"}]}
rc, out = run(c); results.append(("c · company disputed drop", rc == 2 and "DISPUTED_CLAIM_DROP" in out, rc))

# restore — the unmutated file must still PASS
rc, out = run(base); results.append(("restore · clean file passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for name, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {name}  (auditor exit {rc})")
print("TEETH-P1.1:", "PASS — company auditor has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
