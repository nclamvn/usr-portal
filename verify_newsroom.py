#!/usr/bin/env python3
"""TIP-P3.3 — newsroom gate (mode E). Independent checks over content/newsroom/*.md, fail-loud exit 2:
  · CONTENT_FIGURE_DRIFT  — a declared figure's trace recompute is absent from the body.
  · OPINION_REQUIRES_HUMAN_AUTHOR — a non-AI-authorable type (opinion/analysis/…) with no human_author.
  · DANGLING_TAG          — an entity_tag 'type:slug' doesn't resolve to a real node.
  · FORMAT_VIOLATION      — em-dash, comma-before-'và', or a bullet line in prose.
  · SAMPLE_DISCLOSURE_MISSING — a data-report stating a distribution with no sample-disclosure sentence.
  · SOURCE_MISSING        — no sourced provenance (sources empty / missing tier).
Usage: python3 verify_newsroom.py [file.md]."""
import json, sys, re, pathlib
import yaml
from build_newsroom import trace_value, AI_TYPES, tslug

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "content" / "newsroom"
SITE = ROOT / "out" / "site-data.json"
GLOSS = ROOT / "content" / "glossary.json"


def parse(md):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", md, re.S)
    return yaml.safe_load(m.group(1)), m.group(2)


def check(path, site, comp, uav, terms, fails):
    fm, body = parse(path.read_text())
    sid = path.stem
    typ = fm.get("type")
    # 1) figure drift — every declared figure's live value must appear in the prose, on a NUMBER
    #    boundary (not as a substring of a larger number: "6" must not pass via "267"). Digit/dot/comma
    #    on either side of the value disqualifies the match.
    for fig in fm.get("figures") or []:
        try:
            v = trace_value(fig["trace"], site)
        except Exception as e:
            fails.append("CONTENT_FIGURE_DRIFT: %s token %s not traceable (%s)" % (sid, fig.get("token"), e)); continue
        if not re.search(r"(?<![\d.,])" + re.escape(str(v)) + r"(?![\d.,])", body):
            fails.append("CONTENT_FIGURE_DRIFT: %s token %s = %s not present in body" % (sid, fig.get("token"), v))
    # 2) opinion needs a human author
    if typ not in AI_TYPES and not fm.get("human_author"):
        fails.append("OPINION_REQUIRES_HUMAN_AUTHOR: %s type=%s has no human_author" % (sid, typ))
    # 3) dangling tags
    for tag in fm.get("entity_tags") or []:
        t, _, s = tag.partition(":")
        ok = (t == "company" and s in comp) or (t == "uav" and s in uav) or (t == "knowledge" and s in terms)
        if not ok:
            fails.append("DANGLING_TAG: %s tag %r does not resolve" % (sid, tag))
    # 4) format violations (authored prose only)
    if "—" in body:
        fails.append("FORMAT_VIOLATION: %s contains em-dash" % sid)
    if re.search(r",\s+và\b", body):
        fails.append("FORMAT_VIOLATION: %s comma before 'và'" % sid)
    if re.search(r"^\s*[-*•]\s+", body, re.M):
        fails.append("FORMAT_VIOLATION: %s bullet in prose" % sid)
    # 5) data-report disclosure
    if typ == "data-report":
        if not re.search(r"tuyển chọn|không phải thị|không phải thống kê|cấu trúc của (tập|chính)", body):
            fails.append("SAMPLE_DISCLOSURE_MISSING: %s data-report has no sample-disclosure sentence" % sid)
    # 6) sources
    srcs = fm.get("sources") or []
    if not srcs or not all(s.get("tier") for s in srcs):
        fails.append("SOURCE_MISSING: %s has no sourced provenance (tier)" % sid)


def main():
    site = json.loads(SITE.read_bytes())
    comp = {e["slug"] for e in site["entities"] if e.get("entity_type") == "company"}
    uav = {e["slug"] for e in site["entities"] if e.get("entity_type", "uav") == "uav"}
    terms = {tslug(t) for t in json.loads(GLOSS.read_bytes())["terms"]}
    fails = []
    files = [pathlib.Path(sys.argv[1])] if len(sys.argv) > 1 else sorted(SRC.glob("*.md"))
    for f in files:
        check(f, site, comp, uav, terms, fails)
    print("newsroom: %d article(s) checked" % len(files))
    if fails:
        print("\nNEWSROOM GATE FAIL (%d):" % len(fails))
        for f in fails[:25]:
            print("  -", f)
        sys.exit(2)
    print("NEWSROOM GATE PASS: figures trace · authored-only (no opinion w/o author) · tags resolve · format clean · disclosure present · sourced.")


if __name__ == "__main__":
    main()
