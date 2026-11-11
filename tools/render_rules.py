# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Render docs/rules/rules.json into the rules document and the validation checklist.

Same discipline as the notation cards: one JSON source, generated markdown, and a
--check mode so the two cannot drift.

    python3 tools/render_rules.py            # write 02-drawing-rules.md + 04-validation-checklist.md
    python3 tools/render_rules.py --check    # exit 1 if the committed files differ
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "docs", "rules")

AREA_ORDER = [
    "definition vs usage", "boxes", "compartments", "rows", "ports",
    "composition", "specialisation", "requirements", "cross-cutting edges",
    "frames", "marks", "metamodel",
]


def render_rules(doc: dict) -> str:
    out = ["# 02 — Diagramming rules", "",
           doc["about"].strip(), "",
           "Conventions: " + doc["conventions"].strip(), "",
           "Rule ids are cited by the checklist in [`04-validation-checklist.md`](04-validation-checklist.md).", ""]
    areas: dict[str, list[dict]] = {}
    for r in doc["rules"]:
        areas.setdefault(r["area"], []).append(r)
    for area in AREA_ORDER + [a for a in areas if a not in AREA_ORDER]:
        if area not in areas:
            continue
        out += ["---", "", "## %s" % area.replace("-", " ").capitalize(), ""]
        for r in areas[area]:
            out += ["### Rule %s — %s" % (r["id"], r["statement"].rstrip(".")), ""]
            out += ["*Why:* " + r["why"].strip(), ""]
            out += ["```", "✅ " + r["correct"].strip(), "",
                    "❌ " + r["wrong"].strip(), "```", ""]
            if r.get("evidence"):
                out += ["*Evidence:* %s" % r["evidence"].strip(), ""]
    return "\n".join(out)


def render_checklist(doc: dict) -> str:
    out = ["# 04 — Validation checklist (diagrams)", "",
           "Run this **before** returning a diagram, the way the textual checklist is run before",
           "returning `.sysml` text. Each gate cites the rule it enforces. Gates marked",
           "**[auto]** are checked by `tools/check_rules.py` against the notation IR and the",
           "layout geometry; the rest need eyes or a vision model.", ""]
    sections: dict[str, list[dict]] = {}
    for r in doc["rules"]:
        sections.setdefault(r["area"], []).append(r)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    idx = 0
    for area in AREA_ORDER + [a for a in sections if a not in AREA_ORDER]:
        if area not in sections:
            continue
        letter = letters[idx]
        idx += 1
        out += ["---", "", "## %s. %s" % (letter, area.replace("-", " ").capitalize()), ""]
        for n, r in enumerate(sections[area], start=1):
            tag = " **[auto]**" if r.get("checkable", "visual") != "visual" else ""
            out += ["- [ ] **%s%d.** %s%s" % (letter, n, r["statement"].rstrip("."), tag)]
        out += [""]
    out += ["---", "",
            "## Summary of what a machine can enforce", "",
            "| rule | area | how it is checked |", "|---|---|---|"]
    for r in doc["rules"]:
        if r.get("checkable", "visual") != "visual":
            out += ["| %s | %s | %s |" % (r["id"], r["area"], r.get("check", "—"))]
    out += ["", "Everything else is visual: a vision model or a human must look. The cards in",
            "[`../notation/`](../notation/index.md) describe what to look for.", ""]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    with open(os.path.join(RULES, "rules.json"), encoding="utf-8") as fh:
        doc = json.load(fh)
    files = {
        os.path.join(RULES, "02-drawing-rules.md"): render_rules(doc),
        os.path.join(RULES, "04-validation-checklist.md"): render_checklist(doc),
    }
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
            print("stale (re-run tools/render_rules.py):")
            for s in stale:
                print("  " + s)
            return 1
        print("rule documents are up to date (%d files)" % len(files))
        return 0
    print("wrote %d file(s)" % len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
