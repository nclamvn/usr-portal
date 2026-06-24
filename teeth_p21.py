#!/usr/bin/env python3
"""TIP-P2.1 teeth — prove verify_search bites. Mutates temp copies of search-index.json; the real
file is never touched."""
import json, subprocess, sys, tempfile, os, copy, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
IDX = ROOT / "out" / "search-index.json"


def run(obj):
    fd, p = tempfile.mkstemp(suffix=".json", dir="/tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, ensure_ascii=False)
    r = subprocess.run([sys.executable, str(ROOT / "verify_search.py"), p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode, r.stdout + r.stderr


base = json.loads(IDX.read_bytes())
results = []

# (a) tamper an entry url -> SEARCH_DRIFT
a = copy.deepcopy(base)
a["entries"][0]["url"] = "entity/__ghost__.html"
rc, out = run(a); results.append(("a · drifted url", rc == 2 and "SEARCH_DRIFT" in out, rc))

# (b) drop an entry -> SEARCH_MISSING
b = copy.deepcopy(base)
b["entries"] = b["entries"][1:]
rc, out = run(b); results.append(("b · missing node entry", rc == 2 and "SEARCH_MISSING" in out, rc))

# (c) add a ghost entry -> SEARCH_ORPHAN
c = copy.deepcopy(base)
c["entries"].append({"id": "__ghost__", "type": "uav", "label_en": "x", "label_vn": "x",
                     "sub_en": "", "sub_vn": "", "url": "entity/__ghost__.html", "terms": "ghost"})
rc, out = run(c); results.append(("c · orphan entry", rc == 2 and "SEARCH_ORPHAN" in out, rc))

rc, out = run(base); results.append(("restore · real index passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P2.1:", "PASS — search gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
