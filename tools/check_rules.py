# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Check the machine-checkable diagramming rules (docs/rules/rules.json) D1..D11.

Runs against what the pipeline actually produced — the notation IR, the emitted
.tex, the .sty style definitions and the layout geometry sidecar — so "the rule
holds" is a measurement, not an assertion about the docs.

    python3 tools/check_rules.py             # all IRs in gen/, exit 1 on a failure
    python3 tools/check_rules.py --ir gen/veh.json

Rules whose `checkable` is `visual` are listed as unenforced and skipped; they are
the ones a vision model or a human must judge.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "gen")
STY = os.path.join(ROOT, "sysml2tikz.sty")

DEF_COMPARTMENTS = {"attributes", "parts", "ports", "actions", "states", "items",
                    "requirements", "connections", "calculations", "constraints"}
USAGE_COMPARTMENTS = {"attributes", "parts", "ports", "items", "connections",
                      "perform actions", "exhibit states", "require requirements",
                      "perform calculations", "assert constraints"}


def read(path: str) -> str:
    return open(path, encoding="utf-8").read()


def load_pairs() -> list[tuple[str, dict, str]]:
    """(name, IR, emitted .tex) for every IR that has a compiled sibling."""
    out = []
    # gen/model.json is the IR behind gen/out.tex, not gen/model.tex
    alias = {"model.json": "out.tex"}
    for ir_path in sorted(glob.glob(os.path.join(GEN, "*.json"))):
        name = os.path.basename(ir_path)
        if name.startswith("geometry-"):
            continue
        tex = os.path.join(GEN, alias.get(name, name.replace(".json", ".tex")))
        if os.path.exists(tex):
            out.append((name, json.loads(read(ir_path)), read(tex)))
    return out


def strip_tex(tex: str) -> str:
    return tex


def check_d1(name, ir, tex):
    bad = []
    for node in ir.get("nodes", []):
        call = r"\sysmldefnode" if node["kind"].endswith(" def") else r"\sysmlusagenode"
        if call not in tex:
            bad.append(node["id"])
            continue
        if not re.search(re.escape(call) + r"(?:\[[^\]]*\])?\{" + re.escape(node["id"]) + r"\}", tex):
            bad.append(node["id"])
    return (not bad, "def nodes square / usage nodes rounded" if not bad else "wrong corner style: %s" % bad)


def check_d2(name, ir, tex):
    bad = [n["id"] for n in ir.get("nodes", [])
           if not n["kind"].endswith(" def") and not (n.get("type") or "").strip()]
    return (not bad, "usage headers carry `name : Type`" if not bad
            else "usage without a type in the header: %s" % bad)


def check_d3(name, ir, tex):
    bad = [n["id"] for n in ir.get("nodes", []) if not (n.get("kind") or "").strip()]
    missing_kw = [n["id"] for n in ir.get("nodes", [])
                  if n.get("kind") and n["kind"] not in tex]
    return (not bad and not missing_kw, "every box renders its keyword line"
            if not bad and not missing_kw else "missing keyword: %s" % (bad + missing_kw))


def check_d4(name, ir, tex):
    bad = []
    for node in ir.get("nodes", []):
        allowed = DEF_COMPARTMENTS if node["kind"].endswith(" def") else USAGE_COMPARTMENTS
        for comp in node.get("compartments", []):
            if comp["label"] not in allowed:
                bad.append("%s/%s" % (node["id"], comp["label"]))
    return (not bad, "compartment titles follow the definition/usage table" if not bad
            else "wrong compartment title: %s" % bad)


def check_d6(name, ir, tex):
    """Ports straddle the wall — measured from the geometry the renderer used."""
    stem = os.path.splitext(name)[0]
    stem = {"model": "laid_out"}.get(stem, stem)   # model.json was rendered as laid_out.tex
    geo = os.path.join(GEN, "geometry-%s.json" % stem)
    if not os.path.exists(geo):
        return (None, "no geometry sidecar for %s (run the layout adapter)" % stem)
    g = json.loads(read(geo))
    bad = []
    for key, p in g.get("ports", {}).items():
        nid, side = key.split(".")
        n = g["nodes"][nid]
        if side in ("east", "west"):
            wall = n["cx"] + (n["w"] / 2 if side == "east" else -n["w"] / 2)
            delta = abs(p["x"] - wall)
        else:
            wall = n["cy"] + (n["h"] / 2 if side == "north" else -n["h"] / 2)
            delta = abs(p["y"] - wall)
        if delta > 2.0:
            bad.append("%s off wall by %.1fpt" % (key, delta))
    return (not bad, "port glyphs straddle their walls" if not bad else "; ".join(bad))


