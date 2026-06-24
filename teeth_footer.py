#!/usr/bin/env python3
"""Footer gate teeth — prove verify_footer bites. Builds a tiny temp dir with one clean page + one
drifted-footer page; the gate must report >1 form. Real pages untouched."""
import subprocess, sys, re, tempfile, shutil, pathlib
ROOT = pathlib.Path(__file__).resolve().parent

results = []
clean = (ROOT / "reference.html").read_text()
FT = re.compile(r'(<footer class="sfoot.*?</footer>)', re.S)
drift = FT.sub(lambda m: m.group(1).replace('</footer>', '<span>DRIFT</span></footer>', 1), clean, count=1)

d = pathlib.Path(tempfile.mkdtemp(dir="/tmp"))
(d / "a.html").write_text(clean)
(d / "b.html").write_text(drift)
chk = f"""
import sys, re, pathlib
sys.path.insert(0, {str(ROOT)!r})
from verify_footer import FT, canonical
forms={{}}
for f in pathlib.Path({str(d)!r}).glob("*.html"):
    m=FT.search(f.read_text())
    if m: forms.setdefault(canonical(m.group(0)),[]).append(f.name)
sys.exit(2 if len(forms)>1 else 0)
"""
r = subprocess.run([sys.executable, "-c", chk], capture_output=True, text=True)
results.append(("a · drifted footer -> 2 forms", r.returncode == 2, r.returncode))
shutil.rmtree(d, ignore_errors=True)

r2 = subprocess.run([sys.executable, str(ROOT / "verify_footer.py")], capture_output=True, text=True)
results.append(("restore · real corpus = 1 form", r2.returncode == 0 and "FOOTER GATE PASS" in r2.stdout, r2.returncode))

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (exit {rc})")
print("TEETH-FOOTER:", "PASS — footer gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
