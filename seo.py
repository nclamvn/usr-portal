#!/usr/bin/env python3
"""TIP-P2.2 — SEO helpers (shared). JSON-LD per type containing ONLY values that exist in site-data:
honest-null fields are omitted (never emitted as empty/0), disputed fields are kept OUT of structured
data entirely (we don't hand a search engine a value two sources disagree on). Plus canonical + OG.
BASE is the production origin — set it to the real deploy URL before going live (gates are domain-
independent: they check path resolution + value provenance, not the host)."""
import json

BASE = "https://usr-portal.vercel.app"   # production origin (Vercel default cho repo usr-portal); đổi sang domain riêng khi DNS sẵn
SHARE_IMG = "images/content/hero/hero-detroit.webp"   # default social share image — RtR-OWNED (never a third-party news photo)
SPEC_LD = {"mtow_kg": "MTOW (kg)", "max_payload_kg": "Max payload (kg)", "endurance_min": "Endurance (min)",
           "max_range_km": "Max range (km)", "max_link_km": "Datalink (km)", "max_speed_ms": "Max speed (m/s)",
           "service_ceiling_m": "Service ceiling (m)"}
NUMERIC = list(SPEC_LD)


def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def favicons(path):
    """Favicon/PWA links with a RELATIVE prefix derived from page depth, so they resolve under any
    deploy sub-path (e.g. /usr-portal/) — never a root-absolute '/…' (sub-path invariant)."""
    p = "../" * path.count("/")          # 'entity/x.html' -> '../' ; 'index.html' -> ''
    return (f'<link rel="icon" type="image/png" href="{p}favicon-96x96.png" sizes="96x96">'
            f'<link rel="icon" type="image/svg+xml" href="{p}favicon.svg">'
            f'<link rel="shortcut icon" href="{p}favicon.ico">'
            f'<link rel="apple-touch-icon" sizes="180x180" href="{p}apple-touch-icon.png">'
            f'<link rel="manifest" href="{p}site.webmanifest">'
            f'<meta name="theme-color" content="#1A1A1C">')


def meta(title, desc, path, image=None):
    """canonical + Open Graph + Twitter card + favicons. path is the site-relative url. `image` (site-
    relative) overrides the default RtR-owned share image (per-article cover); never a third-party photo."""
    url = BASE + "/" + path
    d = (desc or "").replace('"', "'")
    img = BASE + "/" + (image or SHARE_IMG).lstrip("/")
    return (f'<link rel="canonical" href="{url}">'
            f'<meta property="og:title" content="{title}">'
            f'<meta property="og:description" content="{d}">'
            f'<meta property="og:type" content="website">'
            f'<meta property="og:url" content="{url}">'
            f'<meta property="og:site_name" content="Uncrewed Systems Review">'
            f'<meta property="og:image" content="{img}">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<meta name="twitter:title" content="{title}">'
            f'<meta name="twitter:description" content="{d}">'
            f'<meta name="twitter:image" content="{img}">'
            f'<meta name="description" content="{d}">'
            + favicons(path))


def website_ld():
    """Site-level structured data for the homepage — Organization + WebSite. Only real identity values
    (name/url/logo), no registry numbers, so verify_seo (SEO_FABRICATED) passes."""
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Uncrewed Systems Review",
           "url": BASE, "logo": BASE + "/images/content/rtr/hera-studio-black.webp"}
    web = {"@context": "https://schema.org", "@type": "WebSite", "name": "Uncrewed Systems Review",
           "url": BASE, "description": "A sourced, comparable registry of uncrewed aerial systems."}
    return _ld(org) + _ld(web)


def product_ld(e, path):
    """Product JSON-LD for a UAV — only real, undisputed values."""
    name = (e.get("name") or {}).get("value")
    if not name:
        return ""
    obj = {"@context": "https://schema.org", "@type": "Product", "name": name, "url": BASE + "/" + path}
    maker = (e.get("manufacturer") or {}).get("value")
    if maker:
        obj["manufacturer"] = {"@type": "Organization", "name": maker}
    seg = (e.get("market_segment") or {}).get("value")
    if seg:
        obj["category"] = seg
    props = []
    for k in NUMERIC:
        fo = e.get(k) or {}
        v = fo.get("value")
        if v is None or fo.get("status") == "disputed" or fo.get("disputed"):
            continue   # honest-null omitted · disputed kept OUT of structured data
        props.append({"@type": "PropertyValue", "name": SPEC_LD[k], "value": v})
    if props:
        obj["additionalProperty"] = props
    return _ld(obj)


def org_ld(c, path):
    """Organization JSON-LD for a company — only SOURCED fields (honest-null omitted)."""
    obj = {"@context": "https://schema.org", "@type": "Organization",
           "name": c.get("name"), "url": BASE + "/" + path}
    def sv(k):
        x = c.get(k)
        return x.get("value") if isinstance(x, dict) and "value" in x and "disputed" not in x else None
    web = sv("website")
    if web:
        obj["sameAs"] = [web]
    yr = sv("founded_year")
    if yr:
        obj["foundingDate"] = str(yr)
    city = sv("hq_city")
    country = sv("hq_country")
    if city or country:
        obj["address"] = {"@type": "PostalAddress",
                          **({"addressLocality": city} if city else {}),
                          **({"addressCountry": country} if country else {})}
    return _ld(obj)


def collection_ld(name, path, n):
    return _ld({"@context": "https://schema.org", "@type": "CollectionPage",
                "name": name, "url": BASE + "/" + path, "numberOfItems": n})


def definedterm_ld(term, definition, path):
    """DefinedTerm JSON-LD for a knowledge entry — term + its real definition (no fabrication)."""
    return _ld({"@context": "https://schema.org", "@type": "DefinedTerm", "name": term,
                "description": definition, "url": BASE + "/" + path})
