#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""verify.py — stage 6 gates for the sysml2tikz pipeline.

    python3 tools/verify.py            # golden diff + compile + geometry
    python3 tools/verify.py --vision   # also score against the corpus figure

Gates, cheapest first:
  1. golden .tex    re-emit model.json and diff against the committed gen/out.tex;
                    a change here is a change in the notation or the emitter,
                    which is exactly what should require a human look.
  2. compile        tectonic every .tex in the repo; fail on missing characters
                    (the nullfont class of error) as well as on exit status.
  3. geometry       ports within 2pt of a node wall, no two node boxes overlapping —
                    parsed from the geometry sidecar the layout adapter writes, so
                    it asserts the numbers the renderer actually used.
  4. vision         (opt-in) render the corpus SVG and our PNG, ask the cloud VLM
                    for a notation score and a defect list.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "gen")
TECTONIC = (os.environ.get("TECTONIC")
            or shutil.which("tectonic")
            or os.path.expanduser("~/.local/bin/tectonic"))
CORPUS = os.path.expanduser(
    "~/proj/third_party/SysML-v2-Release/doc/images/sysml")

fails: list[str] = []
notes: list[str] = []


def run(cmd, cwd=None, timeout=300):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


# ------------------------------------------------------------------ 1 golden
def gate_golden() -> None:
    out = os.path.join(GEN, "out.tex")
    tmp = os.path.join(GEN, "build", "golden.tex")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    r = run([sys.executable, os.path.join(GEN, "emit_tex.py"),
             os.path.join(GEN, "model.json"), tmp])
    if r.returncode != 0:
        fails.append("golden: emitter failed: %s" % r.stderr.strip()[:300])
        return
    a = open(out, encoding="utf-8").read()
    b = open(tmp, encoding="utf-8").read()
    if a != b:
        fails.append("golden: gen/out.tex differs from a fresh emit — "
                     "re-run the emitter and review the diff")
    else:
        notes.append("golden: emitter output is byte-identical")


# ----------------------------------------------------------------- 2 compile
def gate_compile() -> None:
    targets = [os.path.join(ROOT, "demo.tex"),
               os.path.join(GEN, "out.tex"),
               os.path.join(GEN, "laid_out.tex"),
               os.path.join(GEN, "veh.tex")]
    for tex in targets:
        if not os.path.exists(tex):
            fails.append("compile: missing %s" % os.path.relpath(tex, ROOT))
            continue
        r = run([TECTONIC, "--keep-logs", tex], cwd=os.path.dirname(tex))
        log = tex.replace(".tex", ".log")
        bad = ""
        if os.path.exists(log):
            text = open(log, encoding="utf-8", errors="replace").read()
            for pat in ("Missing character", "Missing $", "Undefined control sequence",
                        "Package PGF Math Error"):
                if pat in text:
                    bad = pat
                    break
        if r.returncode != 0 or bad:
            fails.append("compile: %s failed (%s)"
                         % (os.path.relpath(tex, ROOT), bad or r.stderr.strip()[:200]))
        else:
            notes.append("compile: %s ok" % os.path.relpath(tex, ROOT))


# ---------------------------------------------------------------- 3 geometry
def gate_geometry() -> None:
    import glob
    paths = sorted(glob.glob(os.path.join(GEN, "geometry-*.json")))
    if not paths:
        fails.append("geometry: no gen/geometry-*.json (run the layout adapter)")
        return
    for path in paths:
        check_one_geometry(path)


def check_one_geometry(path: str) -> None:
    g = json.load(open(path, encoding="utf-8"))
    nodes, ports = g["nodes"], g["ports"]
    for name, p in ports.items():
        nid, side = name.split(".")
        n = nodes[nid]
        if side in ("east", "west"):
            wall = n["cx"] + (n["w"] / 2 if side == "east" else -n["w"] / 2)
            delta = abs(p["x"] - wall)
        else:
            wall = n["cy"] + (n["h"] / 2 if side == "north" else -n["h"] / 2)
            delta = abs(p["y"] - wall)
        if delta > 2.0:
            fails.append("geometry: port %s is %.1fpt off its wall (max 2.0)" % (name, delta))
    ids = sorted(nodes)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            na, nb = nodes[a], nodes[b]
            if (abs(na["cx"] - nb["cx"]) < (na["w"] + nb["w"]) / 2 and
                    abs(na["cy"] - nb["cy"]) < (na["h"] + nb["h"]) / 2):
                fails.append("geometry: nodes %s and %s overlap" % (a, b))
    if not any(f.startswith("geometry:") for f in fails):
        notes.append("geometry %s: %d node(s), %d port(s), no overlap, ports on walls"
                     % (os.path.basename(path), len(nodes), len(ports)))


# ------------------------------------------------------------------- 4 vision
def gate_vision() -> None:
    corpus_svg = os.path.join(CORPUS, "fig-57-Part-Definition-for-Vehicle.svg")
    ours = os.path.join(GEN, "laid_out.pdf")
    if not os.path.exists(corpus_svg) or not os.path.exists(ours):
        fails.append("vision: missing corpus figure or render")
        return
    tmp = os.path.join(GEN, "build")
    os.makedirs(tmp, exist_ok=True)
    ref = os.path.join(tmp, "corpus.png")
    got = os.path.join(tmp, "ours.png")
    run(["inkscape", corpus_svg, "--export-type=png", "--export-filename=" + ref, "-w", "1200"])
    run(["pdftoppm", "-r", "190", "-png", "-singlefile", ours,
         os.path.join(tmp, "ours")])
    shutil.move(os.path.join(tmp, "ours.png"), got)
    prompt = ("Score the RIGHT image as a SysML v2 notation figure: 10 for correct keywords, "
              "compartments, port squares on walls and edge arrowheads. The LEFT image is the "
              "reference style. If you cannot read an image, say unreadable. End with a line "
              "'Score: N'.")
    r = run(["ollama", "run", "gemma4:31b-cloud", prompt, ref, got], timeout=600)
    m = re.search(r"Score:\s*([0-9.]+)", r.stdout or "")
    if m:
        notes.append("vision: %s/10" % m.group(1))
    else:
        fails.append("vision: no score returned (ollama unavailable or model silent)")


def gate_notation() -> None:
    r = run([sys.executable, os.path.join(ROOT, "tools", "render_notation.py"), "--check"])
    if r.returncode != 0:
        fails.append("notation: cards are stale — %s" % (r.stdout.strip().splitlines() or [""])[0])
    else:
        notes.append("notation: %s" % (r.stdout.strip() or "cards current"))


def main(argv: list[str]) -> int:
    gate_golden()
    gate_notation()
    gate_compile()
    gate_geometry()
    if "--vision" in argv:
        gate_vision()
    for n in notes:
        print("  ok   ", n)
    for f in fails:
        print("  FAIL ", f)
    print()
    print("PASS" if not fails else "FAIL (%d)" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
