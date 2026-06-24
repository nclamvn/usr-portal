#!/usr/bin/env python3
"""TIP-P0.2 teeth — prove verify_graph bites. Mutates ONLY temp copies of graph.json; the real
out/graph.json is never touched. Exit 0 only if the ghost-edge graph fails (DANGLING_LINK), a
dropped-edge graph fails (GRAPH_STALE), and the real graph passes (exit 0)."""
import json, subprocess, sys, tempfile, os, copy, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
GRAPH = ROOT / "out" / "graph.json"


def run(path):
    r = subprocess.run([sys.executable, str(ROOT / "verify_graph.py"), str(path)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def run_obj(obj):
    fd, p = tempfile.mkstemp(suffix=".json", dir="/tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, ensure_ascii=False)
    rc, out = run(p); os.unlink(p)
    return rc, out


base = json.loads(GRAPH.read_bytes())
results = []

# (a) ghost edge: article -> a UAV slug that does not exist -> DANGLING_LINK
a = copy.deepcopy(base)
a["edges"].append(["article:truy-nguyen-loi-the-uav", "entity:uav:__ghost__", "tag"])
rc, out = run_obj(a); results.append(("a · ghost-edge dangling", rc == 2 and "DANGLING_LINK" in out, rc))

# (b) drop an edge: graph goes stale vs live re-derivation -> GRAPH_STALE
b = copy.deepcopy(base)
if b["edges"]:
    b["edges"].pop()
rc, out = run_obj(b); results.append(("b · dropped-edge staleness", rc == 2 and "GRAPH_STALE" in out, rc))

# restore — the real graph must still PASS
rc, out = run(GRAPH); results.append(("restore · real graph passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P0.2:", "PASS — graph gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
