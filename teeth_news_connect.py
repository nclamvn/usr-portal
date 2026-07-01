#!/usr/bin/env python3
"""Teeth for verify_news_connect — prove both gates BITE. Tamper cards/pages in memory, run the
shared check, assert the matching gate fires; then prove the clean state passes."""
import copy, re
import verify_news_connect as V

cards, slugs, gloss = V.load()
pages = V.read_pages()
ok = True


def run(name, cards_, pages_, want):
    global ok
    fails = []
    V.check(cards_, slugs, gloss, pages_, fails)
    bit = any(f.startswith(want) for f in fails)
    ok = ok and bit
    print(f"{name:28s} : {'CẮN ✓' if bit else 'KHÔNG CẮN ✗ ' + str(fails[:1])}")


# clean positive control
fc = []
V.check(cards, slugs, gloss, pages, fc)
print(f"{'CLEAN':28s} : {'PASS' if not fc else '!! ' + str(fc[:2])}")
ok = ok and not fc

# pick a real tagged card + its company page for the tamper cases
sample = next(c for c in cards if any(t.startswith("company:") for t in (c.get("entity_tags") or [])))
sample_tag = next(t for t in sample["entity_tags"] if t.startswith("company:"))
sample_slug = sample_tag.split(":", 1)[1]

# (a) NEWS_TAG_DANGLING — inject a tag to a non-existent entity
cd = copy.deepcopy(cards)
cd[0]["entity_tags"] = (cd[0].get("entity_tags") or []) + ["company:ghost-nowhere-zzz"]
run("NEWS_TAG_DANGLING", cd, pages, "NEWS_TAG_DANGLING")

# (b) ASYMMETRY forward — remove the card's link from the entity page it tags
pf = dict(pages)
pf[("company", sample_slug)] = re.sub(rf'news-card/{re.escape(sample["id"])}\.html', 'news-card/removed.html',
                                      pages[("company", sample_slug)])
run("NEWS_TAG_ASYMMETRY/forward", cards, pf, "NEWS_TAG_ASYMMETRY")

# (c) ASYMMETRY backward — inject an orphan card link (a card that does NOT tag this entity)
orphan = next(c["id"] for c in cards if sample_tag not in (c.get("entity_tags") or []))
pb = dict(pages)
html = pages[("company", sample_slug)]
if 'news-list' in html:
    pb[("company", sample_slug)] = re.sub(r'(<ul class="fleet news-list"[^>]*>)',
                                          rf'\1<li><a href="../news-card/{orphan}.html">x</a></li>', html, count=1)
else:  # entity has no news-list yet: synthesize one to prove the orphan path
    pb[("company", sample_slug)] = html + f'<ul class="fleet news-list"><li><a href="../news-card/{orphan}.html">x</a></li></ul>'
run("NEWS_TAG_ASYMMETRY/backward", cards, pb, "NEWS_TAG_ASYMMETRY")

print("NEWS-CONNECT TEETH:", "TẤT CẢ RĂNG CẮN ✓" if ok else "CÓ RĂNG KHÔNG CẮN ✗")
raise SystemExit(0 if ok else 2)
