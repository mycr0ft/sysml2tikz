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

sys.path.insert(0, os.path.expanduser("~/proj/diagramboxes"))

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
    from diagramboxes.layout import Diagram

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


def emit(model: dict, d, by_id, ports, scale: float, out_path: str) -> None:
    geometry = {"nodes": {}, "ports": {}}
    lines = [r"\documentclass[tikz,border=10pt]{standalone}",
             r"\usepackage{sysml2tikz}",
             r"\begin{document}",
             r"\begin{tikzpicture}"]
    for node in model.get("nodes", []):
        n = by_id[node["id"]]
        cx = (n.x + n.w / 2.0) * scale
        cy = -(n.y + n.h / 2.0) * scale
        lines.append(node_call(node, "[at={(%.1fpt,%.1fpt)}]" % (cx, cy)))
        geometry["nodes"][node["id"]] = {
            "cx": cx, "cy": cy,
            "w": by_id[node["id"]].w * scale, "h": by_id[node["id"]].h * scale}
    for i, edge in enumerate(model.get("edges", [])):
        db_edge = d.edges[i]
        pts = [((x) * scale, -(y) * scale) for x, y in db_edge.waypoints]
        if not pts:
            continue
        style = edge.get("style", "reference")
        coords = " -- ".join("(%.1fpt,%.1fpt)" % p for p in pts)
        label = edge.get("label")
        if label:
            lx, ly, _ = label_at(db_edge.waypoints)
            lines.append(r"  \draw[sysml %s] %s;"
                         % (style, coords.replace(
                             " -- ", " -- ", 1)))
            lines.append(r"  \node[font=\scriptsize, right] at (%.1fpt,%.1fpt) {%s};"
                         % (lx * scale, -ly * scale, esc(label)))
        else:
            lines.append(r"  \draw[sysml %s] %s;" % (style, coords))
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


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
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
    d, by_id, ports = layout(model, sizes, scale, layer_gap, node_gap)
    emit(model, d, by_id, ports, scale, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
