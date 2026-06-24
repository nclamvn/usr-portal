#!/usr/bin/env bash
# TIP-005/E — one-command reproducible build + full gate.
# site-data -> data-integrity -> reference -> index -> i18n -> reduced-motion -> headless audit.
# Fail-loud: set -e + every gate exits non-zero on failure. Idempotent site-data checked by sha.
set -euo pipefail
cd "$(dirname "$0")"
PORT=8011

echo "[1/8] site-data (TIP-002)"
python3 build_site_data.py
SHA1=$(shasum -a256 out/site-data.json | cut -d' ' -f1)
python3 build_site_data.py >/dev/null
SHA2=$(shasum -a256 out/site-data.json | cut -d' ' -f1)
[ "$SHA1" = "$SHA2" ] && echo "      idempotent OK ($SHA1)" || { echo "      IDEMPOTENT FAIL"; exit 2; }

echo "[2/8] data integrity (verify_site_data — schema/2 type-aware · honest-null · aggregates-live)"
python3 verify_site_data.py out/master_registry.json out/site-data.json

echo "[2b/8] schema/2 teeth (entity_type · per-type required · invariant #10 disputed-keep-all)"
python3 teeth_p0.py

echo "[2c/8] company teeth (P1.1 — rollup two-way · sourced-attr shape · #10 on company)"
python3 teeth_p11.py

echo "[3/8] reference index rows (TIP-003) + detail pages (TIP-006) + company pages (TIP-P1.1)"
python3 build_reference.py
python3 build_detail.py
python3 build_company.py
python3 build_taxonomy.py
echo "[4/8] newsroom + analysis pillar (TIP-007)"
python3 build_news.py
python3 build_analysis.py
echo "[5/8] index home (TIP-004) + compare (TIP-P1.3) + single-file bundle export (TIP-008)"
python3 build_index.py
python3 build_compare.py
CSHA1=$(shasum -a256 out/compare-data.json | cut -d' ' -f1)
python3 build_compare.py >/dev/null
CSHA2=$(shasum -a256 out/compare-data.json | cut -d' ' -f1)
[ "$CSHA1" = "$CSHA2" ] && echo "      compare-data idempotent OK" || { echo "      COMPARE IDEMPOTENT FAIL"; exit 2; }
python3 build_search.py
XSHA1=$(shasum -a256 out/search-index.json | cut -d' ' -f1)
python3 build_search.py >/dev/null
XSHA2=$(shasum -a256 out/search-index.json | cut -d' ' -f1)
[ "$XSHA1" = "$XSHA2" ] && echo "      search-index idempotent OK" || { echo "      SEARCH IDEMPOTENT FAIL"; exit 2; }
python3 build_data.py
DSHA1=$(shasum -a256 out/data-overview.json | cut -d' ' -f1)
python3 build_data.py >/dev/null
DSHA2=$(shasum -a256 out/data-overview.json | cut -d' ' -f1)
[ "$DSHA1" = "$DSHA2" ] && echo "      data-overview idempotent OK" || { echo "      DATA IDEMPOTENT FAIL"; exit 2; }
python3 build_bundle.py
echo "[6/8] content integrity (verify_content — 4-questions · entity-tags · tier-A · figures trace registry)"
python3 verify_content.py

echo "[6b/8] cross-link graph (crosslink.py) + dangling-link gate (verify_graph) + teeth"
python3 crosslink.py
GSHA1=$(shasum -a256 out/graph.json | cut -d' ' -f1)
python3 crosslink.py >/dev/null
GSHA2=$(shasum -a256 out/graph.json | cut -d' ' -f1)
[ "$GSHA1" = "$GSHA2" ] && echo "      graph idempotent OK ($GSHA1)" || { echo "      GRAPH IDEMPOTENT FAIL"; exit 2; }
python3 verify_graph.py
python3 teeth_p02.py
python3 verify_taxonomy.py
python3 teeth_p14.py
python3 verify_compare.py
python3 teeth_p13.py
python3 verify_search.py
python3 teeth_p21.py
python3 verify_data.py
python3 teeth_p23.py
echo "[7a/8] i18n completeness"
python3 check_i18n.py

echo "[7b/8] reduced-motion + focus (static)"
grep -q "prefers-reduced-motion" base/design-system.css \
  && grep -q "opacity: 1 !important" base/design-system.css \
  && grep -q "focus-visible" base/design-system.css \
  && echo "      reduced-motion kills anim + keeps content; focus-visible present" \
  || { echo "      REDUCED-MOTION/FOCUS FAIL"; exit 2; }

echo "[8/8] headless designer-audit (base + hero + filtered + detail + editorial + teeth)"
pkill -f "http.server $PORT" 2>/dev/null || true
sleep 0.3
python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/ba_server.log 2>&1 &
SRV=$!
sleep 1
set +e
node audit_headless.js
AUDIT=$?
kill "$SRV" 2>/dev/null
set -e
[ "$AUDIT" -eq 0 ] || { echo "      AUDIT FAILED (exit $AUDIT)"; exit "$AUDIT"; }

echo "build_all: OK"
