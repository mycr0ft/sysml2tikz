#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""layout_adapter.py — stage 3 of the sysml2tikz pipeline.

TikZ does not lay out graphs, and diagramboxes does not know how wide a TikZ
tabular will be. So: measure in TeX, lay out in diagramboxes, emit absolute
coordinates.

    1. measure   emit a throwaway .tex that places every block, then prints
                 width()/height() for each via \\typeout; compile with tectonic
                 --keep-logs and parse the log.
    2. layout    build a diagramboxes Diagram with those exact sizes (the
                 per-node `_calc_size` is neutered so the real size survives),
                 run its orthogonal router, read node origins and edge
                 waypoints.
    3. emit      write the real .tex with at={(x,y)} per node and one
                 \\draw ... -- (x,y) -- ... polyline per edge.

Usage:
    python3 layout_adapter.py model.json out.tex [--scale 4.0]

`--scale` is points per diagramboxes unit. Sizes are divided by it going in
and multiplied coming out, so the router's gaps mean "scale points".
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------- emit helpers
_ESCAPE = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#",
    "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    "_": r"\_",
}


def esc(text: str) -> str:
    return "".join(_ESCAPE.get(c, c) for c in text)


def render_row(row: str) -> str:
    row = row.strip()
    if row.startswith(":>>"):
        # '>>' is a ligature in T1/TU fonts and prints as »; break it explicitly
        return r"\redefines{:\textgreater{}\textgreater{}%s}" % esc(row[3:])
    parts = re.split(r"\*([^*]+)\*", row)
    out = []
    for i, part in enumerate(parts):
        out.append((r"\kw{%s}" % esc(part)) if i % 2 else esc(part))
    return "".join(out)


def node_body(node: dict) -> str:
    bits = []
    for comp in node.get("compartments", []):
        bits.append(r"\sysmlcomp{%s}" % esc(comp["label"]))
        for row in comp["rows"]:
            bits.append(render_row(row) + r"\\")
    return "".join(bits)


def node_call(node: dict, opt: str) -> str:
    kind = node["kind"]
    body = node_body(node)
    if kind.endswith(" def"):
        return ("  \\sysmldefnode%s{%s}{%s}{%s}{%%\n    %s\n  }\n"
                % (opt, node["id"], esc(kind), esc(node["name"]), body))
    return ("  \\sysmlusagenode%s{%s}{%s}{%s}{%s}{%%\n    %s\n  }\n"
            % (opt, node["id"], esc(kind), esc(node["name"]),
               esc(node.get("type", "")), body))


