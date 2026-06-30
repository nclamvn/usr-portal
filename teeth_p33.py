#!/usr/bin/env python3
"""TIP-P3.3 teeth — prove verify_newsroom bites on all 6 gates. Writes tampered temp .md; the real
content/newsroom/*.md is never touched."""
import subprocess, sys, tempfile, os, re, pathlib
import yaml
ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "content" / "newsroom"


def split(md):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", md, re.S)
    return yaml.safe_load(m.group(1)), m.group(2)


def assemble(fm, body):
    return "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n" + body


def run(text):
    fd, p = tempfile.mkstemp(suffix=".md", dir="/tmp")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    r = subprocess.run([sys.executable, str(ROOT / "verify_newsroom.py"), p], capture_output=True, text=True)
    os.unlink(p)
    return r.returncode, r.stdout + r.stderr


note = (SRC / "bai-01-data-note-phuong-phap.md").read_text()
report = (SRC / "bai-04-data-report-phan-bo-hang.md").read_text()
results = []

# (a) figure drift — break the live total_uav figure in body (count, not a hardcoded number)
import json as _json
_total = str(sum(1 for e in _json.loads((ROOT / "out" / "site-data.json").read_text())["entities"]
                 if e.get("entity_type") == "uav"))
fm, body = split(note)
rc, out = run(assemble(fm, body.replace(_total, "999")))
results.append(("a · figure drift", rc == 2 and "CONTENT_FIGURE_DRIFT" in out, rc))

# (b) opinion without human_author
fm, body = split(note); fm["type"] = "opinion"; fm["human_author"] = None
rc, out = run(assemble(fm, body))
results.append(("b · opinion no author", rc == 2 and "OPINION_REQUIRES_HUMAN_AUTHOR" in out, rc))

# (c) dangling tag
fm, body = split(note); fm["entity_tags"] = ["company:ghost-co"]
rc, out = run(assemble(fm, body))
results.append(("c · dangling tag", rc == 2 and "DANGLING_TAG" in out, rc))

# (d) format violation — em-dash
fm, body = split(note)
rc, out = run(assemble(fm, body + "\n\nMột câu có em-dash — sai quy phạm."))
results.append(("d · em-dash", rc == 2 and "FORMAT_VIOLATION" in out, rc))

# (e) data-report missing disclosure
fm, body = split(report)
body2 = re.sub(r"[^.]*tuyển chọn[^.]*\.", "", body)
body2 = re.sub(r"[^.]*không phải thị[^.]*\.", "", body2)
body2 = re.sub(r"[^.]*cấu trúc của (tập|chính)[^.]*\.", "", body2)
rc, out = run(assemble(fm, body2))
results.append(("e · report no disclosure", rc == 2 and "SAMPLE_DISCLOSURE_MISSING" in out, rc))

# (f) source missing
fm, body = split(note); fm["sources"] = []
rc, out = run(assemble(fm, body))
results.append(("f · source missing", rc == 2 and "SOURCE_MISSING" in out, rc))

# restore — real corpus passes
r = subprocess.run([sys.executable, str(ROOT / "verify_newsroom.py")], capture_output=True, text=True)
results.append(("restore · real corpus passes", r.returncode == 0, r.returncode))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P3.3:", "PASS — newsroom gate has 6 teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
