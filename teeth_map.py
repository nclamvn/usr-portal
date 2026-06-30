#!/usr/bin/env python3
"""Teeth for verify_map — prove all 6 map gates BITE. Mutate a real rendered page in memory, run the
shared check, assert the matching gate fires; then prove the clean page passes."""
import pathlib, re
import verify_map as V

ROOT = pathlib.Path(__file__).resolve().parent
html = (ROOT / "data.html").read_text()
fhtml = (ROOT / "segment" / "loitering-munition.html").read_text()   # a Tier-2 filter page
live, total, uav = V.live_counts()
co_hq = V.company_hq()
ok = True


def run(name, mutated, want):
    global ok
    fails = []
    V.check_map(mutated, live, total, fails, ROOT, uav=uav)
    bit = any(f.startswith(want) for f in fails)
    ok = ok and bit
    print(f"{name:22s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ' + str(fails[:1])}")


def run_hq(name, mutated, want):
    global ok
    fails = []
    V.check_hq(mutated, co_hq, fails, ROOT)
    bit = any(f.startswith(want) for f in fails)
    ok = ok and bit
    print(f"{name:22s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ' + str(fails[:1])}")


# clean positive controls — global map, a filter page, and the HQ pins all pass untouched
fc = []
V.check_map(html, live, total, fc, ROOT, uav=uav)
V.check_map(fhtml, live, total, fc, ROOT, uav=uav)
V.check_hq(html, co_hq, fc, ROOT)
print(f"{'CLEAN':22s} : {'PASS' if not fc else '!! ' + str(fc[:1])}")
ok = ok and not fc

# (a) FIGURE_DRIFT — corrupt one dot's data-n on the global map
drift = re.sub(r'(data-c="United States"[^>]*data-n=")\d+(")', r'\g<1>999\2', html, count=1)
run("MAP_FIGURE_DRIFT", drift, "MAP_FIGURE_DRIFT")

# (b) NULL_FAKED — set a dot count to 0
nf = re.sub(r'(data-c="China"[^>]*data-n=")\d+(")', r'\g<1>0\2', html, count=1)
run("MAP_NULL_FAKED", nf, "MAP_NULL_FAKED")

# (c) UNPLACED — drop the header placed total (claim fewer placed than counted)
up = re.sub(r'(class="wmap"[^>]*data-placed=")\d+(")', r'\g<1>1\2', html, count=1)
run("MAP_UNPLACED", up, "MAP_UNPLACED")

# (d) DANGLING — point a dot at a ghost country page
dg = re.sub(r'href="country/[a-z0-9-]+\.html"', 'href="country/ghost-nowhere.html"', html, count=1)
run("MAP_DANGLING", dg, "MAP_DANGLING")

# (e) THEME_LEAK — inject a raw hex inside the map block
tl = html.replace('<g class="wm-dots">', '<g class="wm-dots"><circle fill="#ff0000"/>', 1)
run("MAP_THEME_LEAK", tl, "MAP_THEME_LEAK")

# (f) FILTER_DRIFT — corrupt a dot on a Tier-2 filter page (subset recompute must catch it)
fd = re.sub(r'(<circle[^>]*data-c="[^"]*"[^>]*data-n=")\d+(")', r'\g<1>998\2', fhtml, count=1)
run("MAP_FILTER_DRIFT", fd, "MAP_FILTER_DRIFT")

# (g) PIN_FAKED — repoint a pin to a company with no recorded hq_city (fabricated HQ)
pf = re.sub(r'(<path[^>]*)data-co="[^"]*"', r'\g<1>data-co="ghost-maker"', html, count=1)
run_hq("MAP_PIN_FAKED/fake-co", pf, "MAP_PIN_FAKED")

# (g2) PIN_FAKED — move a pin to a city that is not in the gazetteer / not the record's city
pc = re.sub(r'(<path[^>]*data-co="[^"]*"[^>]*)data-city="[^"]*"', r'\g<1>data-city="Atlantis"', html, count=1)
run_hq("MAP_PIN_FAKED/fake-city", pc, "MAP_PIN_FAKED")

print("MAP TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
raise SystemExit(0 if ok else 2)
