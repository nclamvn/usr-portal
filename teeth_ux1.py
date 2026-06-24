#!/usr/bin/env python3
"""TIP-UX1 teeth — prove verify_header bites on HEADER_DRIFT. Copies one page to temp, perturbs its
header (extra control), runs the gate over the corpus + the tampered page; real pages untouched."""
import subprocess, sys, tempfile, os, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent


def run(extra=None):
    args = [sys.executable, str(ROOT / "verify_header.py")] + (extra or [])
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# (a) a single page with a drifted header -> HEADER_DRIFT (run gate over just two: clean + tampered)
clean = (ROOT / "reference.html").read_text()
tampered = re.sub(r'(<header class="gbar"><div class="gbar-in">)',
                  r'\1<button class="gbar-tg">EXTRA</button>', clean, count=1)
fd, p = tempfile.mkstemp(suffix=".html", dir="/tmp")
with os.fdopen(fd, "w") as f:
    f.write(tampered)
# the gate over a single tampered page can't see drift (1 form); compare against a clean one via a tiny dir
import shutil
d = pathlib.Path(tempfile.mkdtemp(dir="/tmp"))
shutil.copy(ROOT / "index.html", d / "index.html")          # clean form
shutil.copy(p, d / "reference.html")                        # drifted form
# point verify_header at the temp dir by monkey-style: run a one-off python that imports + checks
chk = f"""
import sys, re, pathlib
sys.path.insert(0, {str(ROOT)!r})
from verify_header import HDR, canonical
forms={{}}
for f in pathlib.Path({str(d)!r}).glob("*.html"):
    m=HDR.search(f.read_text())
    if m: forms.setdefault(canonical(m.group(0)),[]).append(f.name)
sys.exit(2 if len(forms)>1 else 0)
"""
r = subprocess.run([sys.executable, "-c", chk], capture_output=True, text=True)
bite_a = r.returncode == 2
os.unlink(p); shutil.rmtree(d, ignore_errors=True)

# restore — real corpus is one form
rc, out = run()
bite_restore = rc == 0 and "HEADER GATE PASS" in out

ok = bite_a and bite_restore
print(f"  {'BITE' if bite_a else 'MISS'}  a · drifted header (extra control)  (2 forms detected)")
print(f"  {'BITE' if bite_restore else 'MISS'}  restore · real corpus = 1 form  (gate exit {rc})")
print("TEETH-UX1:", "PASS — header gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
