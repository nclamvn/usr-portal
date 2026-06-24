#!/usr/bin/env python3
"""TIP-P2.2 — SEO helpers (shared). JSON-LD per type containing ONLY values that exist in site-data:
honest-null fields are omitted (never emitted as empty/0), disputed fields are kept OUT of structured
data entirely (we don't hand a search engine a value two sources disagree on). Plus canonical + OG.
BASE is the production origin — set it to the real deploy URL before going live (gates are domain-
independent: they check path resolution + value provenance, not the host)."""
import json

BASE = "https://nclamvn.github.io/usr-portal"   # TODO(owner): confirm production origin
SPEC_LD = {"mtow_kg": "MTOW (kg)", "max_payload_kg": "Max payload (kg)", "endurance_min": "Endurance (min)",
           "max_range_km": "Max range (km)", "max_link_km": "Datalink (km)", "max_speed_ms": "Max speed (m/s)",
           "service_ceiling_m": "Service ceiling (m)"}
NUMERIC = list(SPEC_LD)


def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def meta(title, desc, path):
    """canonical + Open Graph. path is the site-relative url (e.g. 'entity/x.html')."""
    url = BASE + "/" + path
    d = (desc or "").replace('"', "'")
    return (f'<link rel="canonical" href="{url}">'
            f'<meta property="og:title" content="{title}">'
            f'<meta property="og:description" content="{d}">'
            f'<meta property="og:type" content="website">'
            f'<meta property="og:url" content="{url}">'
            f'<meta name="description" content="{d}">')


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
