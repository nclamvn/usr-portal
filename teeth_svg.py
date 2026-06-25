#!/usr/bin/env python3
"""TIP-UX2.1 teeth — prove verify_svg (SVG_FILL_IMPLICIT) bites. Drops a temp .html with an
implicit-fill shape into the tree, asserts the gate exits 2, then removes it and asserts 0."""
import subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
TMP = ROOT / "_teeth_svg_tmp.html"


def run():
    r = subprocess.run([sys.executable, str(ROOT / "verify_svg.py")], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


results = []
# (restore) clean tree passes
rc, out = run(); results.append(("restore · clean tree passes", rc == 0))

# (a) <svg> with no root fill + a class-filled shape (no fill attr) -> SVG_FILL_IMPLICIT
TMP.write_text('<!doctype html><svg viewBox="0 0 10 10"><circle class="x" cx="5" cy="5" r="4"/></svg>')
rc, out = run(); results.append(("inject implicit-fill svg → caught", rc == 2 and "SVG_FILL_IMPLICIT" in out))

# (b) add a root fill="none" -> safe again
TMP.write_text('<!doctype html><svg viewBox="0 0 10 10" fill="none"><circle class="x" cx="5" cy="5" r="4"/></svg>')
rc, out = run(); results.append(("root fill=none → safe", rc == 0))

TMP.unlink(missing_ok=True)
rc, out = run(); results.append(("cleanup · tree passes again", rc == 0))

ok = all(x for _, x in results)
for name, x in results:
    print(f"  {'BITE' if x else 'MISS'}  {name}")
print("TEETH-SVG:", "PASS — SVG gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
