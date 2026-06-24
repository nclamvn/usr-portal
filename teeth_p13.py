#!/usr/bin/env python3
"""TIP-P1.3 teeth — prove verify_compare bites. Mutates temp copies of compare-data.json; the real
file is never touched."""
import json, subprocess, sys, tempfile, os, copy, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "out" / "compare-data.json"


def run(obj):
    fd, p = tempfile.mkstemp(suffix=".json", dir="/tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, ensure_ascii=False)
    r = subprocess.run([sys.executable, str(ROOT / "verify_compare.py"), p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode, r.stdout + r.stderr


base = json.loads(DATA.read_bytes())
results = []

# (a) tamper a real spec value -> COMPARE_DRIFT
a = copy.deepcopy(base)
for u in a["uavs"]:
    for k, c in u["specs"].items():
        if c.get("v") is not None:
            c["v"] = c["v"] + 999; break
    else:
        continue
    break
rc, out = run(a); results.append(("a · tampered spec value", rc == 2 and "COMPARE_DRIFT" in out, rc))

# (b) swallow a real value to null -> honest-null two-way mismatch
b = copy.deepcopy(base)
for u in b["uavs"]:
    for k, c in u["specs"].items():
        if c.get("v") is not None:
            c["v"] = None; break
    else:
        continue
    break
rc, out = run(b); results.append(("b · swallowed value to null", rc == 2 and "HONEST-NULL" in out, rc))

# (c) hardcode/stale spec_range -> COMPARE_DRIFT
c = copy.deepcopy(base)
k0 = list(c["spec_range"].keys())[0]
c["spec_range"][k0] = {"min": 0.001, "max": 999999}
rc, out = run(c); results.append(("c · hardcoded spec_range", rc == 2 and "COMPARE_DRIFT" in out, rc))

rc, out = run(base); results.append(("restore · real data passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P1.3:", "PASS — compare gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
