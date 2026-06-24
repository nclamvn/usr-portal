#!/usr/bin/env python3
"""TIP-P2.2 teeth — prove verify_seo bites. Mutates temp copies only; real files untouched."""
import subprocess, sys, tempfile, os, re, pathlib
from seo import BASE
ROOT = pathlib.Path(__file__).resolve().parent


def run(args):
    r = subprocess.run([sys.executable, str(ROOT / "verify_seo.py")] + args, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


results = []

# (a) sitemap with a dead <loc> -> SITEMAP_DEAD
sm = (ROOT / "sitemap.xml").read_text().replace(
    "</urlset>", f"  <url><loc>{BASE}/entity/__ghost__.html</loc></url>\n</urlset>")
fd, p = tempfile.mkstemp(suffix=".xml", dir="/tmp"); open(p, "w").write(sm)
rc, out = run(["sitemap", p]); os.unlink(p)
results.append(("a · sitemap dead loc", rc == 2 and "SITEMAP_DEAD" in out, rc))

# (b) fabricated JSON-LD value (bump a Product additionalProperty) -> SEO_FABRICATED
victim = None
for f in sorted((ROOT / "entity").glob("*.html")):
    t = f.read_text()
    if '"additionalProperty"' in t and '"value":' in t:
        victim = (f, t); break
f, t = victim
i = t.find('"additionalProperty"')
t2 = t[:i] + re.sub(r'"value":\s*[0-9.]+', '"value": 999999', t[i:], count=1)
dst = pathlib.Path("/tmp") / f.name; dst.write_text(t2)
rc, out = run(["page", str(dst)]); dst.unlink()
results.append(("b · fabricated JSON-LD value", rc == 2 and "SEO_FABRICATED" in out, rc))

rc, out = run([]); results.append(("restore · real passes", rc == 0, rc))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P2.2:", "PASS — seo gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
