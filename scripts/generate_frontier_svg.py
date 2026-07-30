#!/usr/bin/env python3
"""Generate docs/frontier.svg: the published depth-count Pareto frontier for
AES MixColumns vs this project's circuits. Pure stdlib; the data below is the
single source, and every point in it is sourced:

  - published points and the off-frontier Sun-Yang-Li point: PRIOR_ART.md
    (99@3 Shi-Feng-Xu ToSC 2023; 97@4 and 94@5 Osvik-Canright ePrint 2024/1076;
    92@6 Maximov; 88@7 Jean ePrint 2026/1481; 89 Sun-Yang-Li ePrint 2025/1493).
    NEITHER Jean NOR Sun-Yang-Li states a depth: the 7 and the 9 are both this
    project's measurements of its own transcriptions, and the <desc> attributes
    them symmetrically.
  - this project's circuits: bounds.json (97@3, 92@4, 89@5, 88@5, 88@6, 88@7,
    88@8).
  - TWO frontier lines are drawn, because two are true. Solid blue is the
    frontier reachable with no imported material: 97@3, 92@4, 89@5, 88@6.
    Dashed blue extends it to the combined frontier 97@3, 92@4, 88@5, whose
    depth-5 point is derived work.
  - 88 is NOT a new count record; Jean holds it and has priority. The 88@6 is
    drawn as a frontier point because it improves the depth-count frontier
    (one level shallower than Jean's 88 at the same count, four gates below
    Maximov's published depth-6 92), not because 88 is new.
  - the depth-7 point is a TIE: our 88@7 matches Jean's published 88@7 with an
    independent circuit (61/88 shared masks); it does not beat it, so it is
    drawn as one half-grey half-blue marker rather than as an improvement. It is
    now dominated by our own 88@6 and so is off our frontier.
  - hollow blue = ours but derived from published work (its seed chain passes
    through Jean's circuit): the 88@5, and the 88@8, which is also dominated.
  - the three crosses (98@3, 91@6, 89@10) are this project's superseded v1
    results, carried over unchanged from the earlier figure.
"""

from pathlib import Path

# ---- geometry (unchanged from the earlier figure) --------------------------
W, H = 670, 390
XL, XR, YT, YB = 70, 630, 30, 330                        # plot box
DMIN, DMAX = 3, 10                                       # depth axis
GMIN, GMAX = 86, 100                                     # gate axis
BLUE, GREY, FAINT = "#1f6feb", "#888888", "#bbbbbb"

# (depth, gates, label, dx, dy, anchor)
PUBLISHED = [(3, 99, "99 SFX23", 9, -8, "start"),
             (4, 97, "97 OC24", 9, -8, "start"),
             (5, 94, "94 OC24", 9, -8, "start"),
             (6, 92, "92 Max19", 9, -8, "start"),
             # depth 7 is our own measurement of our transcription -- Jean's
             # note states no depth either (same caveat as SYL25 below)
             (7, 88, "88 Jean26", 9, -22, "start")]
# published but dominated by 88 @ depth 7, so not a frontier point; the depth is
# our own measurement of our transcription -- the paper states none
PUBLISHED_OFF = [(9, 89, "89 SYL25", 9, -9, "start")]
# our own-lineage frontier: (depth, gates, label, dx, dy, anchor)
OURS = [(3, 97, "97", 11, 15, "start"),
        (4, 92, "92", -10, 4, "end"),
        (5, 89, "89", 8, -8, "start"),
        (6, 88, "88", 9, -8, "start")]
TIE = (7, 88)                                            # ours == the published point
# ours, but derived from published work (seed chain through Jean's 88)
OURS_DERIVED = [(5, 88, "88 derived", 0, 19, "middle"),
                (8, 88, "88 @ 8 derived", 0, 19, "middle")]
COMBINED_EXTRA = [(4, 92), (5, 88)]                      # dashed: frontier with derived material
SUPERSEDED = [(3, 98), (6, 91), (10, 89)]                # this project's v1 points


def x(d):
    return XL + (d - DMIN) * (XR - XL) / (DMAX - DMIN)


def y(g):
    return YB - (g - GMIN) * (YB - YT) / (GMAX - GMIN)


def dot(e, cx, cy, r, fill):
    e.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>')


def cross(e, cx, cy, r=5):
    e.append(f'<path d="M{cx-r:.1f} {cy-r:.1f} L{cx+r:.1f} {cy+r:.1f} '
             f'M{cx-r:.1f} {cy+r:.1f} L{cx+r:.1f} {cy-r:.1f}" '
             f'stroke="{FAINT}" stroke-width="2"/>')


