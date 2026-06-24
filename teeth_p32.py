#!/usr/bin/env python3
"""TIP-P3.2 teeth — prove verify_review bites. Mutates temp copies of review-data.json; real untouched."""
import json, subprocess, sys, tempfile, os, copy, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
RV = ROOT / "out" / "review-data.json"


def run(obj):
    fd, p = tempfile.mkstemp(suffix=".json", dir="/tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, ensure_ascii=False)
    r = subprocess.run([sys.executable, str(ROOT / "verify_review.py"), p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode, r.stdout + r.stderr


base = json.loads(RV.read_bytes())
results = []

# (a) tamper a real dimension score -> REVIEW_DRIFT
a = copy.deepcopy(base)
for u in a["uavs"]:
    for k, s in u["scores"].items():
        if s is not None:
            u["scores"][k] = (s + 40) % 100 + 1; break
    else:
        continue
    break
rc, out = run(a); results.append(("a · tampered score", rc == 2 and "REVIEW_DRIFT" in out, rc))

# (b) score a honest-null dimension (penalise missing spec as 0) -> HONEST-NULL two-way
b = copy.deepcopy(base)
for u in b["uavs"]:
    for k, s in u["scores"].items():
        if s is None:
            u["scores"][k] = 0; break
    else:
        continue
    break
rc, out = run(b); results.append(("b · scored a null dim (0)", rc == 2 and "HONEST-NULL" in out, rc))

# (c) hand-tune a total -> REVIEW_TOTAL
c = copy.deepcopy(base)
for u in c["uavs"]:
    if u["total"] is not None:
        u["total"] = (u["total"] + 33) % 100; break
rc, out = run(c); results.append(("c · hand-tuned total", rc == 2 and "REVIEW_TOTAL" in out, rc))

rc, out = run(base); results.append(("restore · real passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P3.2:", "PASS — review gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
