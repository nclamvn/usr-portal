#!/usr/bin/env python3
"""TIP-UX2 teeth — prove verify_home bites. Mutates a temp copy of index.html; the real file untouched."""
import subprocess, sys, tempfile, os, re, pathlib, shutil
ROOT = pathlib.Path(__file__).resolve().parent


def run_against(tmp_home):
    # verify_home hardcodes HOME; run a shim that points it at the temp file
    shim = f"""
import sys, pathlib
sys.argv=['x']
import importlib.util
spec=importlib.util.spec_from_file_location('vh', {str(ROOT/'verify_home.py')!r})
m=importlib.util.module_from_spec(spec)
m_HOME={str(tmp_home)!r}
spec.loader.exec_module(m)
m.HOME=pathlib.Path({str(tmp_home)!r})
m.main()
"""
    r = subprocess.run([sys.executable, "-c", shim], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


real = (ROOT / "index.html").read_text()
results = []

# (a) inject an empty media-slot marker -> EMPTY_MEDIA_SLOT
fd, p = tempfile.mkstemp(suffix=".html", dir="/tmp"); os.close(fd)
pathlib.Path(p).write_text(real.replace("</body>", '<div class="pk">Media Library</div></body>', 1))
rc, out = run_against(p); results.append(("a · empty media slot", rc == 2 and "EMPTY_MEDIA_SLOT" in out, rc))
os.unlink(p)

# (b) tamper the hero number -> HOME_FIGURE_DRIFT
fd, p = tempfile.mkstemp(suffix=".html", dir="/tmp"); os.close(fd)
import json
n = len([e for e in json.load(open(ROOT/"out"/"site-data.json"))["entities"] if e.get("entity_type","uav")=="uav"])
pathlib.Path(p).write_text(real.replace(f'>{n}<', '>99999<'))
rc, out = run_against(p); results.append(("b · tampered hero count", rc == 2 and "HOME_FIGURE_DRIFT" in out, rc))
os.unlink(p)

# restore — real home passes
rc, out = run_against(ROOT / "index.html"); results.append(("restore · real home passes", rc == 0, rc))

ok = all(x for _, x, _ in results)
for nme, x, rc in results:
    print(f"  {'BITE' if x else 'MISS'}  {nme}  (exit {rc})")
print("TEETH-HOME:", "PASS — home gate has teeth" if ok else "FAIL")
sys.exit(0 if ok else 2)