def half_dot(e, cx, cy, r=6):
    """Left half published-grey, right half this-work-blue: the same point was
    reached independently by both, with different circuits."""
    e.append(f'<path d="M{cx:.1f} {cy-r:.1f} A{r} {r} 0 0 0 {cx:.1f} {cy+r:.1f} Z" fill="{GREY}"/>')
    e.append(f'<path d="M{cx:.1f} {cy-r:.1f} A{r} {r} 0 0 1 {cx:.1f} {cy+r:.1f} Z" fill="{BLUE}"/>')
    e.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="#444444" stroke-width="0.8"/>')


def label(e, cx, cy, dx, dy, text, fill, anchor="start", size=None, weight=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    s = f' font-size="{size}"' if size else ""
    w = ' font-weight="bold"' if weight else ""
    e.append(f'<text x="{cx+dx:.1f}" y="{cy+dy:.1f}"{a}{s}{w} fill="{fill}">{text}</text>')


def main():
    e = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family="Helvetica,Arial,sans-serif" font-size="13" '
         f'role="img" aria-labelledby="ftitle fdesc">',
         '<title id="ftitle">AES MixColumns: the published depth-count Pareto '
         'frontier versus this work</title>',
         '<desc id="fdesc">Scatter plot, 2-input XOR gate count against circuit '
         'depth. The published frontier (dashed grey) runs 99 gates at depth 3 '
         '(Shi-Feng-Xu 2023), 97 at depth 4 and 94 at depth 5 (Osvik-Canright '
         '2024), 92 at depth 6 (Maximov) and 88 at depth 7 (Jean, ePrint '
         '2026/1481; that paper states no depth either, so the 7 is likewise '
         'this project\'s own measurement of its transcription). Two frontier '
         'lines are drawn for this work. Solid blue is what no imported '
         'material touches: 97 gates at depth 3, 92 at depth 4, 89 at depth 5 '
         'and 88 at depth 6. Dashed blue extends it to the combined frontier '
         '97 at depth 3, 92 at depth 4 and 88 at depth 5, whose depth-5 point '
         'is derived work and is drawn hollow. 88 is not a new gate count: Jean '
         'published it first and has priority. What the 88 at depth 6 improves '
         'is the depth-count frontier - one level shallower than Jean\'s 88 at '
         'the same count, and four gates below Maximov\'s published depth-6 92. '
         'The depth-7 point is drawn as a half-grey half-blue marker because '
         'our 88 there ties the published 88 with an independent circuit (61 of '
         '88 masks shared) rather than beating it; it is now dominated by our '
         'own 88 at depth 6. A second hollow blue marker shows our 88 at depth '
         '8, also derived from Jean\'s circuit and also dominated. A hollow '
         'grey marker shows the published Sun-Yang-Li 89 (ePrint 2025/1493), '
         'off the frontier; that paper states no depth, so it is placed at '
         'depth 9, this project\'s own measurement of its transcription. '
         'Crosses mark this project\'s superseded earlier results.</desc>',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>']

    # gridlines + axis ticks
    for g in range(GMIN, GMAX + 1, 2):
        gy = y(g)
        e.append(f'<line x1="{XL}" y1="{gy:.1f}" x2="{XR}" y2="{gy:.1f}" stroke="#dddddd" stroke-width="1"/>')
        e.append(f'<text x="{XL-8}" y="{gy+4:.1f}" text-anchor="end" fill="#555555">{g}</text>')
    for d in range(DMIN, DMAX + 1):
        gx = x(d)
        e.append(f'<line x1="{gx:.1f}" y1="{YT}" x2="{gx:.1f}" y2="{YB}" stroke="#eeeeee" stroke-width="1"/>')
        e.append(f'<text x="{gx:.1f}" y="{YB+20}" text-anchor="middle" fill="#555555">{d}</text>')
    e.append(f'<rect x="{XL}" y="{YT}" width="{XR-XL}" height="{YB-YT}" fill="none" stroke="#999999"/>')
    e.append(f'<text x="{(XL+XR)//2}" y="{YB+45}" text-anchor="middle" fill="#333333">circuit depth</text>')
    e.append(f'<text x="18" y="180" text-anchor="middle" fill="#333333" '
             f'transform="rotate(-90 18 180)">2-input XOR gates</text>')

    # published frontier
    pts = " ".join(f"{x(d):.1f},{y(g):.1f}" for d, g, *_ in PUBLISHED)
    e.append(f'<polyline points="{pts}" fill="none" stroke="{GREY}" stroke-width="2.5" stroke-dasharray="6,4"/>')
    for d, g, txt, dx, dy, anch in PUBLISHED:
        if (d, g) != TIE:
            dot(e, x(d), y(g), 5, GREY)
        label(e, x(d), y(g), dx, dy, txt, "#666666", anch)

    # published but off the frontier (dominated by 88 @ depth 7)
    for d, g, txt, dx, dy, anch in PUBLISHED_OFF:
        e.append(f'<circle cx="{x(d):.1f}" cy="{y(g):.1f}" r="5.5" fill="#ffffff" '
                 f'stroke="{GREY}" stroke-width="2"/>')
        label(e, x(d), y(g), dx, dy, txt, "#666666", anch, size=12)

    # this project's superseded earlier results
    for d, g in SUPERSEDED:
        cross(e, x(d), y(g))

    # this work: the frontier reachable with no imported material
    pts = " ".join(f"{x(d):.1f},{y(g):.1f}" for d, g, *_ in OURS)
    e.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
    # ... and its extension once derived material is allowed (combined frontier)
    pts = " ".join(f"{x(d):.1f},{y(g):.1f}" for d, g in COMBINED_EXTRA)
    e.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="2" '
             f'stroke-dasharray="5,4"/>')
    for d, g, txt, dx, dy, anch in OURS:
        dot(e, x(d), y(g), 6, BLUE)
        label(e, x(d), y(g), dx, dy, txt, BLUE, anch, weight=True)

    # the tie: same count, same depth, different circuit
    half_dot(e, x(TIE[0]), y(TIE[1]))
    e.append(f'<text x="{XR-4}" y="322" text-anchor="end" font-size="10.5" '
             f'fill="#666666">88 @ 7: ours ties the published point with an '
             f'independent circuit (61/88 shared masks)</text>')

    # ours, but derived from published work (and, at depth 8, dominated too)
    for d, g, txt, dx, dy, anch in OURS_DERIVED:
        e.append(f'<circle cx="{x(d):.1f}" cy="{y(g):.1f}" r="5.5" fill="#ffffff" '
                 f'stroke="{BLUE}" stroke-width="2"/>')
        label(e, x(d), y(g), dx, dy, txt, BLUE, anch, size=12)

    # legend
    lx, tx = 407, 432
    rows = [("dashline", "published frontier"),
            ("blueline", "this work, no imported material"),
            ("bluedash", "... extended by derived work"),
            ("half", "88 @ 7: ours ties published"),
            ("hollowblue", "ours, derived from published work"),
            ("hollowgrey", "published, off-frontier"),
            ("cross", "this project, superseded (v1)")]
    for i, (kind, txt) in enumerate(rows):
        ly = 44 + i * 22
        if kind == "dashline":
            e.append(f'<line x1="{lx-17}" y1="{ly-4}" x2="{lx+17}" y2="{ly-4}" stroke="{GREY}" '
                     f'stroke-width="2.5" stroke-dasharray="6,4"/>')
            dot(e, lx, ly - 4, 5, GREY)
        elif kind == "blueline":
            e.append(f'<line x1="{lx-17}" y1="{ly-4}" x2="{lx+17}" y2="{ly-4}" stroke="{BLUE}" stroke-width="2.5"/>')
            dot(e, lx, ly - 4, 6, BLUE)
        elif kind == "bluedash":
            e.append(f'<line x1="{lx-17}" y1="{ly-4}" x2="{lx+17}" y2="{ly-4}" stroke="{BLUE}" '
                     f'stroke-width="2" stroke-dasharray="5,4"/>')
            e.append(f'<circle cx="{lx}" cy="{ly-4}" r="5.5" fill="#ffffff" stroke="{BLUE}" stroke-width="2"/>')
        elif kind == "half":
            half_dot(e, lx, ly - 4)
        elif kind == "hollowblue":
            e.append(f'<circle cx="{lx}" cy="{ly-4}" r="5.5" fill="#ffffff" stroke="{BLUE}" stroke-width="2"/>')
        elif kind == "hollowgrey":
            e.append(f'<circle cx="{lx}" cy="{ly-4}" r="5.5" fill="#ffffff" stroke="{GREY}" stroke-width="2"/>')
        else:
            cross(e, lx, ly - 4)
        e.append(f'<text x="{tx}" y="{ly}" font-size="12" fill="#333333">{txt}</text>')

    e.append("</svg>")

    out = Path(__file__).resolve().parents[1] / "docs" / "frontier.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(e) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
