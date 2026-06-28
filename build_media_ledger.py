#!/usr/bin/env python3
"""TIP-NEWS-VISUAL — media staging ledger. Provenance as an ASSET, not a wall: scan every displayed
image across the site (media.json assets · newsroom .md `image:` frontmatter · news-cards.json) and
emit out/media-ledger.json — one row per image with source / tier / credit / license_status. This is
the bridge between code and the owner's out-of-band licensing work: the license team reads the ledger
to see what is `pending` (needs a license) vs `cc`/`owned`/`licensed`. When a license lands they flip
license_status in the source manifest — no code change, no rebuild logic ("không làm lại").

Completeness gate (fail-loud exit 2):
  · LEDGER_STATUS_MISSING  — a displayed image has no license_status (must be in the ledger).
  · LEDGER_CREDIT_MISSING  — a non-owned image (cc/pending/licensed) is shown without a credit.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
MEDIA = ROOT / "content" / "media.json"
CARDS = ROOT / "content" / "news-cards.json"
NEWSROOM = ROOT / "content" / "newsroom"
OUT = ROOT / "out" / "media-ledger.json"

VALID = {"owned", "cc", "licensed", "pending"}
FM = re.compile(r"^---\n(.*?)\n---\n", re.S)


def _fm(md):
    import yaml
    m = FM.match(md)
    return yaml.safe_load(m.group(1)) if m else {}


def _status_for_local(src):
    """A local committed image: open/ = cc, everything else under images/content = owned (RtR)."""
    return "cc" if "/images/content/open/" in src else "owned"


def collect():
    rows = []
    # 1) media.json assets — carry an explicit license_status
    m = json.loads(MEDIA.read_bytes())
    for aid, a in m["assets"].items():
        rows.append({
            "ref": f"asset:{aid}", "where": "media.json",
            "src": a.get("src"), "source": a.get("source"), "source_url": None,
            "tier": a.get("identity_tier"), "credit": a.get("credit"),
            "license_status": a.get("license_status"),
            "owned": a.get("license_status") == "owned" or a.get("rights", "").startswith("rtr_"),
        })
    # 2) newsroom .md `image:` frontmatter — http src = third-party (pending), local = cc/owned by path
    for p in sorted(NEWSROOM.glob("*.md")):
        img = (_fm(p.read_text(encoding="utf-8")) or {}).get("image")
        if not isinstance(img, dict) or not img.get("src"):
            continue
        src = img["src"]
        http = src.startswith("http")
        status = img.get("license_status") or ("pending" if http else _status_for_local(src))
        rows.append({
            "ref": f"newsroom:{p.stem}", "where": f"content/newsroom/{p.name}",
            "src": src, "source": img.get("source"), "source_url": img.get("source_url") or (src if http else None),
            "tier": img.get("tier"), "credit": img.get("credit"),
            "license_status": status, "owned": status == "owned",
        })
    # 3) news-cards.json images — all local open-licensed (cc)
    for c in json.loads(CARDS.read_bytes()).get("cards", []):
        if not c.get("image"):
            continue
        rows.append({
            "ref": f"card:{c['id']}", "where": "content/news-cards.json",
            "src": c["image"], "source": c.get("outlet"), "source_url": c.get("source_url"),
            "tier": c.get("tier"), "credit": c.get("image_credit"),
            "license_status": _status_for_local(c["image"]), "owned": "/open/" not in c["image"],
        })
    return rows


def main():
    rows = collect()
    fails = []
    for r in rows:
        st = r.get("license_status")
        if st not in VALID:
            fails.append(f"LEDGER_STATUS_MISSING: {r['ref']} ({r['where']}) status={st!r} not in {sorted(VALID)}")
        if not r.get("owned") and not r.get("credit"):
            fails.append(f"LEDGER_CREDIT_MISSING: {r['ref']} ({r['where']}) non-owned image shown without credit")
    from collections import Counter
    by_status = dict(Counter(r["license_status"] for r in rows))
    ledger = {
        "schema": "media-ledger/1",
        "total": len(rows),
        "by_status": by_status,
        "to_license": [r for r in rows if r["license_status"] == "pending"],
        "entries": sorted(rows, key=lambda r: (r["license_status"], r["ref"])),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"media-ledger.json: {len(rows)} images · {by_status} · {len(ledger['to_license'])} pending (to license)")
    if fails:
        print("\nMEDIA LEDGER GATE FAIL:")
        for f in fails[:25]:
            print("  -", f)
        sys.exit(2)
    print("MEDIA LEDGER PASS: every displayed image has a license_status · non-owned images carry credit.")


if __name__ == "__main__":
    main()
