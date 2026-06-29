#!/usr/bin/env python3
"""Teeth cho verify_taxonomy — chứng mỗi răng CẮN. Mutate bản thật rồi RESTORE (try/finally);
sample backlink lấy đúng từ recompute để ca ASYMMETRY tất-định."""
import subprocess, sys, json, pathlib, re
import verify_taxonomy as V

ROOT = pathlib.Path(__file__).resolve().parent


def run():
    r = subprocess.run([sys.executable, str(ROOT / "verify_taxonomy.py")], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


results = []


def record(name, bit, rc):
    results.append((name, bit, rc))


def mutate(path, newtext, want, name, created=False):
    bak = path.read_text(encoding="utf-8") if path.exists() else None
    try:
        path.write_text(newtext, encoding="utf-8")
        rc, out = run()
        record(name, rc == 2 and want in out, rc)
    finally:
        if created:
            path.unlink()
        elif bak is not None:
            path.write_text(bak, encoding="utf-8")


def main():
    site = json.loads((ROOT / "out" / "site-data.json").read_bytes())
    uavs = [e for e in site["entities"] if e.get("entity_type", "uav") == "uav"]
    exp, sample = V.recompute(uavs)

    rc, out = run()
    record("clean control", rc == 0, rc)

    # a real term page (not index)
    tp = next(p for p in sorted((ROOT / "airframe").glob("*.html")) if p.stem != "index")
    txt = tp.read_text(encoding="utf-8")

    # (a) NULL_FAKED — inject a non-qualifying entity link
    mutate(tp, txt.replace("</ul>", '<li><a href="../uav/zzz-ghost.html">x</a></li></ul>', 1),
           "TAX_NULL_FAKED", "a · faked member")

    # (b) COUNT_DRIFT — drop one real member link
    drop = re.sub(r'<li><a href="\.\./uav/[a-z0-9-]+\.html">.*?</a></li>', "", txt, count=1)
    mutate(tp, drop, "TAX_COUNT_DRIFT", "b · dropped member")

    # (c) THEME_LEAK — hardcoded color inside <style>
    idx = ROOT / "airframe" / "index.html"
    itxt = idx.read_text(encoding="utf-8")
    mutate(idx, itxt.replace("</style>", "  a{color:#ff0000}\n</style>", 1),
           "TAX_THEME_LEAK", "c · hardcoded color")

    # (d) LINK_ASYMMETRY — remove the backlink from the entity page the gate samples
    uav_slug, href = sample["airframe"]
    up = ROOT / "uav" / f"{uav_slug}.html"
    utxt = up.read_text(encoding="utf-8")
    mutate(up, utxt.replace(href, "#severed"), "TAX_LINK_ASYMMETRY", "d · severed backlink")

    # (e) ORPHAN — stray term page with no registry value
    ghost = ROOT / "airframe" / "__ghost__.html"
    mutate(ghost, "<html><body>no uav</body></html>", "TAX_ORPHAN", "e · orphan page", created=True)

    ok = all(b for _, b, _ in results)
    for n, b, rc in results:
        tag = "PASS" if n == "clean control" and b else ("CẮN ✓" if b else "KHÔNG CẮN ✗")
        print(f"  {tag:8s} {n}  (exit {rc})")
    print("TAXONOMY TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
