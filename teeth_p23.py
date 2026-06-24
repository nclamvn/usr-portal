#!/usr/bin/env python3
"""TIP-P2.3 teeth — prove verify_data bites. Mutates temp copies of data-overview.json; real file untouched."""
import json, subprocess, sys, tempfile, os, copy, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
OV = ROOT / "out" / "data-overview.json"


def run(obj):
    fd, p = tempfile.mkstemp(suffix=".json", dir="/tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, ensure_ascii=False)
    r = subprocess.run([sys.executable, str(ROOT / "verify_data.py"), p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode, r.stdout + r.stderr


base = json.loads(OV.read_bytes())
results = []

# (a) tamper a country bucket value -> OVERVIEW_DRIFT
a = copy.deepcopy(base)
for b in a["country"]:
    if not b.get("other"):
        b["v"] += 50; break
rc, out = run(a); results.append(("a · country value tamper", rc == 2 and "OVERVIEW" in out, rc))

# (b) tamper segment honest-null bucket -> OVERVIEW_DRIFT (two-way)
b2 = copy.deepcopy(base)
for b in b2["segment"]:
    if b.get("null"):
        b["v"] = 0; break
rc, out = run(b2); results.append(("b · segment null tamper", rc == 2 and "OVERVIEW" in out, rc))

# (c) tamper a standard's yes -> OVERVIEW_DRIFT (would falsely inflate compliance)
c = copy.deepcopy(base)
c["standards"][0]["yes"] += 99
rc, out = run(c); results.append(("c · standard yes tamper", rc == 2 and "OVERVIEW_DRIFT" in out, rc))

rc, out = run(base); results.append(("restore · real data passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P2.3:", "PASS — data-overview gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
