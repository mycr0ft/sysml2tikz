#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""from_sysml.py — stage 1+2 of the sysml2tikz pipeline.

sysmlpy model -> notation IR (the JSON the emitter consumes).

Scope of this first cut, stated plainly:
  * top-level definitions and usages (package children, one level deep) become
    BOXES; their members become compartment ROWS, not separate boxes.
  * a row is the member's own SysML text (`dump()`), which already carries the
    notation the corpus prints: `:>` subsetting, `:>>Owner::x` redefinition,
    `= value`, `[mult]`.
  * keyword = the element's SysML kind + " def" for definitions
    (`part def` / `part`, `attribute def` / `attribute`, ...).
  * compartment label follows the corpus: bare noun on definitions
    (`attributes`, `ports`), verb + noun on usages (`perform actions`,
    `exhibit states`).
  * one composition edge is emitted for a top-level usage whose type resolves
    to another top-level definition.

Not handled yet (deliberate): nested part trees as nodes, ports as routing
anchors taken from the model, requirement satisfy edges from the model,
view/viewpoint frames.

Usage:
    PYTHONPATH=~/proj/sysmlpy/src python3 from_sysml.py model.sysml out.json
"""
from __future__ import annotations

import json
import os
import re
import sys



KIND = {
    "Part": "part", "Attribute": "attribute", "Port": "port", "Item": "item",
    "Action": "action", "State": "state", "Requirement": "requirement",
    "Calculation": "calc", "Constraint": "constraint", "Allocation": "allocation",
    "Interface": "interface", "Enumeration": "enum", "Connection": "connection",
}

# class -> compartment label for a DEFINITION, and for a USAGE
COMPARTMENT = {
    "Attribute": ("attributes", "attributes"),
    "Part": ("parts", "parts"),
    "Port": ("ports", "ports"),
    "Item": ("items", "items"),
    "Action": ("actions", "perform actions"),
    "State": ("states", "exhibit states"),
    "Requirement": ("requirements", "require requirements"),
    "Calculation": ("calculations", "perform calculations"),
    "Constraint": ("constraints", "assert constraints"),
    "Connection": ("connections", "connections"),
}

HEADER_RE = re.compile(
    r"^\s*(?:\w+\s+(?:def\s+)?)?"   # keyword, optionally 'def'
    r"(?P<name>[A-Za-z_][\w]*(?:::[A-Za-z_][\w]*)?)"   # name or qualified name
    r"\s*(?::\s*(?P<type>[A-Za-z_][\w:]*(?:\[[^\]]*\])?))?"  # optional : Type
)


def first_line(text: str) -> str:
    return text.strip().splitlines()[0] if text.strip() else ""


ROW_KEYWORD_RE = re.compile(
    r"^(?:abstract\s+)?(?:part|attribute|port|item|action|state|requirement|"
    r"calc|constraint|allocation|interface|connection|enum|ref)\s+(?:def\s+)?")


def dump_row(elem) -> str:
    """A member's SysML text as one notation row.

    The corpus prints compartment rows WITHOUT the member's own keyword
    ("power : PowerValue", not "attribute power : PowerValue"), so the leading
    keyword is stripped — the compartment label already carries it.
    """
    text = elem.dump().strip()
    text = " ".join(line.strip() for line in text.splitlines())
    text = text.rstrip(";").split("{")[0].strip()
    return ROW_KEYWORD_RE.sub("", text)


def classify(elem):
    cls = type(elem).__name__
    return KIND.get(cls), COMPARTMENT.get(cls)


skipped: list[str] = []


def project_element(elem) -> dict | None:
    kind, compartments = classify(elem)
    if kind is None:
        return None
    is_def = bool(getattr(elem, "is_definition", False))
    header = first_line(elem.dump())
    m = HEADER_RE.match(header)
    if not m or not m.group("name"):
        return None
    node = {
        "id": re.sub(r"\W+", "_", m.group("name")),
        "kind": kind + (" def" if is_def else ""),
        "name": m.group("name"),
    }
    type_field = m.group("type")
    if type_field and not is_def:
        node["type"] = type_field
    # members -> rows, grouped into corpus-ordered compartments
    order = ["attributes", "parts", "ports", "actions", "states",
             "requirements", "items", "connections", "calculations", "constraints"]
    buckets: dict[str, list[str]] = {}
    for child in getattr(elem, "children", []) or []:
        ckind, ccomp = classify(child)
        if ckind is None or ccomp is None:
            continue
        label = ccomp[0] if is_def else ccomp[1]
        row = dump_row(child)
        if row.strip() in ("action", "perform", "perform action"):
            # sysmlpy keeps no name for `perform x;` (dump() -> "perform action ;")
            skipped.append("%s: %s" % (type(child).__name__, elem.dump().split()[0]))
            continue
        if is_def and type(child).__name__ == "Action" and row:
            row = "*perform* " + row
        if not row:
            continue
        buckets.setdefault(label, []).append(row)
    node["compartments"] = [
        {"label": label, "rows": buckets[label]}
        for label in sorted(buckets, key=lambda l: order.index(l) if l in order else 99)
    ]
    return node


def project(model) -> dict:
    nodes: list[dict] = []
    types: dict[str, str] = {}          # definition name -> node id
    usages: list[tuple[str, str, str | None]] = []   # (node id, type name, mult)

    for pkg in getattr(model, "children", []) or []:
        for elem in getattr(pkg, "children", []) or []:
            node = project_element(elem)
            if node is None:
                continue
            nodes.append(node)
            if node["kind"].endswith(" def"):
                types[node["name"]] = node["id"]
            elif node.get("type"):
                mult = re.search(r"\[([^\]]+)\]", node["type"])
                base = re.sub(r"\s*\[[^\]]*\]", "", node["type"]).strip()
                usages.append((node["id"], base, mult.group(1) if mult else None))

    edges = []
    for node_id, type_name, mult in usages:
        target = types.get(type_name.split("::")[-1])
        if target:
            edge = {"src": node_id, "dst": target, "style": "composition"}
            if mult:
                edge["label"] = mult
            edges.append(edge)

    # keep definitions above their usages
    out_nodes = sorted(nodes, key=lambda n: (not n["kind"].endswith(" def"), n["id"]))
    ir = {"node_distance": "14mm", "nodes": out_nodes, "ports": [], "edges": edges}
    if skipped:
        ir["projection_notes"] = {
            "skipped_members": sorted(set(skipped)),
            "why": "sysmlpy does not retain a name for these members (e.g. a bare "
                   "`perform x;` parses to 'perform action ;'), so there is no row to print",
        }
    return ir


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        import sysmlpy
    except ImportError:                    # dev checkout without an install
        sys.path.insert(0, os.path.expanduser("~/proj/sysmlpy/src"))
        import sysmlpy

    with open(argv[1], encoding="utf-8") as fh:
        model = sysmlpy.loads(fh.read())
    ir = project(model)
    with open(argv[2], "w", encoding="utf-8") as fh:
        json.dump(ir, fh, indent=2)
    print("projected %d node(s), %d edge(s) -> %s"
          % (len(ir["nodes"]), len(ir["edges"]), argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
