#!/usr/bin/env python3
"""Generate the exploded axonometric wall section used in the hero.

The drawing is the page's signature: a straw panel pulled apart into its
four layers. Geometry lives here so the figure can be re-proportioned
without hand-editing SVG paths.

Axes: x runs along the wall, y is height, z is wall thickness (towards the
viewer). Isometric projection, viewer at (+x, +y, +z), so the visible faces
of every box are +x, +y and +z. Boxes are painted in order of x+y+z.

Usage:  python3 wall_section.py            print the SVG
        python3 wall_section.py --inject   write it into ../index.html
                                           between the wall:start/end markers
"""

import pathlib
import re
import sys

COS30, SIN30 = 0.8660254, 0.5

W, H = 220, 250          # wall width and height
GAP = 64                 # extra thickness-axis distance between exploded layers
STUD = 12                # timber member section


def proj(x, y, z):
    return (x * COS30 - z * COS30, x * SIN30 + z * SIN30 - y)


def box(x0, x1, y0, y1, z0, z1):
    return dict(x0=x0, x1=x1, y0=y0, y1=y1, z0=z0, z1=z1)


def faces(b):
    """Visible faces as (kind, [points]) for one box."""
    x0, x1, y0, y1, z0, z1 = (b[k] for k in ("x0", "x1", "y0", "y1", "z0", "z1"))
    return [
        ("top", [proj(x0, y1, z0), proj(x1, y1, z0), proj(x1, y1, z1), proj(x0, y1, z1)]),
        ("front", [proj(x0, y0, z1), proj(x1, y0, z1), proj(x1, y1, z1), proj(x0, y1, z1)]),
        ("side", [proj(x1, y0, z0), proj(x1, y0, z1), proj(x1, y1, z1), proj(x1, y1, z0)]),
    ]


# Layers from the inside out. k is the explode index along +z.
# Straw sits inside the frame when assembled; exploding pulls it forward.
LAYERS = [
    ("clay-in", 0, [box(0, W, 0, H, 0, 6)]),
    ("frame", 1, [
        box(0, W, 0, STUD, 6, 56),                     # bottom plate
        box(0, STUD, STUD, H - STUD, 6, 56),           # left stud
        box((W - STUD) / 2, (W + STUD) / 2, STUD, H - STUD, 6, 56),
        box(W - STUD, W, STUD, H - STUD, 6, 56),       # right stud
        box(0, W, H - STUD, H, 6, 56),                 # top plate
    ]),
    ("straw", 2, [
        box(STUD, (W - STUD) / 2, STUD, H - STUD, 8, 54),
        box((W + STUD) / 2, W - STUD, STUD, H - STUD, 8, 54),
    ]),
    ("clay-out", 3, [box(0, W, 0, H, 56, 62)]),
]

# Marker number per layer, counted from the outside in (matches the legend).
MARKER = {"clay-out": 1, "straw": 2, "frame": 3, "clay-in": 4}

# Where each number sits: a point on a face that stays visible when exploded.
BALE = (W - 3 * STUD) / 2
MARKER_AT = {
    "clay-out": (W * 0.5, H * 0.72, 62),                    # middle of the front face
    "straw": ((W + STUD) / 2 + BALE / 2, H - STUD, 31),     # top of the right bale
    "frame": (W * 0.2, H, 31),                              # top plate
    "clay-in": (W * 0.8, H * 0.78, 6),                      # upper right of the front face
}

FILL = {
    "clay":  {"top": "var(--fig-clay-top)",  "front": "url(#stipple)", "side": "var(--fig-clay-side)"},
    "straw": {"top": "url(#straw-top)",      "front": "url(#straw)",   "side": "var(--fig-straw-side)"},
    "frame": {"top": "var(--fig-wood-top)",  "front": "var(--fig-wood-front)", "side": "var(--fig-wood-side)"},
}


def material(name):
    return "clay" if name.startswith("clay") else name


def shifted(b, dz):
    b = dict(b)
    b["z0"] += dz
    b["z1"] += dz
    return b


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def main():
    parts, bounds = [], []
    markers = []
    for name, k, boxes in LAYERS:
        dz = k * GAP
        placed = sorted((shifted(b, dz) for b in boxes),
                        key=lambda b: (b["x0"] + b["x1"]) + (b["y0"] + b["y1"]) + (b["z0"] + b["z1"]))
        # assembled-state offset: undo the explode along the projected z axis
        ax, ay = k * GAP * COS30, -k * GAP * SIN30
        polys = []
        for b in placed:
            for kind, p in faces(b):
                bounds.extend(p)
                polys.append(f'<polygon class="f-{kind}" points="{pts(p)}" fill="{FILL[material(name)][kind]}"/>')
        parts.append(
            f'<g class="wall-layer" data-layer="{name}" style="--ax:{ax:.1f}px;--ay:{ay:.1f}px;--k:{k}">'
            + "".join(polys) + "</g>"
        )
        mx, my = proj(*MARKER_AT[name][:2], MARKER_AT[name][2] + dz)
        markers.append((MARKER[name], mx, my))

    minx = min(x for x, _ in bounds) - 6
    maxx = max(x for x, _ in bounds) + 6
    miny = min(y for _, y in bounds) - 6
    maxy = max(y for _, y in bounds) + 6

    # numbers sit on each layer's own visible face, so no leader line has to
    # cross another layer
    marker_svg = []
    for n, mx, my in sorted(markers):
        marker_svg.append(
            f'<g class="wall-marker"><circle cx="{mx:.1f}" cy="{my:.1f}" r="13"/>'
            f'<text x="{mx:.1f}" y="{my:.1f}" dy="0.35em">{n}</text></g>'
        )

    defs = """<defs>
<pattern id="straw" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-30)">
<rect width="7" height="7" fill="var(--fig-straw-front)"/><line x1="0" y1="0" x2="0" y2="7" stroke="var(--fig-straw-line)" stroke-width="1.4"/></pattern>
<pattern id="straw-top" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
<rect width="6" height="6" fill="var(--fig-straw-top)"/><line x1="0" y1="0" x2="0" y2="6" stroke="var(--fig-straw-line)" stroke-width="1"/></pattern>
<pattern id="stipple" width="9" height="9" patternUnits="userSpaceOnUse">
<rect width="9" height="9" fill="var(--fig-clay-front)"/><circle cx="2" cy="3" r="0.8" fill="var(--fig-clay-dot)"/><circle cx="6.5" cy="7" r="0.7" fill="var(--fig-clay-dot)"/></pattern>
</defs>"""

    svg = (
        f'<svg class="wall-figure" viewBox="{minx:.0f} {miny:.0f} {maxx - minx:.0f} {maxy - miny:.0f}" '
        f'role="img" aria-labelledby="wall-fig-title">'
        f'<title id="wall-fig-title" data-i18n="hero.figureTitle"></title>'
        + defs + "".join(parts)
        + '<g class="wall-markers">' + "".join(marker_svg) + "</g></svg>"
    )
    if "--inject" in sys.argv:
        page = pathlib.Path(__file__).resolve().parent.parent / "index.html"
        html = page.read_text(encoding="utf-8")
        html, n = re.subn(r"(<!-- wall:start -->).*?(<!-- wall:end -->)",
                          lambda m: m.group(1) + "\n" + svg + "\n" + m.group(2), html, flags=re.S)
        if n != 1:
            sys.exit("wall:start/end markers not found in index.html")
        page.write_text(html, encoding="utf-8")
    else:
        print(svg)


if __name__ == "__main__":
    main()