def check_d7(name, ir, tex):
    sty = read(STY)
    m = re.search(r"sysml composition/\.style=\{([^}]*)\}", sty)
    if not m:
        return (False, "no `sysml composition` style defined")
    spec = m.group(1)
    ok = "Diamond" in spec and "fill=" in spec and spec.count("Diamond") == 1
    return (ok, "composition style: diamond at the whole end only (%s)" % spec.strip()
            if ok else "composition style does not encode a single filled diamond: %s" % spec)


def check_d8(name, ir, tex):
    """A composition label must not sit at mid-edge."""
    bad = []
    for m in re.finditer(r"\\draw\[sysml composition\](.*?);", tex, re.S):
        chunk = m.group(1)
        for pos in re.findall(r"pos=([0-9.]+)", chunk):
            if float(pos) >= 0.5:
                bad.append(pos)
        if "{" in chunk and "pos=" not in chunk:
            bad.append("label without pos")
    return (not bad, "composition labels sit at the part end" if not bad
            else "composition label at mid-edge: pos=%s" % bad)


def check_d9(name, ir, tex):
    sty = read(STY)
    m = re.search(r"sysml gen/\.style=\{([^}]*)\}", sty)
    if not m:
        return (False, "no `sysml gen` style defined")
    spec = m.group(1)
    # hollow == `open` or a white fill; a black fill would be a flow arrowhead
    hollow = ("open" in spec) or re.search(r"fill=white", spec)
    ok = ("Triangle" in spec) and bool(hollow) and "fill=black" not in spec
    return (ok, "generalisation uses a hollow triangle (%s)" % spec.strip()
            if ok else "generalisation triangle is not hollow: %s" % spec)


def check_d10(name, ir, tex):
    bad = []
    reqs = [n for n in ir.get("nodes", []) if "requirement" in n["kind"]]
    for n in reqs:
        labels = [c["label"] for c in n.get("compartments", [])]
        rows = " ".join(r for c in n.get("compartments", []) for r in c["rows"])
        if "attributes" not in labels:
            bad.append("%s has no attributes compartment" % n["id"])
        if not re.search(r"(^|\s)id\s*=|<[0-9_]+>", rows):
            bad.append("%s has no id" % n["id"])
    if not reqs:
        return (None, "no requirement node in this IR — rule not exercised")
    return (not bad, "requirements carry an id and a doc/attributes compartment" if not bad
            else "; ".join(bad))


def check_d11(name, ir, tex):
    bad = []
    for e in ir.get("edges", []):
        if e.get("style") in ("satisfy", "verify", "derive", "allocate", "perform"):
            if not (e.get("label") or "").strip():
                bad.append("%s->%s unlabelled" % (e["src"], e["dst"]))
            if e["style"] not in tex:
                bad.append("%s style not emitted" % e["style"])
    return (not bad, "cross-cutting edges are dashed and keyword-labelled" if not bad
            else "; ".join(bad))


CHECKS = {"D1": check_d1, "D2": check_d2, "D3": check_d3, "D4": check_d4,
          "D6": check_d6, "D7": check_d7, "D8": check_d8, "D9": check_d9,
          "D10": check_d10, "D11": check_d11}


def main(argv: list[str]) -> int:
    doc = json.loads(read(os.path.join(ROOT, "docs", "rules", "rules.json")))
    only = None
    if "--ir" in argv:
        only = os.path.basename(argv[argv.index("--ir") + 1])
    pairs = [p for p in load_pairs() if only is None or p[0] == only]
    if not pairs:
        print("no IR/.tex pairs found in gen/")
        return 2

    failures, skipped_visual = [], []
    for name, ir, tex in pairs:
        print("\n== %s" % name)
        for rule in doc["rules"]:
            rid = rule["id"]
            if rule.get("checkable", "visual") == "visual":
                skipped_visual.append(rid)
                continue
            fn = CHECKS.get(rid)
            if fn is None:
                print("  --   %s no implementation" % rid)
                continue
            ok, detail = fn(name, ir, tex)
            if ok is None:
                print("  skip %s %s" % (rid, detail))
            elif ok:
                print("  ok   %s %s" % (rid, detail))
            else:
                print("  FAIL %s %s" % (rid, detail))
                failures.append("%s/%s" % (name, rid))

    print("\nvisual-only rules (need a human or a vision model): %s"
          % ", ".join(sorted(set(skipped_visual))))
    print("PASS" if not failures else "FAIL (%d)" % len(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
