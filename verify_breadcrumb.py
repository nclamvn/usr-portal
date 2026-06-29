#!/usr/bin/env python3
"""TIP-BREADCRUMB gate — BreadcrumbList trỏ TRANG THẬT, không bịa. Fail-loud exit 2:
  · BC_MISSING   — trang nội dung / term taxonomy thiếu khối BreadcrumbList.
  · BC_DANGLING  — itemListElement.item trỏ URL không resolve về trang đã build (răng chống bịa lõi).
  · BC_POSITION  — position không 1..n liên tục, hoặc lá != canonical chính trang.
  · BC_NAME_FAKE — tên crumb lá rỗng / không xuất hiện trong <title> thật của trang.
  · BC_KNOW_*    — §8.4.3: knowledge page phải đủ canonical(meta) + DefinedTerm(schema) + breadcrumb.
"""
import json, sys, re, pathlib
import html as _html
from seo import BASE

ROOT = pathlib.Path(__file__).resolve().parent
DIRS = ["uav", "company", "news", "analysis", "knowledge", "country", "segment",
        "airframe", "propulsion", "weight", "flight-time", "compliance"]


def blocks(htmltext):
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', htmltext, re.S):
        try:
            out.append(json.loads(m.group(1)))
        except Exception:
            out.append({"_parse_error": True})
    return out


def norm(s):
    return _html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def main():
    fails, n = [], 0
    for d in DIRS:
        dp = ROOT / d
        if not dp.exists():
            continue
        for p in sorted(dp.glob("*.html")):
            html = p.read_text(encoding="utf-8")
            rel = str(p.relative_to(ROOT))
            bcs = [o for o in blocks(html) if o.get("@type") == "BreadcrumbList"]
            if not bcs:
                fails.append("BC_MISSING: %s has no BreadcrumbList" % rel); continue
            items = bcs[0].get("itemListElement", [])
            if [it.get("position") for it in items] != list(range(1, len(items) + 1)):
                fails.append("BC_POSITION: %s positions not 1..n" % rel)
            for it in items:
                path = (it.get("item") or "").replace(BASE + "/", "")
                if not path or not (ROOT / path).exists():
                    fails.append("BC_DANGLING: %s crumb -> %r does not resolve" % (rel, it.get("item")))
            if items:
                leaf = items[-1]
                if leaf.get("item") != BASE + "/" + rel:
                    fails.append("BC_POSITION: %s leaf %r != canonical" % (rel, leaf.get("item")))
                title = re.search(r"<title>(.*?)</title>", html, re.S)
                tt = norm(title.group(1)) if title else ""
                lname = norm(leaf.get("name") or "")
                if not lname:
                    fails.append("BC_NAME_FAKE: %s leaf name empty" % rel)
                elif lname not in tt:
                    fails.append("BC_NAME_FAKE: %s leaf %r not in page title" % (rel, lname))
            n += 1

    # §8.4.3 — knowledge SEO on-page: meta (canonical) + schema (DefinedTerm) + breadcrumb (above)
    for p in sorted((ROOT / "knowledge").glob("*.html")):
        html = p.read_text(encoding="utf-8")
        if 'rel="canonical"' not in html:
            fails.append("BC_KNOW_META: knowledge/%s missing canonical" % p.name)
        if '"@type": "DefinedTerm"' not in html:
            fails.append("BC_KNOW_SCHEMA: knowledge/%s missing DefinedTerm schema" % p.name)

    print("breadcrumb: %d pages with BreadcrumbList checked" % n)
    if fails:
        print("\nBREADCRUMB GATE FAIL (%d):" % len(fails))
        for f in fails[:25]:
            print("  -", f)
        sys.exit(2)
    print("BREADCRUMB GATE PASS: every crumb resolves to a real page · positions 1..n · leaf=canonical · names real.")


if __name__ == "__main__":
    main()
