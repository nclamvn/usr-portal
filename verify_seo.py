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
TOP = ["index.html", "reference.html", "search.html", "compare.html", "data.html", "knowledge.html", "review.html", "news.html"]
DIRS = ["uav", "company", "country", "segment", "airframe", "propulsion", "weight", "flight-time", "compliance", "news", "analysis", "knowledge", "news-card"]
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


ART_TYPES = {"NewsArticle", "AnalysisNewsArticle", "Article", "ReportageNewsArticle"}
REVIEWDATA = ROOT / "out" / "review-data.json"


def check_article(path, fails):
    """§8.10.1 — every news/ + analysis/ page must carry an Article-type JSON-LD; and that block must
    be internally honest (headline present, ISO datePublished, real publisher, no empty byline)."""
    html = path.read_text()
    slug = path.stem
    art = None
    for obj in jsonld_blocks(html):
        if obj.get("_parse_error"):
            fails.append("SEO_FABRICATED: %s has invalid JSON-LD" % slug); continue
        if obj.get("@type") in ART_TYPES:
            art = obj
    if art is None:
        fails.append("SEO_LD_MISSING: %s has no Article JSON-LD (§8.10.1 100%%)" % slug); return
    if not (art.get("headline") or "").strip():
        fails.append("SEO_FABRICATED: %s Article headline empty" % slug)
    dp = art.get("datePublished")
    if dp and not re.match(r"^\d{4}-\d{2}-\d{2}", str(dp)):
        fails.append("SEO_FABRICATED: %s datePublished %r not ISO" % (slug, dp))
    pub = (art.get("publisher") or {}).get("name")
    if pub != "Uncrewed Systems Review":
        fails.append("SEO_FABRICATED: %s publisher %r != site" % (slug, pub))
    au = art.get("author")
    if au is not None and not (au.get("name") or "").strip():
        fails.append("SEO_FABRICATED: %s Article author present but empty (fabricated byline)" % slug)


def check_reviews(fails, page=None):
    """§8.10.1 Review — every Review on review.html must carry a REAL spec-derived rating (== the live
    capability total in review-data.json), reviewed by the org (no fabricated person)."""
    page = pathlib.Path(page) if page else ROOT / "review.html"
    if not page.exists() or not REVIEWDATA.exists():
        return 0
    by_name = {u["name"]: u["total"] for u in json.loads(REVIEWDATA.read_bytes())["uavs"]}
    scored = sum(1 for t in by_name.values() if t is not None)
    blocks = [o for o in jsonld_blocks(page.read_text()) if o.get("@type") == "Review"]
    if scored and not blocks:
        fails.append("SEO_LD_MISSING: review.html has %d scored UAV but 0 Review JSON-LD" % scored)
    for o in blocks:
        nm = (o.get("itemReviewed") or {}).get("name")
        rv = (o.get("reviewRating") or {}).get("ratingValue")
        if nm not in by_name:
            fails.append("SEO_FABRICATED: review %r not in registry" % nm)
        elif by_name[nm] is None:
            fails.append("SEO_FABRICATED: review %r emits rating for honest-null (unscored)" % nm)
        elif by_name[nm] != rv:
            fails.append("SEO_FABRICATED: review %r ratingValue=%r != live %r" % (nm, rv, by_name[nm]))
        if (o.get("author") or {}).get("@type") != "Organization":
            fails.append("SEO_FABRICATED: review %r author not the org (fabricated reviewer?)" % nm)
    return len(blocks)


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
    elif args and args[0] == "article":
        check_article(pathlib.Path(args[1]), fails)
    elif args and args[0] == "reviews":
        check_reviews(fails, args[1] if len(args) > 1 else None)
    elif args and args[0] == "sitemap":
        check_sitemap(args[1], fails)
    else:
        by = load_site()
        n = check_sitemap(ROOT / "sitemap.xml", fails)
        pages = 0
        for d in ("uav", "company"):
            for p in (ROOT / d).glob("*.html"):
                check_page(p, by, fails); pages += 1
        arts = 0
        for d in ("news", "analysis"):
            for p in (ROOT / d).glob("*.html"):
                check_article(p, fails); arts += 1
        revs = check_reviews(fails)
        print("seo: sitemap %d urls · %d entity+company JSON-LD · %d Article pages · %d Review LD checked"
              % (n, pages, arts, revs))
    if fails:
        print("\nSEO GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("SEO GATE PASS: sitemap bijection · JSON-LD carries only real, undisputed values.")


if __name__ == "__main__":
    main()
