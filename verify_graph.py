#!/usr/bin/env python3
"""TIP-P0.2 — INDEPENDENT dangling-link gate. Does NOT trust crosslink.py: it re-derives the
authoritative node universe + expected edges straight from the sources (site-data/2 + glossary +
articles), then checks graph.json against them:
  · DANGLING_LINK — any edge whose src/dst is not a real node (incl. empty taxonomy target).
  · GRAPH_STALE   — graph.json nodes/edges != live re-derivation (hardcoded or out of date).
Fail-loud exit 2. Usage: python3 verify_graph.py [graph.json]  (default out/graph.json)."""
import json, sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
GLOSS = ROOT / "content" / "glossary.json"
GRAPH = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "graph.json"

EMPTY_TARGETS = {"tax:manufacturer:", "tax:country:", "tax:segment:", "entity:uav:", "term:"}


def slugify(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
def val(e, f): return (e.get(f) or {}).get("value")


def derive(site, arts, terms):
    """Independent restatement of the contract (mirrors crosslink, by design — drift => gate fails)."""
    ents = site["entities"]
    uavs = [e for e in ents if e.get("entity_type", "uav") == "uav"]
    cslug = {e["slug"] for e in ents if e.get("entity_type") == "company"}
    nodes, edges = set(), set()

    def mtgt(v):
        s = slugify(v)
        return ("entity:company:%s" % s) if s in cslug else ("tax:manufacturer:%s" % v)

    for e in uavs:
        u = "entity:uav:%s" % e["slug"]; nodes.add(u)
        if val(e, "manufacturer"):
            t = mtgt(val(e, "manufacturer")); nodes.add(t); edges.add((u, t, "manufacturer"))
        if val(e, "manufacturer_country"):
            t = "tax:country:%s" % val(e, "manufacturer_country"); nodes.add(t); edges.add((u, t, "country"))
        if val(e, "market_segment"):
            t = "tax:segment:%s" % val(e, "market_segment"); nodes.add(t); edges.add((u, t, "segment"))
    for s in cslug:
        nodes.add("entity:company:%s" % s)
    for t in terms:
        nodes.add("term:%s" % t)
    for a in arts:
        an = "article:%s" % a["slug"]; nodes.add(an)
        for tg in a.get("entity_tags", []):
            if tg.get("type") == "aircraft" and tg.get("slug"):
                edges.add((an, "entity:uav:%s" % tg["slug"], "tag"))
        for term in a.get("glossary", []):
            edges.add((an, "term:%s" % term, "glossary"))
    return nodes, edges


def main():
    graph = json.loads(GRAPH.read_bytes())
    site = json.loads(SITE.read_bytes())
    arts = json.loads(ARTS.read_bytes())["articles"]
    terms = json.loads(GLOSS.read_bytes())["terms"]
    exp_nodes, exp_edges = derive(site, arts, terms)

    g_nodes = set(graph.get("nodes", []))
    g_edges = {tuple(x) for x in graph.get("edges", [])}
    fails = []

    # 1) DANGLING — every edge endpoint must be a real node in the independent universe
    for (s, d, k) in g_edges:
        if d in EMPTY_TARGETS or d.endswith(":"):
            fails.append("DANGLING_LINK: empty target on edge %s -%s-> %s" % (s, k, d))
        elif d not in exp_nodes:
            fails.append("DANGLING_LINK: dst %r not a real node (%s -%s-> %s)" % (d, s, k, d))
        if s not in exp_nodes:
            fails.append("DANGLING_LINK: src %r not a real node (%s -%s-> %s)" % (s, s, k, d))

    # 2) GRAPH_STALE — graph.json must equal the live re-derivation (not hardcoded / not stale)
    if g_nodes != exp_nodes:
        miss, extra = exp_nodes - g_nodes, g_nodes - exp_nodes
        fails.append("GRAPH_STALE nodes: missing %d extra %d (e.g. %s)"
                     % (len(miss), len(extra), (sorted(miss) or sorted(extra))[:1]))
    if g_edges != exp_edges:
        fails.append("GRAPH_STALE edges: graph %d != live %d" % (len(g_edges), len(exp_edges)))

    dangling = sum(1 for f in fails if f.startswith("DANGLING"))
    print("graph: %d nodes · %d edges | dangling=%d | by_edge %s"
          % (len(g_nodes), len(g_edges), dangling,
             {k: sum(1 for _, _, kk in g_edges if kk == k) for k in sorted({kk for _, _, kk in g_edges})}))
    if fails:
        print("\nGRAPH GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("GRAPH GATE PASS: every edge resolves to a real node · graph is live (== source re-derivation) · 0 dangling.")


if __name__ == "__main__":
    main()
