#!/usr/bin/env python3
"""TIP-P02 — frame-glyph factory. Schematic SVG of the AIRFRAME TYPE (a diagram of the *class* of
frame), never a render of a specific model. Geometry ported from visual-language-specimen.html and
extended per DECISION D-1.

Zero-fab rule baked in: a glyph commits ONLY to what the data asserts.
  - octocopter asserts 8 rotors -> draw 8 (fidelity).
  - 'multirotor' is generic (no rotor count) -> the multirotor glyph draws a dashed sweep + hub,
    NO discrete rotor arms/discs. (Mapping multirotor->quad would invent a 4-rotor claim — forbidden.)
  - unknown / unmapped -> neutral dashed ring + '?', never a guessed frame.
"""
import math, re

ALLOWED = {"quad", "hexa", "octo", "multirotor", "fixed", "vtol", "heli", "ducted", "unknown"}


def _poly(cx, cy, r, n, rot):
    return [(cx + r * math.cos(rot + i * 2 * math.pi / n),
             cy + r * math.sin(rot + i * 2 * math.pi / n)) for i in range(n)]


def _rotor_arms(cx, cy, n, arm, disc, rot):
    """n discrete arms + rotor discs — used ONLY where the data states the rotor count."""
    s = ""
    for x, y in _poly(cx, cy, arm, n, rot):
        s += f'<line class="bp-line" x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>'
        s += f'<circle class="bp-disc" cx="{x:.1f}" cy="{y:.1f}" r="{disc}"/>'
    s += f'<circle class="bp-line" cx="{cx}" cy="{cy}" r="6"/>'
    return s


def _inner(kind):
    if kind == "quad":
        return _rotor_arms(50, 50, 4, 30, 13, math.pi / 4)
    if kind == "hexa":
        return _rotor_arms(50, 50, 6, 32, 10, -math.pi / 2)
    if kind == "octo":
        return _rotor_arms(50, 50, 8, 33, 7, -math.pi / 2)
    if kind == "multirotor":
        # generic rotorcraft — count UNSPECIFIED: dashed sweep rings + hub, NO discrete rotors
        return ('<circle class="bp-faintl" cx="50" cy="50" r="33"/>'
                '<circle class="bp-faintl" cx="50" cy="50" r="20"/>'
                '<circle class="bp-line" cx="50" cy="50" r="7"/>')
    if kind == "fixed":
        return ('<path class="bp-line" d="M50 16 C46 16 44 22 44 34 L44 64 C44 76 46 84 50 84 C54 84 56 76 56 64 L56 34 C56 22 54 16 50 16Z"/>'
                '<path class="bp-line" d="M8 48 C26 44 40 43 50 43 C60 43 74 44 92 48 C74 51 60 52 50 52 C40 52 26 51 8 48Z"/>'
                '<path class="bp-line" d="M34 78 C42 76 46 76 50 76 C54 76 58 76 66 78 C58 80 54 80 50 80 C46 80 42 80 34 78Z"/>'
                '<circle class="bp-disc" cx="50" cy="20" r="2.4"/>')
    if kind == "vtol":
        return ('<path class="bp-line" d="M50 20 C47 20 45 26 45 36 L45 62 C45 72 47 78 50 78 C53 78 55 72 55 62 L55 36 C55 26 53 20 50 20Z"/>'
                '<path class="bp-line" d="M12 46 C28 43 40 42 50 42 C60 42 72 43 88 46 C72 49 60 50 50 50 C40 50 28 49 12 46Z"/>'
                '<line class="bp-line" x1="30" y1="30" x2="30" y2="70"/><line class="bp-line" x1="70" y1="30" x2="70" y2="70"/>'
                '<circle class="bp-disc" cx="30" cy="30" r="8"/><circle class="bp-disc" cx="30" cy="70" r="8"/>'
                '<circle class="bp-disc" cx="70" cy="30" r="8"/><circle class="bp-disc" cx="70" cy="70" r="8"/>')
    if kind == "heli":
        return ('<circle class="bp-faintl" cx="50" cy="44" r="30"/>'
                '<path class="bp-line" d="M50 28 C45 28 43 34 43 46 L43 66 C43 72 46 74 50 74 C54 74 57 72 57 66 L57 46 C57 34 55 28 50 28Z"/>'
                '<line class="bp-line" x1="50" y1="72" x2="50" y2="90"/><line class="bp-line" x1="44" y1="90" x2="56" y2="90"/>'
                '<circle class="bp-line" cx="50" cy="44" r="4"/>')
    if kind == "ducted":
        return ('<circle class="bp-line" cx="50" cy="50" r="32"/><circle class="bp-line" cx="50" cy="50" r="24" opacity=".55"/>'
                '<line class="bp-line" x1="18" y1="50" x2="82" y2="50"/><line class="bp-line" x1="50" y1="18" x2="50" y2="82"/>'
                '<circle class="bp-line" cx="50" cy="50" r="7"/>')
    # unknown / unmapped — neutral, never a guessed frame
    return ('<circle class="bp-faintl" cx="50" cy="50" r="26"/>'
            '<text x="50" y="58" text-anchor="middle" font-family="IBM Plex Mono" font-size="22">?</text>')


def glyph_svg(kind, size="glyph-sm", draw=False):
    """Inline <svg> for the frame kind at a size class. draw=True marks strokes [data-draw] so the
    large detail glyph self-draws (the page must run initDraw+initReveal; no-JS/.reduced-motion ->
    solid via the .js gate). Unmapped -> unknown."""
    k = kind if kind in ALLOWED else "unknown"
    inner = _inner(k)
    if draw:
        inner = re.sub(r'<(line|circle|path)\b', r'<\1 data-draw', inner)   # not <text>
    extra = " glyph-unknown" if k == "unknown" else ""
    # fill="none" on the ROOT (presentation attr) — every shape is line-art; CSS rules for
    # text/filled accents still win over this (CSS > presentation attr). Makes the glyph robust
    # to CSS-not-loading / <use>+shadow-tree (TIP-UX2.1 SVG-fill rule, no default-black).
    return (f'<svg class="glyph-svg {size}{extra}" viewBox="0 0 100 100" fill="none" '
            f'aria-hidden="true" data-glyph="{k}">{inner}</svg>')
