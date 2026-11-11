#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
r"""emit_tex.py — reference implementation of stage 4 of the sysml2tikz pipeline.

Reads a small notation IR (JSON) and writes a TikZ .tex file that uses
sysml2tikz.sty. Deliberately dumb: no parsing, no layout engine, no model
semantics — those are stages 1-3. This exists to pin down the emitter
contract (row mini-syntax, escaping, deterministic ordering) and to prove the
IR is expressive enough for definition/usage figures.

Row mini-syntax (one string per compartment row):
    "*perform* providePower"   -> keyword in bold:  \kw{perform} providePower
    ":>>Vehicle::mass"         -> redefinition row: \redefines{:>>Vehicle::mass}
    "mass :> mass"             -> plain text, ':>' kept literally
    "text = \"1800 kg\""       -> plain text, '=' kept literally

Usage:
    python3 emit_tex.py model.json out.tex
"""
from __future__ import annotations

import json
import re
import sys

# LaTeX specials that must not reach the output raw. Order matters: backslash
# first, then the rest. ':' '>' '=' '<' '"' are left alone on purpose — they
# are SysML notation, and the font encoding handles them.
_ESCAPE = {
    "\\": r"\textbackslash{}",
    "_": r"\_",
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "$": r"\$",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def esc(text: str) -> str:
    out = []
    for ch in text:
        out.append(_ESCAPE.get(ch, ch))
    return "".join(out)


def render_row(row: str) -> str:
    """Turn one IR row string into LaTeX source (no trailing line break)."""
    row = row.strip()
    if row.startswith(":>>"):
        # '>>' is a ligature in T1/TU fonts and prints as »; break it explicitly
        return r"\redefines{:\textgreater{}\textgreater{}%s}" % esc(row[3:])
    # *keyword* anywhere in the row becomes \kw{keyword}
    parts = re.split(r"\*([^*]+)\*", row)
    out = []
    for i, part in enumerate(parts):
        out.append((r"\kw{%s}" % esc(part)) if i % 2 else esc(part))
    return "".join(out)


def render_compartments(compartments) -> str:
    bits = []
    for comp in compartments:
        bits.append(r"\sysmlcomp{%s}" % esc(comp["label"]))
        for row in comp["rows"]:
            bits.append(render_row(row) + r"\\")
    # the final row keeps its \\ so the tabular closes cleanly
    return "".join(bits)


def emit_node(node: dict) -> str:
    kind = node["kind"]
    place = node.get("place")  # e.g. "at={(0,0)}" or "below=of veh"
    opt = f"[{place}]" if place else "[at={(0,0)}]"
    body = render_compartments(node.get("compartments", []))
    if kind.endswith(" def"):
        return (
            "  \\sysmldefnode%s{%s}{%s}{%s}{%%\n    %s\n  }\n"
            % (opt, node["id"], esc(kind), esc(node["name"]), body)
        )
    # a usage: header carries "name : Type"
    return (
        "  \\sysmlusagenode%s{%s}{%s}{%s}{%s}{%%\n    %s\n  }\n"
        % (opt, node["id"], esc(kind), esc(node["name"]), esc(node.get("type", "")), body)
    )


def emit_port(port: dict) -> str:
    return "  \\sysmlport{%s}{%s}{%s}{%s}\n" % (
        port["node"],
        port["side"],
        esc(port["name"]),
        port.get("label_side", "above"),
    )


def emit_edge(edge: dict) -> str:
    style = edge.get("style", "reference")
    src = edge["src"] if "src_port" not in edge else "%s-p-%s" % (edge["src"], edge["src_port"])
    dst = edge["dst"] if "dst_port" not in edge else "%s-p-%s" % (edge["dst"], edge["dst_port"])
    bits = [r"  \draw[sysml %s] (%s)" % (style, src)]
    route = edge.get("route")
    if route == "arc-right":
        bits.append(r" to[out=0, in=0, looseness=1.15]")
    elif route == "arc-left":
        bits.append(r" to[out=180, in=180, looseness=1.15]")
    if route and route.startswith("bend-"):
        bits.append(r" to[bend %s]" % route.split("-", 1)[1])
    if not route:
        bits.append(r" --")
    label = edge.get("label")
    if label:
        bits.append(r" node[%s, font=\scriptsize, pos=0.5]{%s}"
                    % (edge.get("label_side", "right"), esc(label)))
    bits.append(" (%s);\n" % dst)
    return "".join(bits)


def emit(model: dict) -> str:
    head = [
        r"\documentclass[tikz,border=10pt]{standalone}",
        r"\usepackage{sysml2tikz}",
        r"\begin{document}",
        r"\begin{tikzpicture}[node distance=%s]" % model.get("node_distance", "12mm"),
        "",
    ]
    body = []
    for node in model.get("nodes", []):
        body.append(emit_node(node))
    body.append("")
    for port in model.get("ports", []):
        body.append(emit_port(port))
    body.append("")
    for edge in model.get("edges", []):
        body.append(emit_edge(edge))
    tail = [r"\end{tikzpicture}", r"\end{document}", ""]
    return "\n".join(head + body + tail)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        model = json.load(fh)
    tex = emit(model)
    with open(argv[2], "w", encoding="utf-8") as fh:
        fh.write(tex)
    print("wrote", argv[2], "(%d bytes, %d nodes, %d edges)"
          % (len(tex), len(model.get("nodes", [])), len(model.get("edges", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
