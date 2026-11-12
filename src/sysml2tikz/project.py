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


def iter_leaf_packages(model):
    """(path, package) for every package that directly owns projectable members.

    Reference models nest packages several levels deep (SimpleVehicleModel
    -> Definitions -> PartDefinitions -> Part...), so a projection that only
    looks one level down sees nothing but packages.
    """
    out = []

    def walk(pkg, path):
        kids = list(getattr(pkg, "children", []) or [])
        mine = [k for k in kids if type(k).__name__ in KIND]
        if mine:
            out.append((path or getattr(pkg, "name", "model"), pkg, mine))
        for k in kids:
            if type(k).__name__ == "Package":
                walk(k, (path + "::" if path else "") + (getattr(k, "name", "") or ""))

    walk(model, getattr(model, "name", "") or "")
    return out


def project_members(members) -> dict:
    """Project an explicit list of elements (one figure's worth)."""
    nodes, types, usages = [], {}, []
    for elem in members:
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
    out = sorted(nodes, key=lambda n: (not n["kind"].endswith(" def"), n["id"]))
    return {"node_distance": "14mm", "nodes": out, "ports": [], "edges": edges}


def _slug(name: str, parent: str = "") -> str:
    base = re.sub(r"\W+", "_", name or "x").strip("_") or "x"
    return (parent + "_" + base) if parent else base


def project_tree(root) -> dict:
    """A whole-part tree: nested part usages become NODES joined by composition.

    This is the projection a parts tree needs (fig-62): walking members as rows
    would flatten the very structure the figure is about.
    """
    nodes: list[dict] = []
    edges: list[dict] = []
    seen: set[str] = set()

    def add(elem, parent_id: str | None, depth: int):
        node = project_element(elem)
        if node is None:
            return
        node = dict(node)
        node["id"] = _slug(node["id"], parent_id or "")
        if node["id"] in seen:
            return
        seen.add(node["id"])
        node["compartments"] = [c for c in node.get("compartments", [])
                                if c["label"] == "attributes"]
        nodes.append(node)
        if parent_id:
            mult = re.search(r"\[([^\]]+)\]", node.get("type", "") or "")
            edge = {"src": node["id"], "dst": parent_id, "style": "composition"}
            if mult:
                edge["label"] = mult.group(1)
            edges.append(edge)
        if depth >= 4:
            return
        for child in getattr(elem, "children", []) or []:
            if type(child).__name__ in KIND:
                add(child, node["id"], depth + 1)

    add(root, None, 0)
    return {"node_distance": "14mm", "nodes": nodes, "ports": [], "edges": edges}


def project_by_package(model) -> list[tuple[str, dict]]:
    """One IR per package that owns elements — the natural figure granularity."""
    out = []
    for path, _pkg, mine in iter_leaf_packages(model):
        # a package of part usages that themselves own parts is a tree, not a list
        trees = [m for m in mine if type(m).__name__ in KIND
                 and not getattr(m, "is_definition", False)
                 and any(type(c).__name__ in KIND for c in getattr(m, "children", []) or [])]
        if trees:
            ir = {"node_distance": "14mm", "nodes": [], "ports": [], "edges": []}
            for root in trees:
                sub = project_tree(root)
                have = {n["id"] for n in ir["nodes"]}
                ir["nodes"] += [n for n in sub["nodes"] if n["id"] not in have]
                ir["edges"] += sub["edges"]
        else:
            ir = project_members(mine)
        out.append((path, ir))
    return out


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
        try:
            import sysmlpy
        except ImportError as exc:
            raise SystemExit(
                "project needs sysmlpy (pip install 'sysml2tikz[parse]'): %s" % exc)

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