# ------------------------------------------------------------------- 1 measure
def measure(model: dict, workdir: str, tectonic: str) -> dict[str, tuple[float, float]]:
    """Return {node id: (width_pt, height_pt)} measured by TeX itself."""
    # the throwaway measure document needs the package on its path; a render
    # directory created outside the repo (the corpus) has no symlink to it
    sty = os.path.join(workdir, "sysml2tikz.sty")
    if not os.path.exists(sty):
        import shutil
        from . import sty_path
        shutil.copyfile(sty_path(), sty)
    nodes = model.get("nodes", [])
    # spread them out so nothing overlaps while measuring
    lines = [r"\documentclass[tikz,border=2pt,multi=false]{standalone}",
             r"\usepackage{sysml2tikz}",
             r"\begin{document}",
             r"\begin{tikzpicture}[x=200cm,y=1cm]"]
    for i, node in enumerate(nodes):
        lines.append(node_call(node, "[at={(%.3fcm,0)}]" % i))
    for node in nodes:
        # measure by anchor difference: width("name") is fragile with quoting
        lines.append(r"  \newdimen\sysmlw\newdimen\sysmlh")
        lines.append(r"  \pgfextractx{\sysmlw}{\pgfpointdiff{\pgfpointanchor{%s}{west}}"
                     r"{\pgfpointanchor{%s}{east}}}" % (node["id"], node["id"]))
        lines.append(r"  \pgfextracty{\sysmlh}{\pgfpointdiff{\pgfpointanchor{%s}{south}}"
                     r"{\pgfpointanchor{%s}{north}}}" % (node["id"], node["id"]))
        lines.append(r"  \typeout{SYSMLSZ %s \the\sysmlw}" % node["id"])
        lines.append(r"  \typeout{SYSMLSH %s \the\sysmlh}" % node["id"])
    lines += [r"\end{tikzpicture}", r"\end{document}", ""]
    tex = os.path.join(workdir, "measure.tex")
    with open(tex, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    subprocess.run([tectonic, "--keep-logs", tex], cwd=workdir,
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = os.path.join(workdir, "measure.log")
    sizes: dict[str, dict[str, float]] = {}
    with open(log, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.search(r"SYSMLSZ (\S+) ([\d.]+)", line)
            if m:
                sizes.setdefault(m.group(1), {})["w"] = float(m.group(2))
            m = re.search(r"SYSMLSH (\S+) ([\d.]+)", line)
            if m:
                sizes.setdefault(m.group(1), {})["h"] = float(m.group(2))
    missing = [n["id"] for n in nodes if n["id"] not in sizes]
    if missing:
        raise SystemExit("measure failed for: %s" % ", ".join(missing))
    return {k: (v["w"], v["h"]) for k, v in sizes.items()}


# -------------------------------------------------------------------- 2 layout
def layout(model: dict, sizes: dict[str, tuple[float, float]], scale: float,
           layer_gap: int, node_gap: int):
    try:
        from diagramboxes.layout import Diagram
    except ImportError:                    # dev checkout without an install
        sys.path.insert(0, os.path.expanduser("~/proj/diagramboxes"))
        try:
            from diagramboxes.layout import Diagram
        except ImportError as exc:
            raise SystemExit(
                "layout needs diagramboxes (pip install 'sysml2tikz[layout]'): %s" % exc)

    d = Diagram()
    by_id = {}
    for node in model.get("nodes", []):
        n = d.add_node(node["id"])
        n._calc_size = lambda: None          # keep the TeX size, do not re-derive
        w, h = sizes[node["id"]]
        # diagramboxes' router works in integer pixel units
        n.w, n.h = max(1, int(round(w / scale))), max(1, int(round(h / scale)))
        by_id[node["id"]] = n
    # ports: IR side names -> diagramboxes sides; the router docks on them
    side_map = {"east": "right", "west": "left", "north": "top", "south": "bottom"}
    ports: dict[tuple[str, str], object] = {}
    for port in model.get("ports", []):
        node = by_id[port["node"]]
        db_side = side_map[port["side"]]
        ports[(port["node"], port["side"])] = node.add_port(
            port["name"], side=db_side, offset=0.5,
            direction=port.get("direction"))
    for edge in model.get("edges", []):
        kw = {}
        if edge.get("src_port"):
            kw["source_port"] = ports[(edge["src"], edge["src_port"])]
        if edge.get("dst_port"):
            kw["target_port"] = ports[(edge["dst"], edge["dst_port"])]
        d.add_edge(by_id[edge["src"]], by_id[edge["dst"]], **kw)
    d.layout(routing="orthogonal", layer_gap=layer_gap, node_gap=node_gap)
    return d, by_id, ports


# ---------------------------------------------------------------------- 3 emit
def label_at(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    """Label position + the angle of the segment carrying it (longest segment)."""
    best, best_len = None, -1.0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if length > best_len:
            best, best_len = ((x1 + x2) / 2.0, (y1 + y2) / 2.0), length
    return best[0], best[1], best_len


def emit(model: dict, d, by_id, ports, scale: float, out_path: str,
         node_gap: int = 8, layer_gap: int = 16) -> None:
    geometry = {"nodes": {}, "ports": {}}
    lines = [r"\documentclass[tikz,border=10pt]{standalone}",
             r"\usepackage{sysml2tikz}",
             r"\begin{document}",
             r"\begin{tikzpicture}"]
    wrapped = pack_ranks(d, model, scale, node_gap, layer_gap_hint=layer_gap)
    for node in model.get("nodes", []):
        n = by_id[node["id"]]
        cx = (n.x + n.w / 2.0) * scale
        cy = -(n.y + n.h / 2.0) * scale
        lines.append(node_call(node, "[at={(%.1fpt,%.1fpt)}]" % (cx, cy)))
        geometry["nodes"][node["id"]] = {
            "cx": cx, "cy": cy,
            "w": by_id[node["id"]].w * scale, "h": by_id[node["id"]].h * scale}
    geometry["wrapped_ranks"] = wrapped
    boxes = {}
    for nid, g in geometry["nodes"].items():
        boxes[nid] = (g["cx"] - g["w"] / 2.0, g["cy"] - g["h"] / 2.0,
                      g["cx"] + g["w"] / 2.0, g["cy"] + g["h"] / 2.0)

    for i, edge in enumerate(model.get("edges", [])):
        db_edge = d.edges[i]
        style = edge.get("style", "reference")
        label = edge.get("label")

        # port-anchored edges keep the engine's route (it starts on a port glyph);
        # node-to-node edges get our own candidate search, which tests every
        # alternative against every foreign box instead of accepting one route
        if edge.get("src_port") or edge.get("dst_port"):
            pts = [(x * scale, -(y) * scale) for x, y in db_edge.waypoints]
            label_pts = pts
        else:
            pts = route_between(boxes, edge["src"], edge["dst"])
            label_pts = pts
        if not pts:
            continue

        coords = " -- ".join("(%.1fpt,%.1fpt)" % p for p in pts)
        lines.append(r"  \draw[sysml %s] %s;" % (style, coords))
        if label:
            if style == "composition" and len(label_pts) >= 2:
                (x1, y1), (x2, y2) = label_pts[0], label_pts[1]
                lx, ly = x1 + (x2 - x1) * 0.15, y1 + (y2 - y1) * 0.15
            else:
                lx, ly, _ = label_at(label_pts)
            lines.append(r"  \node[font=\scriptsize, right] at (%.1fpt,%.1fpt) {%s};"
                         % (lx, ly, esc(label)))

    # diagramboxes parks a port just OUTSIDE the node wall (x = px + pw); the
    # corpus draws the square centred ON the wall. Slide the glyph back by half
    # the router's own port box, so glyph centre == wall and the routed flow
    # still terminates on the glyph's outer face.
    for port in model.get("ports", []):
        db_port = ports[(port["node"], port["side"])]
        px = (db_port.x + db_port.w / 2.0) * scale
        py = -(db_port.y + db_port.h / 2.0) * scale
        side = port["side"]
        if side == "east":
            px -= (db_port.w / 2.0) * scale
        elif side == "west":
            px += (db_port.w / 2.0) * scale
        elif side == "north":
            py -= (db_port.h / 2.0) * scale
        elif side == "south":
            py += (db_port.h / 2.0) * scale
        lines.append("  \\sysmlportat{%s-p-%s}{(%.1fpt,%.1fpt)}{%s}{%s}"
                     % (port["node"], port["side"], px, py, esc(port["name"]),
                        port.get("label_side", "above right")))
        geometry["ports"]["%s.%s" % (port["node"], port["side"])] = {
            "x": px, "y": py, "side": port["side"]}
    lines += [r"\end{tikzpicture}", r"\end{document}", ""]
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    stem = os.path.splitext(os.path.basename(out_path))[0]
    sidecar = os.path.join(os.path.dirname(os.path.abspath(out_path)),
                           "geometry-%s.json" % stem)
    with open(sidecar, "w", encoding="utf-8") as fh:
        json.dump(geometry, fh, indent=2, sort_keys=True)
    print("wrote", out_path, "and", sidecar)


def grid_positions(sizes: dict[str, tuple[float, float]], gap: float = 16.0):
    """Place edge-free nodes in a grid, sized per row and per column.

    A package of 34 definitions has no edges, so a rank-based router puts all 34
    on one line and the figure becomes a 9000x400 smear. Nothing is being laid
    out in that case, so lay it out as a grid — and size each column by its
    widest box and each row by its tallest, otherwise one tall block (Vehicle)
    inflates every row and the sheet is mostly whitespace.
    """
    import math
    ids = sorted(sizes)
    cols = max(1, int(math.ceil(math.sqrt(len(ids) * 1.4))))
    rows = math.ceil(len(ids) / cols)

    col_w = [0.0] * cols
    row_h = [0.0] * rows
    for idx, nid in enumerate(ids):
        r, c = divmod(idx, cols)
        col_w[c] = max(col_w[c], sizes[nid][0])
        row_h[r] = max(row_h[r], sizes[nid][1])

    x_at, y_at = [], []
    x = 0.0
    for w in col_w:
        x_at.append(x)
        x += w + gap
    y = 0.0
    for h in row_h:
        y_at.append(y)
        y += h + gap

    return {nid: (x_at[idx % cols], -y_at[idx // cols]) for idx, nid in enumerate(ids)}


def wrap_ranks(geometry: dict, max_width: float = 1500.0, gap: float = 26.0) -> int:
    """Wrap only the ranks that are too wide; leave the rest exactly where they are.

    A tree puts every sibling on one rank, so a 19-node rank becomes a 3000pt
    strip. Siblings do not have to share one line, so an over-wide rank is split
    into rows: the rank keeps its y for the first row, its extra rows push the
    ranks below down, and untouched ranks keep their x. Returns the number of
    wrapped ranks.
    """
    nodes = geometry["nodes"]
    if not nodes:
        return 0

    ranks: dict[float, list[str]] = {}
    for nid, g in nodes.items():
        ranks.setdefault(round(g["cy"], 1), []).append(nid)

    wrapped = 0
    offset = 0.0
    for rank_y in sorted(ranks, reverse=True):          # top-down (y up)
        ids = sorted(ranks[rank_y], key=lambda n: nodes[n]["cx"])
        row_h = max(nodes[n]["h"] for n in ids)

        rows, cur, cur_w = [], [], 0.0
        for nid in ids:
            w = nodes[nid]["w"]
            if cur and cur_w + gap + w > max_width:
                rows.append(cur)
                cur, cur_w = [], 0.0
            cur.append(nid)
            cur_w += (gap if cur_w else 0.0) + w
        if cur:
            rows.append(cur)

        base_y = rank_y - offset
        if len(rows) == 1:
            for nid in ids:                              # untouched: only the shift
                nodes[nid]["cy"] = base_y
            offset += 0.0
            continue

        for r_i, row in enumerate(rows):
            row_w = sum(nodes[n]["w"] for n in row) + gap * (len(row) - 1)
            x = -row_w / 2.0
            y = base_y - r_i * (row_h + gap)
            for nid in row:
                nodes[nid]["cx"] = x + nodes[nid]["w"] / 2.0
                nodes[nid]["cy"] = y
                x += nodes[nid]["w"] + gap
        wrapped += 1
        offset += (len(rows) - 1) * (row_h + gap)
    return wrapped


def pack_ranks(d, model: dict, scale: float, node_gap: int, max_width: float = 1100.0,
               layer_gap_hint: int | None = None):
    """Rank-width-first placement, applied AFTER the engine's layering.

    The engine's layering (which nodes are on which rank) is good — it is the
    Sugiyama layer assignment and it produces the vertical order the notation
    wants. What it does not do is account for width: it walks each rank left to
    right from that rank's own origin, so ranks drift right under wide parents
    and a 19-node rank becomes a 2957pt strip.

    So: accept the engine's ranks, measure every rank's width in emitted
    points, then
      1. centre every rank that fits      -> figures stop drifting right
      2. wrap every rank that does not    -> strips become sheets
      3. push the ranks below a wrapped one down, keeping their centring
    Port-anchored nodes are left exactly where the engine put them: their edges
    are emitted from the engine's waypoints and sliding them would detach the
    ports. Returns the number of ranks wrapped.
    """
    nodes = d.nodes
    ranked: dict[int, list] = {}
    # the engine staggers rows of a rank slightly (PartsTree: -152/-144/-136);
    # bucket on a quantum comfortably below the layer gap so a staggered rank
    # stays one rank: layer_gap is node_gap*2=16 units, so a quarter of that
    # (4 units) is right; the verifier uses h-based tolerance.
    bucket = node_gap                                # 8 units: catches a stagger
                                                     # of up to 8 units per rank
    for n in nodes:
        ranked.setdefault(round(n.y / bucket) * bucket, []).append(n)

    unit_gap = node_gap * scale                      # engine units -> points
    wrapped = 0
    offset = 0.0                                     # accumulated y push, points

    # ascending engine y: a wrapped rank adds `offset`, and ranks with larger
    # engine y (further down the figure) come later in the loop, so the push
    # reaches them
    for rank_y in sorted(ranked):
        members = ranked[rank_y]
        anchors = port_anchored(d)
        slideable = [n for n in members if id(n) not in anchors]
        if not slideable:
            offset += 0.0
            continue

        total_w = (sum(n.w for n in members) * scale
                   + unit_gap * (len(members) - 1))

        if total_w <= max_width:
            # centring only: shift the whole rank so its midpoint is x=0, and
            # carry any push-down accumulated from a wrapped rank above
            xs = [(n.x + n.w / 2.0) for n in members]
            mid = (min(xs) + max(xs)) / 2.0
            for n in members:
                n.x -= mid
                n.y += offset
            continue

        # over-wide: wrap into rows of <= max_width, then centre each row
        wrapped += 1
        members.sort(key=lambda n: n.x)
        rows, cur, cur_w = [], [], 0.0
        for n in members:
            w = n.w * scale
            if cur and cur_w + unit_gap + w > max_width:
                rows.append(cur)
                cur, cur_w = [], 0.0
            cur.append(n)
            cur_w += (unit_gap if cur_w else 0.0) + w
        if cur:
            rows.append(cur)

        row_h = max(n.h for n in members) * scale
        base_y = rank_y + offset                     # engine units
        for r_i, row in enumerate(rows):
            row_w = sum(n.w for n in row) * scale + unit_gap * (len(row) - 1)
            x = -row_w / 2.0 / scale                 # engine units
            y = base_y + r_i * (row_h + unit_gap) / scale
            for n in row:
                n.x = x
                n.y = y
                x += n.w + node_gap
        offset += (len(rows) - 1) * (row_h + unit_gap) / scale
    return wrapped


def port_anchored(d) -> set[int]:
    """Identity of nodes whose edges dock on ports (their x must not change).

    diagramboxes' Node carries the name in ``.name`` (``.label`` is the
    Lifeline attribute); identity is what matters anyway, since ``add_node``
    was called per IR node.
    """
    out: set[int] = set()
    for e in d.edges:
        for end in (e.source, e.target):
            if getattr(end, "ports", None):
                out.add(id(end))
    return out


def _segment_hits(p1, p2, boxes, skip, samples=120):
    """How many foreign boxes this segment passes through."""
    (x1, y1), (x2, y2) = p1, p2
    hits = 0
    for name, (x0, y0, x3, y3) in boxes.items():
        if name in skip:
            continue
        for i in range(samples + 1):
            u = i / samples
            x, y = x1 + (x2 - x1) * u, y1 + (y2 - y1) * u
            if x0 < x < x3 and y0 < y < y3:
                hits += 1
                break
    return hits


def _path_hits(pts, boxes, skip):
    return sum(_segment_hits(a, b, boxes, skip) for a, b in zip(pts, pts[1:]))


def route_between(boxes, src, dst, gap=24.0):
    """Candidate orthogonal routes between two boxes; pick the one with no crossings.

    The layout engine gives positions; this decides the path. Every candidate is
    tested against every foreign box, and the score is crossings first, bends
    second, length last — a detour is always better than a line through a block.
    """
    sx0, sy0, sx1, sy1 = boxes[src]
    tx0, ty0, tx1, ty1 = boxes[dst]
    scx, scy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    tcx, tcy = (tx0 + tx1) / 2, (ty0 + ty1) / 2
    skip = {src, dst}

    vertical = abs(tcy - scy) >= abs(tcx - scx)
    cands = []

    # gutters: when a rank is packed, a sibling-to-sibling edge has no lane
    # between boxes, so it must leave the band entirely and come back
    all_x0 = min(v[0] for v in boxes.values())
    all_x1 = max(v[2] for v in boxes.values())
    all_y0 = min(v[1] for v in boxes.values())
    all_y1 = max(v[3] for v in boxes.values())
    if vertical:
        down = tcy < scy
        a = (scx, sy0 if down else sy1)
        b = (tcx, ty1 if down else ty0)
        if abs(scx - tcx) < 0.5:
            cands.append([a, b])
        for off in (0, gap, 2 * gap, 3 * gap, -gap, -2 * gap):
            my = (a[1] + b[1]) / 2 + off
            cands.append([a, (a[0], my), (b[0], my), b])
        cands.append([a, (a[0], b[1]), b])
        cands.append([a, (b[0], a[1]), b])
        for gx in (all_x0 - gap, all_x1 + gap):
            cands.append([a, (gx, a[1]), (gx, b[1]), b])
    else:
        right = tcx > scx
        a = (sx1 if right else sx0, scy)
        b = (tx0 if right else tx1, tcy)
        if abs(scy - tcy) < 0.5:
            cands.append([a, b])
        for off in (0, gap, 2 * gap, 3 * gap, -gap, -2 * gap):
            mx = (a[0] + b[0]) / 2 + off
            cands.append([a, (mx, a[1]), (mx, b[1]), b])
        cands.append([a, (b[0], a[1]), b])
        cands.append([a, (a[0], b[1]), b])
        for gy in (all_y0 - gap, all_y1 + gap):
            cands.append([a, (a[0], gy), (b[0], gy), b])

    best, best_score = None, None
    for pts in cands:
        hits = _path_hits(pts, boxes, skip)
        bends = len(pts) - 2
        length = sum(abs(x2 - x1) + abs(y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:]))
        score = 10000 * hits + 30 * bends + 0.01 * length
        if best_score is None or score < best_score:
            best, best_score = pts, score
    return best


def emit_grid(model: dict, sizes: dict[str, tuple[float, float]], out_path: str) -> None:
    pos = grid_positions(sizes)
    geometry = {"nodes": {}, "ports": {}, "layout": "grid"}
    lines = [r"\documentclass[tikz,border=10pt]{standalone}",
             r"\usepackage{sysml2tikz}",
             r"\begin{document}",
             r"\begin{tikzpicture}"]
    for node in model.get("nodes", []):
        x, y = pos[node["id"]]
        lines.append(node_call(node, "[at={(%.1fpt,%.1fpt)}]" % (x, y)))
        w, h = sizes[node["id"]]
        geometry["nodes"][node["id"]] = {"cx": x, "cy": y, "w": w, "h": h}
    lines += [r"\end{tikzpicture}", r"\end{document}", ""]
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    stem = os.path.splitext(os.path.basename(out_path))[0]
    with open(os.path.join(os.path.dirname(os.path.abspath(out_path)),
                           "geometry-%s.json" % stem), "w", encoding="utf-8") as fh:
        json.dump(geometry, fh, indent=2, sort_keys=True)
    print("wrote", out_path, "(grid layout, %d nodes)" % len(sizes))


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    want_sty = "--copy-sty" in sys.argv
    argv = [a for a in argv if a != "--copy-sty"]
    model_path, out_path = argv[1], argv[2]
    scale = 4.0
    layer_gap, node_gap = 14, 8
    for i, arg in enumerate(argv[3:]):
        if arg == "--scale":
            scale = float(argv[3 + i + 1])
    with open(model_path, encoding="utf-8") as fh:
        model = json.load(fh)
    workdir = os.path.dirname(os.path.abspath(out_path))
    tectonic = os.path.expanduser("~/.local/bin/tectonic")
    sizes = measure(model, workdir, tectonic)
    print("measured:", {k: (round(v[0], 1), round(v[1], 1)) for k, v in sizes.items()})
    if not model.get("edges") and len(sizes) > 3:
        emit_grid(model, sizes, out_path)
        if want_sty:
            print("copied", copy_sty(os.path.dirname(os.path.abspath(out_path))))
        return 0
    d, by_id, ports = layout(model, sizes, scale, layer_gap, node_gap)
    emit(model, d, by_id, ports, scale, out_path, node_gap, layer_gap)
    if want_sty:
        from .emit import copy_sty
        print("copied", copy_sty(os.path.dirname(os.path.abspath(out_path))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
