# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Render docs/notation/notation.json into markdown cards + an index.

One source of truth, two audiences: the JSON is what an agent loads and greps;
the markdown is what a human (or an agent with a markdown-only toolset) reads.
They cannot drift because the markdown is generated and gated by a golden diff.

    python3 tools/render_notation.py            # write cards + index
    python3 tools/render_notation.py --check    # exit 1 if committed files differ
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTATION = os.path.join(ROOT, "docs", "notation")
CARDS = os.path.join(NOTATION, "cards")


def slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace("/", "-")


def render_card(view: dict) -> str:
    out = ["# %s" % view["view"], ""]
    if view.get("also_called"):
        out += ["Also called: " + ", ".join(view["also_called"]), ""]
    out += ["SysML v2 view: `%s`" % view.get("sysml_v2_view", "n/a"), ""]
    out += ["## Purpose", "", view["purpose"].strip(), ""]

    frame = view.get("frame") or {}
    out += ["## How to recognise it", ""]
    if frame.get("shown"):
        out += ["* An enclosing frame whose header reads %s." % frame.get("header", "`<kind> <name>`")]
    for cue in view.get("identify_by", []):
        out += ["* " + cue]
    out += [""]

    nodes = view.get("nodes") or []
    if nodes:
        out += ["## Nodes", "", "| shape | what it means | text inside |", "|---|---|---|"]
        for n in nodes:
            out += ["| %s | %s | %s |" % (n.get("shape", ""), n.get("means", ""), n.get("text", ""))]
        out += [""]

    edges = view.get("edges") or []
    if edges:
        out += ["## Edges", "", "| style | ends | what it means |", "|---|---|---|"]
        for e in edges:
            out += ["| %s | %s | %s |" % (e.get("style", ""), e.get("ends", ""), e.get("means", ""))]
        out += [""]

    if view.get("keywords"):
        out += ["## Keyword lines", "", "`" + "`, `".join(view["keywords"]) + "`", ""]

    if view.get("confuse_with"):
        out += ["## Do not confuse with", ""]
        for c in view["confuse_with"]:
            out += ["* **%s** — %s" % (c["view"], c["how_to_tell"])]
        out += [""]

    if view.get("notes"):
        out += ["## Notes", "", view["notes"].strip(), ""]

    src = view.get("figure")
    status = "verified against the figure" if view.get("verified_against_figure") else "NOT yet verified against a figure"
    out += ["## Evidence", ""]
    out += ["* reference figure: `%s` (%s)" % (src or "none", status)]
    out += ["* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`"]
    out += [""]
    return "\n".join(out)


def render_index(doc: dict) -> str:
    out = ["# SysML v2 notation cards — for vision models", "",
           doc["about"].strip(), "",
           "Machine-readable twin: [`notation.json`](notation.json). These cards are generated",
           "from it by `tools/render_notation.py`; edit the JSON, not the markdown.", "",
           "## Identifying a diagram type", "",
           doc["decision_tree"].strip(), "",
           "## The cards", "",
           "| view | also called | recognise by | figure | verified |", "|---|---|---|---|---|"]
    for v in doc["views"]:
        cue = (v.get("identify_by") or [""])[0].replace("|", "/")
        out += ["| [%s](cards/%s.md) | %s | %s | %s | %s |"
                % (v["view"], slug(v["view"]),
                   ", ".join(v.get("also_called", [])) or "—",
                   cue[:90],
                   "`%s`" % v["figure"] if v.get("figure") else "—",
                   "yes" if v.get("verified_against_figure") else "no")]
    out += ["", "## Reading order for an agent", "", doc["reading_order"].strip(), ""]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    with open(os.path.join(NOTATION, "notation.json"), encoding="utf-8") as fh:
        doc = json.load(fh)
    os.makedirs(CARDS, exist_ok=True)
    files: dict[str, str] = {
        os.path.join(NOTATION, "index.md"): render_index(doc),
    }
    for view in doc["views"]:
        files[os.path.join(CARDS, slug(view["view"]) + ".md")] = render_card(view)

    stale = []
    for path, content in files.items():
        text = content.rstrip() + "\n"
        if check:
            current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if current != text:
                stale.append(os.path.relpath(path, ROOT))
        else:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
    if check:
        if stale:
            print("stale (re-run tools/render_notation.py):")
            for s in stale:
                print("  " + s)
            return 1
        print("notation cards are up to date (%d files)" % len(files))
        return 0
    print("wrote %d file(s)" % len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
