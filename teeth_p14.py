#!/usr/bin/env python3
"""TIP-P1.4 teeth — prove verify_taxonomy bites. Copies the page dirs to temp, deletes one page,
runs the gate against the temp dirs; the real country/ + segment/ are never touched."""
import subprocess, sys, tempfile, os, shutil, pathlib
ROOT = pathlib.Path(__file__).resolve().parent


def run(cdir, sdir):
    r = subprocess.run([sys.executable, str(ROOT / "verify_taxonomy.py"), str(cdir), str(sdir)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


tmp = tempfile.mkdtemp(dir="/tmp")
ctmp, stmp = pathlib.Path(tmp) / "country", pathlib.Path(tmp) / "segment"
shutil.copytree(ROOT / "country", ctmp)
shutil.copytree(ROOT / "segment", stmp)
results = []

# (a) delete a country page -> its term has no page -> TAXONOMY_MISSING
victim = sorted(ctmp.glob("*.html"))[0]
victim.unlink()
rc, out = run(ctmp, stmp)
results.append(("a · missing country page", rc == 2 and "TAXONOMY_MISSING" in out, rc))

# (b) add an orphan page with no term -> TAXONOMY_ORPHAN
(stmp / "ghost-segment.html").write_text("x")
rc, out = run(ctmp, stmp)
results.append(("b · orphan segment page", rc == 2 and "TAXONOMY_ORPHAN" in out, rc))

# restore check — the real dirs must pass
rc, out = run(ROOT / "country", ROOT / "segment")
results.append(("restore · real dirs pass", rc == 0, rc))

shutil.rmtree(tmp, ignore_errors=True)
ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P1.4:", "PASS — taxonomy gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
