#!/usr/bin/env python3
"""TIP-P2.2 — SEO gate. Independent, fail-loud exit 2:
  · SITEMAP bijection — every <loc> resolves to a real page (SITEMAP_DEAD); every built page is in
    the sitemap (SITEMAP_MISSING).
  · SEO_FABRICATED — every value emitted in a page's JSON-LD must exist (undisputed) in site-data.
    Honest-null fields must be ABSENT from structured data; disputed fields must be ABSENT too.
Modes (for teeth): no args = full · `sitemap <path>` · `page <htmlfile>`."""
import json, sys, re, pathlib
from seo import BASE, SPEC_LD

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
TOP = ["index.html", "reference.html", "search.html", "compare.html", "data.html"]
DIRS = ["entity", "company", "country", "segment", "news", "analysis"]
LD_NAME_TO_KEY = {v: k for k, v in SPEC_LD.items()}


def load_site():
    s = json.loads(SITE.read_bytes())
    return {e["slug"]: e for e in s["entities"]}


def jsonld_blocks(htmltext):
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', htmltext, re.S):
        try:
            out.append(json.loads(m.group(1)))
        except Exception:
            out.append({"_parse_error": True})
    return out


def check_page(path, by_slug, fails):
    """Validate JSON-LD on one page against site-data (Product / Organization)."""
    html = (path if isinstance(path, pathlib.Path) else pathlib.Path(path)).read_text()
    slug = pathlib.Path(path).stem
    for obj in jsonld_blocks(html):
        if obj.get("_parse_error"):
            fails.append("SEO_FABRICATED: %s has invalid JSON-LD" % slug); continue
        t = obj.get("@type")
        e = by_slug.get(slug)
        if t == "Product" and e:
            for p in obj.get("additionalProperty", []):
                key = LD_NAME_TO_KEY.get(p.get("name"))
                fo = (e.get(key) or {}) if key else {}
                if not key or fo.get("value") is None:
                    fails.append("SEO_FABRICATED: %s Product prop %r has no real value" % (slug, p.get("name")))
                elif fo.get("status") == "disputed" or fo.get("disputed"):
                    fails.append("SEO_FABRICATED: %s emits DISPUTED field %s in structured data" % (slug, key))
                elif fo.get("value") != p.get("value"):
                    fails.append("SEO_FABRICATED: %s %s=%r != site %r" % (slug, key, p.get("value"), fo.get("value")))
        if t == "Organization" and e:
            def sv(k):
                x = e.get(k)
                return x.get("value") if isinstance(x, dict) and "value" in x and "disputed" not in x else None
            if "foundingDate" in obj and str(sv("founded_year")) != obj["foundingDate"]:
                fails.append("SEO_FABRICATED: %s foundingDate not sourced" % slug)
            if "sameAs" in obj and sv("website") not in obj["sameAs"]:
                fails.append("SEO_FABRICATED: %s sameAs not sourced" % slug)
            addr = obj.get("address", {})
            if addr.get("addressLocality") and addr["addressLocality"] != sv("hq_city"):
                fails.append("SEO_FABRICATED: %s addressLocality not sourced" % slug)


def check_sitemap(sm_path, fails):
    locs = re.findall(r"<loc>(.*?)</loc>", pathlib.Path(sm_path).read_text())
    have = set()
    for loc in locs:
        p = loc.replace(BASE + "/", "")
        have.add(p)
        if not (ROOT / p).exists():
            fails.append("SITEMAP_DEAD: <loc> %r does not resolve" % p)
    built = set(t for t in TOP if (ROOT / t).exists())
    for d in DIRS:
        built |= {str(p.relative_to(ROOT)) for p in (ROOT / d).glob("*.html")}
    for p in sorted(built - have):
        fails.append("SITEMAP_MISSING: page %r not in sitemap" % p)
    return len(locs)


def main():
    fails = []
    args = sys.argv[1:]
    if args and args[0] == "page":
        check_page(args[1], load_site(), fails)
    elif args and args[0] == "sitemap":
        check_sitemap(args[1], fails)
    else:
        by = load_site()
        n = check_sitemap(ROOT / "sitemap.xml", fails)
        pages = 0
        for d in ("entity", "company"):
            for p in (ROOT / d).glob("*.html"):
                check_page(p, by, fails); pages += 1
        print("seo: sitemap %d urls · %d entity+company JSON-LD checked" % (n, pages))
    if fails:
        print("\nSEO GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("SEO GATE PASS: sitemap bijection · JSON-LD carries only real, undisputed values.")


if __name__ == "__main__":
    main()
