# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Gate: no routed edge may pass through a box it does not terminate on.

This is the mechanical version of the "edges running over boxes" fight. It works
on what the renderer emitted — the polylines in the .tex plus the box rectangles
in the geometry sidecar — so it catches the defect after the router, whoever the
router is.

    python3 tools/check_routing.py                # every .tex with a geometry sidecar
    python3 tools/check_routing.py gen/veh.tex    # one file

A hit means the router chose a path through a foreign box. Fix the routing input
(order, ports, gaps) — do not paper over it with a manual bend, which the next
re-layout will discard.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "gen")
PAD = 1.0          # pt; ignore hairline grazes on a shared border
SAMPLES = 400      # per segment, plenty for axis-aligned runs


def segments(tex: str) -> list[list[tuple[float, float]]]:
    """Every polyline drawn with a sysml edge style, as lists of points."""
    out = []
    for m in re.finditer(r"\\draw\[sysml [^\]]*\]((?:(?!;).)*);", tex, re.S):
        body = m.group(1)
        # a 'to[out=..,in=..]' curve has only its endpoints as coordinates; treat
        # it as a straight chord — conservative for crossing detection
        pts = [(float(a), float(b))
               for a, b in re.findall(r"\((-?[\d.]+)pt,\s*(-?[\d.]+)pt\)", body)]
        if len(pts) >= 2:
            out.append(pts)
    return out


def hits(pts, boxes, skip: set[str]) -> list[str]:
    bad = []
    for name, (x0, y0, x1, y1) in boxes.items():
        if name in skip:
            continue
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            for i in range(SAMPLES + 1):
                t = i / SAMPLES
                x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                if x0 + PAD < x < x1 - PAD and y0 + PAD < y < y1 - PAD:
                    bad.append(name)
                    break
            else:
                continue
            break
    return sorted(set(bad))


def check(tex_path: str) -> list[str]:
    stem = os.path.basename(tex_path)[:-4]
    stem = {"model": "laid_out"}.get(stem, stem)
    geo_path = os.path.join(os.path.dirname(tex_path), "geometry-%s.json" % stem)
    if not os.path.exists(geo_path):
        return []
    geo = json.loads(open(geo_path, encoding="utf-8").read())
    boxes = {k: (v["cx"] - v["w"] / 2, v["cy"] - v["h"] / 2,
                 v["cx"] + v["w"] / 2, v["cy"] + v["h"] / 2)
             for k, v in geo["nodes"].items()}
    # which boxes an edge may legitimately touch: the ones it starts/ends in
    tex = open(tex_path, encoding="utf-8").read()
    problems = []
    for pts in segments(tex):
        near = []
        for name, (x0, y0, x1, y1) in boxes.items():
            for (px, py) in (pts[0], pts[-1]):
                if (x0 - 2) <= px <= (x1 + 2) and (y0 - 2) <= py <= (y1 + 2):
                    near.append(name)
        bad = hits(pts, boxes, set(near))
        if bad:
            problems.append("edge %s -> %s crosses %s"
                            % (fmt(pts[0]), fmt(pts[-1]), ", ".join(bad)))
    return problems


def fmt(p) -> str:
    return "(%.0f,%.0f)" % p


def main(argv: list[str]) -> int:
    targets = argv[1:] or sorted(glob.glob(os.path.join(GEN, "*.tex")))
    failures = []
    for tex in targets:
        probs = check(tex)
        name = os.path.basename(tex)
        if probs:
            print("FAIL %s" % name)
            for p in probs:
                print("       " + p)
            failures.append(name)
        else:
            print("ok   %s routing clear of foreign boxes" % name)
    print("\nPASS" if not failures else "FAIL (%d file(s))" % len(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
