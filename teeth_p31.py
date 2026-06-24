#!/usr/bin/env python3
"""TIP-P3.1 teeth — prove verify_knowledge bites. Copies knowledge/ to temp, mutates; real untouched."""
import subprocess, sys, tempfile, shutil, pathlib
ROOT = pathlib.Path(__file__).resolve().parent


def run(kdir):
    r = subprocess.run([sys.executable, str(ROOT / "verify_knowledge.py"), str(kdir)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


tmp = pathlib.Path(tempfile.mkdtemp(dir="/tmp")) / "knowledge"
shutil.copytree(ROOT / "knowledge", tmp)
results = []

# (a) delete a term page -> KNOWLEDGE_MISSING
victim = sorted(tmp.glob("*.html"))[0]
victim.unlink()
rc, out = run(tmp); results.append(("a · missing term page", rc == 2 and "KNOWLEDGE_MISSING" in out, rc))

# (b) add an orphan page with no term -> KNOWLEDGE_ORPHAN
(tmp / "ghost-term.html").write_text("x")
rc, out = run(tmp); results.append(("b · orphan term page", rc == 2 and "KNOWLEDGE_ORPHAN" in out, rc))

rc, out = run(ROOT / "knowledge"); results.append(("restore · real passes", rc == 0, rc))
shutil.rmtree(tmp.parent, ignore_errors=True)

ok = all(p for _, p, _ in results)
for n, p, rc in results:
    print(f"  {'BITE' if p else 'MISS'}  {n}  (gate exit {rc})")
print("TEETH-P3.1:", "PASS — knowledge gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
