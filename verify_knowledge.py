#!/usr/bin/env python3
"""TIP-P3.1 — knowledge gate. Independent bijection between glossary TERMS and the rendered term
pages (PRD 'no empty tag'), plus: every in-body glossary auto-link target resolves to a real
knowledge page (no dangling mention). Fail-loud exit 2.
  · KNOWLEDGE_MISSING — a term has no page · KNOWLEDGE_ORPHAN — a page has no term.
  · KNOWLEDGE_DANGLING — an article references a glossary term with no page.
Usage: python3 verify_knowledge.py [knowledge_dir]."""
import json, sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
GLOSS = ROOT / "content" / "glossary.json"
ARTS = ROOT / "content" / "articles.json"
KDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "knowledge"
def tslug(v): return re.sub(r"[^a-z0-9]+", "-", (v or "").lower()).strip("-")


def main():
    terms = json.loads(GLOSS.read_bytes())["terms"]
    arts = json.loads(ARTS.read_bytes())["articles"]
    exp = {tslug(t) for t in terms}
    have = {p.stem for p in KDIR.glob("*.html")} if KDIR.exists() else set()
    fails = []
    for t in sorted(exp - have):
        fails.append("KNOWLEDGE_MISSING: term %r has no page" % t)
    for t in sorted(have - exp):
        fails.append("KNOWLEDGE_ORPHAN: page %r has no term" % t)
    # every article glossary mention must resolve to a real term page
    for a in arts:
        for term in a.get("glossary", []):
            if tslug(term) not in exp:
                fails.append("KNOWLEDGE_DANGLING: article %s references %r with no page" % (a.get("slug"), term))
    print("knowledge: %d term / %d page" % (len(exp), len(have)))
    if fails:
        print("\nKNOWLEDGE GATE FAIL (%d):" % len(fails))
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    print("KNOWLEDGE GATE PASS: every term has one page · no orphan · every mention resolves.")


if __name__ == "__main__":
    main()
