#!/usr/bin/env python3
"""TIP-007/V — content integrity gate (fail-loud, exit 2). Independent of the builders.

Enforces the editorial-intelligence contract on content/articles.json:
  - every analysis has the four-questions filled, ≥1 entity-tag, ≥1 tier-A source;
  - every entity_tag with a slug points at a REAL registry entity (no dangling node);
  - every glossary term used is defined in content/glossary.json;
  - every figure's numbers TRACE to the registry (figure.kind resolves to a live computation;
    content carries NO hardcoded numbers) — the zero-fabrication line for data;
  - style-guide: title has no '!' and no straight double-quote; date is DD/M (no year);
  - sample:true articles render the "nội dung mẫu" banner on their generated page.
"""
import json, pathlib, re, sys
from build_analysis import figure_bars

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out" / "site-data.json"
ARTS = ROOT / "content" / "articles.json"
GLOSS = ROOT / "content" / "glossary.json"

TYPES = {"news", "analysis"}
SECTIONS = {"policy", "market", "tech", "defense", "business", "intl"}
FIG_ALLOWED = {"id", "kind", "caption", "unit"}   # NO numeric keys allowed in content figures
fails = []


def main():
    site = json.loads(SITE.read_bytes())
    glossary = json.loads(GLOSS.read_bytes())["terms"]
    arts = json.loads(ARTS.read_bytes())["articles"]
    entity_slugs = {e["slug"] for e in site["entities"]}

    seen = set()
    n_an = n_news = 0
    for a in arts:
        slug = a.get("slug", "?")
        def bad(msg): fails.append(f"[{slug}] {msg}")

        if slug in seen:
            bad("duplicate slug")
        seen.add(slug)
        if a.get("type") not in TYPES:
            bad(f"bad type {a.get('type')!r}")
        if a.get("section") not in SECTIONS:
            bad(f"bad section {a.get('section')!r}")

        # style-guide
        title = a.get("title", "")
        if "!" in title:
            bad("title contains '!'")
        if '"' in title:
            bad("title contains straight double-quote")
        if not re.match(r"^\d{1,2}/\d{1,2}$", a.get("date", "")):
            bad(f"date {a.get('date')!r} not DD/M (no year)")

        # entity tags -> registry (no dangling)
        for t in a.get("entity_tags", []):
            if t.get("slug") and t["slug"] not in entity_slugs:
                bad(f"entity_tag slug not in registry: {t['slug']}")
        # glossary terms exist
        for term in a.get("glossary", []):
            if term not in glossary:
                bad(f"glossary term undefined: {term}")

        # figures: no hardcoded numbers; kind resolves to a live registry computation
        for fig in a.get("figures", []):
            extra = set(fig) - FIG_ALLOWED
            if extra:
                bad(f"figure {fig.get('id')} has non-allowed keys (hardcoded data?): {extra}")
            try:
                bars, src = figure_bars(fig.get("kind"), site)
                if not bars:
                    bad(f"figure {fig.get('id')} kind '{fig.get('kind')}' produced no registry data")
            except Exception as e:
                bad(f"figure {fig.get('id')} kind '{fig.get('kind')}' not traceable to registry: {e}")

        if a.get("type") == "analysis":
            n_an += 1
            fq = a.get("four_questions", {})
            for k in ("happening", "meaning", "todo", "data"):
                if not (fq.get(k) or "").strip():
                    bad(f"four_questions.{k} empty")
            if not a.get("entity_tags"):
                bad("analysis has no entity_tag")
            if not any(s.get("tier") == "A" for s in a.get("sources", [])):
                bad("analysis has no tier-A source")
            # sample -> generated page must carry the banner
            if a.get("sample"):
                pg = ROOT / "analysis" / f'{slug}.html'
                if pg.exists() and "Nội dung là chữ mẫu" not in pg.read_text():
                    bad("sample article missing 'nội dung mẫu' banner on page")
        else:
            n_news += 1
            if a.get("sample"):
                pg = ROOT / "news" / f'{slug}.html'
                if pg.exists() and "Nội dung là chữ mẫu" not in pg.read_text():
                    bad("sample article missing 'nội dung mẫu' banner on page")

    print(f"articles: {len(arts)} ({n_an} analysis, {n_news} news) | entity slugs: {len(entity_slugs)}")
    if fails:
        print("\nCONTENT FAIL:")
        for f in fails:
            print("  -", f)
        sys.exit(2)
    print("CONTENT PASS: four-questions filled · entity-tags resolve · tier-A present · "
          "figures trace to registry · style-guide clean · sample banners present.")


if __name__ == "__main__":
    main()
