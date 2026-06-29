#!/usr/bin/env python3
"""PRD §4.2 URL pattern + §8.1.4 (link không vỡ) — giữ align /uav/ bền, fail-loud exit 2:
  · REDIRECT_MISSING — vercel.json thiếu 301 /entity/* -> /uav/* (statusCode 301 đúng spec §4.2/§8.1.4; link cũ đang index sẽ vỡ).
  · STALE_ENTITY_DIR — thư mục entity/ quay lại (URL pattern lệch PRD §4.2 trở lại).
  · UAV_DIR_EMPTY    — uav/ rỗng (detail layer không render về đúng dir).
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    fails = []
    vj = json.loads((ROOT / "vercel.json").read_text())
    reds = vj.get("redirects", [])
    ok = any("/entity/" in r.get("source", "") and "/uav/" in r.get("destination", "") and r.get("statusCode") == 301
             for r in reds)
    if not ok:
        fails.append("REDIRECT_MISSING: vercel.json không có redirect 301 (statusCode:301) /entity/* -> /uav/*")
    if (ROOT / "entity").exists():
        fails.append("STALE_ENTITY_DIR: thư mục entity/ tồn tại (URL pattern lệch §4.2)")
    n = len(list((ROOT / "uav").glob("*.html"))) if (ROOT / "uav").exists() else 0
    if n == 0:
        fails.append("UAV_DIR_EMPTY: uav/ không có trang detail")
    if fails:
        print("\nREDIRECT GATE FAIL (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        sys.exit(2)
    print("REDIRECT GATE PASS: 301 /entity/->/uav/ present · no stale entity/ · uav/ has %d pages." % n)


if __name__ == "__main__":
    main()
