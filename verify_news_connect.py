#!/usr/bin/env python3
"""verify_news_connect.py — TIP-NEWS-CONNECT nhịp A gate (fail-loud exit 2).

Two-way binding between aggregation cards (dòng A entity_tags) and entity pages.
  NEWS_TAG_DANGLING   — a card entity_tag 'kind:id' does not resolve to a real entity slug
                        (company/uav) or knowledge term.
  NEWS_TAG_ASYMMETRY  — a card tags entity X but X's page does not list the card, OR an entity page
                        lists a news card that does not tag that entity (an orphan link).

Honest-null holds: a card with no registry subject keeps entity_tags [] and never appears on a page.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CARDS = ROOT / "content" / "news-cards.json"
SITE = ROOT / "out" / "site-data.json"
GLOSS = ROOT / "content" / "glossary.json"
KIND_DIR = {"company": "company", "uav": "uav"}   # tag kinds that render a two-way page section

_NEWSLIST_RE = re.compile(r'<ul class="fleet news-list"[^>]*>(.*?)</ul>', re.S)
_CARDLINK_RE = re.compile(r'news-card/([a-z0-9-]+)\.html')


def load():
    cards = json.loads(CARDS.read_text(encoding="utf-8")).get("cards", [])
    slugs = {e["slug"] for e in json.loads(SITE.read_bytes()).get("entities", [])}
    gloss = set(json.loads(GLOSS.read_bytes()).get("terms", {}).keys())
    return cards, slugs, gloss


def read_pages():
    """{(kind, slug): html} for every entity page whose kind renders a news section."""
    pages = {}
    for kind, d in KIND_DIR.items():
        for p in (ROOT / d).glob("*.html"):
            pages[(kind, p.stem)] = p.read_text()
    return pages


def _linked(html):
    return {m for block in _NEWSLIST_RE.findall(html) for m in _CARDLINK_RE.findall(block)}


def check(cards, slugs, gloss, pages, fails):
    # forward: every tag resolves, and the tagged entity's page lists the card
    for c in cards:
        cid = c.get("id")
        for t in c.get("entity_tags") or []:
            if ":" not in t:
                fails.append(f"NEWS_TAG_DANGLING: card {cid!r} tag {t!r} malformed"); continue
            kind, ident = t.split(":", 1)
            resolved = (ident in gloss) if kind == "knowledge" else (ident in slugs)
            if not resolved:
                fails.append(f"NEWS_TAG_DANGLING: card {cid!r} tag {t!r} does not resolve"); continue
            if kind in KIND_DIR:
                html = pages.get((kind, ident))
                if html is None:
                    fails.append(f"NEWS_TAG_ASYMMETRY: card {cid!r} tags {t!r} but {kind}/{ident}.html missing"); continue
                if cid not in _linked(html):
                    fails.append(f"NEWS_TAG_ASYMMETRY: card {cid!r} tags {t!r} but that page does not list it")
    # backward: every card linked on an entity page tags that entity (no orphan links)
    card_tags = {c["id"]: set(c.get("entity_tags") or []) for c in cards}
    for (kind, slug), html in pages.items():
        for lid in _linked(html):
            if f"{kind}:{slug}" not in card_tags.get(lid, set()):
                fails.append(f"NEWS_TAG_ASYMMETRY: {kind}/{slug}.html lists card {lid!r} that does not tag it")
    return fails


def main():
    cards, slugs, gloss = load()
    fails = []
    check(cards, slugs, gloss, read_pages(), fails)
    if fails:
        print("\nNEWS-CONNECT FAIL:")
        for f in fails[:20]:
            print("  -", f)
        sys.exit(2)
    tagged = sum(1 for c in cards if c.get("entity_tags"))
    links = sum(len(c.get("entity_tags") or []) for c in cards)
    print(f"NEWS-CONNECT PASS: {tagged} card(s) tagged · {links} entity link(s) · all resolve · two-way binding intact.")


if __name__ == "__main__":
    main()
