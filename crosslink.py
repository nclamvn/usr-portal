#!/usr/bin/env python3
"""TIP-P0.2 — build-time cross-link graph (SKELETON). Reads site-data/2 + articles + glossary,
emits out/graph.json: nodes (every REAL entity / taxonomy value / glossary term / article) and
edges (derived ONLY from real fields — no fabricated relations). Computed live every build;
deterministic (sorted) so idempotent. Ships WITH its auditor verify_graph.py (dangling-link gate).

Edge families (P0 skeleton):
  uav -> tax:manufacturer|country|segment   taxonomy membership. manufacturer target is the
                                            P1 RE-POINT SEAM (see manufacturer_target).
  article -> entity:uav                     entity_tags type=aircraft with slug (entity-centric).
  article -> term                           article.glossary[] mentions (knowledge link).
Label-only tags (country/technology tags without a canonical target) are intentionally NOT edged
at P0 — no fabricated relations; they get edges once taxonomy/knowledge nodes are promoted (P1/P3).
"""
import json, pathlib, re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
GLOSS = ROOT / "content" / "glossary.json"
OUT = ROOT / "out" / "graph.json"


def slugify(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
def val(e, f): return (e.get(f) or {}).get("value")


def manufacturer_target(value, company_slugs):
    """P1 RE-POINT SEAM. If a company entity exists for this manufacturer, the edge points at the
    company node; otherwise at the taxonomy node. The dangling-gate logic ('dst must resolve to a
    real node') is identical either way — P1 promotion only flips the TARGET key, never the gate."""
    s = slugify(value)
    if s in company_slugs:
        return "entity:company:%s" % s
    return "tax:manufacturer:%s" % value


def build_graph(site, arts, terms):
    ents = site["entities"]
    uavs = [e for e in ents if e.get("entity_type", "uav") == "uav"]
    company_slugs = {e["slug"] for e in ents if e.get("entity_type") == "company"}
    nodes, edges = set(), set()

    for e in uavs:
        u = "entity:uav:%s" % e["slug"]; nodes.add(u)
        mfr = val(e, "manufacturer")
        if mfr:
            t = manufacturer_target(mfr, company_slugs); nodes.add(t); edges.add((u, t, "manufacturer"))
        ctry = val(e, "manufacturer_country")
        if ctry:
            t = "tax:country:%s" % ctry; nodes.add(t); edges.add((u, t, "country"))
        seg = val(e, "market_segment")
        if seg:
            t = "tax:segment:%s" % seg; nodes.add(t); edges.add((u, t, "segment"))

    for s in company_slugs:               # company nodes (P1; none at P0) — keep the universe honest
        nodes.add("entity:company:%s" % s)
    for t in terms:                       # glossary term nodes (full universe)
        nodes.add("term:%s" % t)
    for a in arts:                        # article nodes + outbound edges
        an = "article:%s" % a["slug"]; nodes.add(an)
        for tg in a.get("entity_tags", []):
            if tg.get("type") == "aircraft" and tg.get("slug"):
                edges.add((an, "entity:uav:%s" % tg["slug"], "tag"))
        for term in a.get("glossary", []):
            edges.add((an, "term:%s" % term, "glossary"))
    return nodes, edges


def node_class(n):
    p = n.split(":")
    return p[0] + ":" + p[1] if p[0] in ("entity", "tax") else p[0]


def main():
    site = json.loads(SITE.read_bytes())
    arts = json.loads(ARTS.read_bytes())["articles"]
    terms = json.loads(GLOSS.read_bytes())["terms"]
    nodes, edges = build_graph(site, arts, terms)
    graph = {
        "schema": "graph/1",
        "stats": {
            "nodes": len(nodes), "edges": len(edges),
            "by_node": dict(sorted(Counter(node_class(n) for n in nodes).items())),
            "by_edge": dict(sorted(Counter(k for _, _, k in edges).items())),
        },
        "nodes": sorted(nodes),
        "edges": [list(e) for e in sorted(edges)],
    }
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n")
    print("graph.json: %d nodes · %d edges | edges %s"
          % (len(nodes), len(edges), graph["stats"]["by_edge"]))


if __name__ == "__main__":
    main()
