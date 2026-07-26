#!/usr/bin/env python3
"""Generate docs/frontier.svg: the published depth-count Pareto frontier for
AES MixColumns vs this project's circuits. Pure stdlib; data below is the
single source (sources for every point: PRIOR_ART.md)."""

from pathlib import Path

PUBLISHED = [(3, 99, "SFX23"), (4, 97, "OC24"), (5, 94, "OC24"),
             (6, 92, "Max19"), (7, 88, "Jean26")]
OURS = [(3, 97, ""), (4, 92, ""), (5, 89, "")]
SUPERSEDED = [(3, 98, ""), (6, 91, ""), (10, 89, "")]   # this project's v1 points

X0, Y0, W, H = 70, 30, 560, 300                          # plot box
DMIN, DMAX, GMIN, GMAX = 3, 10, 86, 100

def sx(d): return X0 + (d - DMIN) * (W / (DMAX - DMIN))
def sy(g): return Y0 + (GMAX - g) * (H / (GMAX - GMIN))

def main():
    e = []
    e.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {X0+W+40} {Y0+H+60}" '
             f'font-family="Helvetica,Arial,sans-serif" font-size="13">')
    e.append(f'<rect x="0" y="0" width="{X0+W+40}" height="{Y0+H+60}" fill="white"/>')
    # grid + axes labels
    for g in range(GMIN, GMAX + 1, 2):
        y = sy(g)
        e.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X0+W}" y2="{y:.1f}" stroke="#dddddd" stroke-width="1"/>')
        e.append(f'<text x="{X0-8}" y="{y+4:.1f}" text-anchor="end" fill="#555555">{g}</text>')
    for d in range(DMIN, DMAX + 1):
        x = sx(d)
        e.append(f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y0+H}" stroke="#eeeeee" stroke-width="1"/>')
        e.append(f'<text x="{x:.1f}" y="{Y0+H+20}" text-anchor="middle" fill="#555555">{d}</text>')
    e.append(f'<rect x="{X0}" y="{Y0}" width="{W}" height="{H}" fill="none" stroke="#999999"/>')
    e.append(f'<text x="{X0+W/2:.0f}" y="{Y0+H+45}" text-anchor="middle" fill="#333333">circuit depth</text>')
    e.append(f'<text x="18" y="{Y0+H/2:.0f}" text-anchor="middle" fill="#333333" '
             f'transform="rotate(-90 18 {Y0+H/2:.0f})">2-input XOR gates</text>')

    def polyline(pts, color, dash=""):
        p = " ".join(f"{sx(d):.1f},{sy(g):.1f}" for d, g, _ in pts)
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        e.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="2.5"{dd}/>')

    # published frontier (gray) and this work (blue)
    polyline(PUBLISHED, "#888888", dash="6,4")
    for d, g, src in PUBLISHED:
        e.append(f'<circle cx="{sx(d):.1f}" cy="{sy(g):.1f}" r="5" fill="#888888"/>')
        e.append(f'<text x="{sx(d)+9:.1f}" y="{sy(g)-8:.1f}" fill="#666666">{g} {src}</text>')
    for d, g, _ in SUPERSEDED:
        x, y = sx(d), sy(g)
        e.append(f'<path d="M{x-5:.1f} {y-5:.1f} L{x+5:.1f} {y+5:.1f} M{x-5:.1f} {y+5:.1f} L{x+5:.1f} {y-5:.1f}" '
                 f'stroke="#bbbbbb" stroke-width="2"/>')
    polyline(OURS, "#1f6feb")
    for d, g, _ in OURS:
        e.append(f'<circle cx="{sx(d):.1f}" cy="{sy(g):.1f}" r="6" fill="#1f6feb"/>')
        e.append(f'<text x="{sx(d)+10:.1f}" y="{sy(g)+18:.1f}" font-weight="bold" '
                 f'fill="#1f6feb">{g}</text>')

    # legend
    lx, ly = X0 + W - 240, Y0 + 14
    e.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+34}" y2="{ly}" stroke="#888888" stroke-width="2.5" stroke-dasharray="6,4"/>')
    e.append(f'<text x="{lx+42}" y="{ly+4}" fill="#333333">published frontier</text>')
    e.append(f'<circle cx="{lx+17}" cy="{ly+22}" r="6" fill="#1f6feb"/>')
    e.append(f'<text x="{lx+42}" y="{ly+26}" fill="#333333">this work</text>')
    e.append(f'<path d="M{lx+12} {ly+39} L{lx+22} {ly+49} M{lx+12} {ly+49} L{lx+22} {ly+39}" stroke="#bbbbbb" stroke-width="2"/>')
    e.append(f'<text x="{lx+42}" y="{ly+48}" fill="#333333">this project, superseded (v1)</text>')
    e.append("</svg>")

    out = Path(__file__).resolve().parents[1] / "docs" / "frontier.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(e) + "\n", encoding="utf-8")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
