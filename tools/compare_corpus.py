# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Private side-by-side comparison: a reference figure vs our render.

Everything this writes goes to a gitignored directory — the specification's
figures are copyrighted by the organisations listed in the specification and
their licence forbids posting them on a network computer, so they must not enter
the repository, the sdist, a docs site or a paper. This tool exists so the
comparison can still be made locally, and so the reasoning about "how close are
we" is repeatable instead of remembered.

    python3 tools/compare_corpus.py \
        --corpus fig-64-Parts-Interconnection-for-vehicle_b.svg \
        --ours examples/ibd.tex \
        --label interconnection

Writes private/compare/<label>/{reference.png,ours.png,side-by-side.png,report.md}

The report lists the notation rules the pair is meant to exercise, so a reviewer
scores the same things each time rather than "looks fine to me".
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.expanduser("~/proj/third_party/SysML-v2-Release/doc/images/sysml")
OUT = os.path.join(ROOT, "private", "compare")
TECTONIC = os.environ.get("TECTONIC") or os.path.expanduser("~/.local/bin/tectonic")

# which rules a given view kind is supposed to demonstrate
RULES_FOR = {
    "definition and usage": ["D1", "D2", "D3", "D4", "D5", "D7", "D9"],
    "parts tree": ["D1", "D3", "D7", "D8"],
    "interconnection": ["D1", "D3", "D6", "D11"],
    "action flow": ["D3", "D6", "D11"],
    "state": ["D3", "D4", "D11"],
    "requirement": ["D3", "D10", "D11"],
    "verification": ["D3", "D11"],
    "view": ["D3", "D11", "D12"],
}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600, **kw)


def ensure_private(path: str) -> None:
    """Refuse to write anywhere that git would pick up."""
    if not path.startswith(os.path.join(ROOT, "private")):
        raise SystemExit("refusing to write outside private/ (spec figures must stay uncommitted)")


def render_reference(svg: str, dest: str, width: int = 1400) -> None:
    src = os.path.join(CORPUS, svg)
    if not os.path.exists(src):
        raise SystemExit("no such reference figure: %s" % src)
    r = run(["inkscape", src, "--export-type=png", "--export-filename=" + dest,
             "-w", str(width)])
    if r.returncode != 0 or not os.path.exists(dest):
        raise SystemExit("inkscape failed: %s" % (r.stderr.strip()[:200]))


def render_ours(tex: str, workdir: str, dest: str) -> None:
    r = run([TECTONIC, "--outdir", workdir, os.path.join(ROOT, tex)], cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit("tectonic failed: %s" % (r.stderr.strip()[:300] or r.stdout.strip()[:300]))
    pdf = os.path.join(workdir, os.path.splitext(os.path.basename(tex))[0] + ".pdf")
    base = os.path.splitext(dest)[0]
    r = run(["pdftoppm", "-r", "190", "-png", "-singlefile", pdf, base])
    if not os.path.exists(dest):
        raise SystemExit("pdftoppm produced nothing for %s" % pdf)


def side_by_side(ref: str, ours: str, dest: str) -> None:
    r = run(["montage", "-label", "SysML v2 standard (fig)", ref,
             "-label", "sysml2tikz", ours, "-background", "white",
             "-pointsize", "14", "-geometry", "+12+12", "-tile", "2x1", dest])
    if r.returncode != 0:
        raise SystemExit("montage failed: %s" % r.stderr.strip()[:200])


def report(path: str, label: str, svg: str, tex: str, rules: list[dict], sizes: dict) -> None:
    lines = ["# Private comparison — %s" % label, "",
             "* reference: `%s` (OMG SysML v2 reference implementation; **not redistributable**)" % svg,
             "* ours: `%s`" % tex,
             "* reference PNG: %s, ours: %s" % (sizes.get("ref"), sizes.get("ours")),
             "", "Local-only artefact. Do not commit, publish or attach to a paper.", "",
             "## Rules this pair should exercise", ""]
    for r in rules:
        lines.append("* **%s** — %s" % (r["id"], r["statement"]))
    lines += ["", "## Score sheet", "", "| rule | holds in ours? | note |", "|---|---|---|"]
    for r in rules:
        lines.append("| %s | ? | |" % r["id"])
    lines += ["", "Fill the table by looking at `side-by-side.png`; anything that fails is a",
              "renderer defect, not a documentation defect.", ""]
    open(path, "w", encoding="utf-8").write("\n".join(lines))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, help="figure file name in the corpus images dir")
    ap.add_argument("--ours", required=True, help=".tex in this repo")
    ap.add_argument("--label", required=True)
    ap.add_argument("--rules-for", required=True, choices=sorted(RULES_FOR),
                    help="view kind, to pull the relevant rule ids")
    ap.add_argument("--workdir", default="/tmp/sysml2tikz-compare")
    args = ap.parse_args(argv[1:])

    dest = os.path.join(OUT, args.label)
    ensure_private(dest)
    os.makedirs(dest, exist_ok=True)
    os.makedirs(args.workdir, exist_ok=True)

    ref = os.path.join(dest, "reference.png")
    ours = os.path.join(dest, "ours.png")
    render_reference(args.corpus, ref)
    render_ours(args.ours, args.workdir, ours)
    side_by_side(ref, ours, os.path.join(dest, "side-by-side.png"))

    doc = json.load(open(os.path.join(ROOT, "docs", "rules", "rules.json"), encoding="utf-8"))
    by_id = {r["id"]: r for r in doc["rules"]}
    rules = [by_id[i] for i in RULES_FOR[args.rules_for] if i in by_id]

    def dim(p):
        r = run(["identify", "-format", "%wx%h", p])
        return r.stdout.strip() or "?"

    report(os.path.join(dest, "report.md"), args.label, args.corpus, args.ours, rules,
           {"ref": dim(ref), "ours": dim(ours)})

    print("private comparison written to %s" % os.path.relpath(dest, ROOT))
    for f in ("reference.png", "ours.png", "side-by-side.png", "report.md"):
        print("  " + os.path.join(os.path.relpath(dest, ROOT), f))
    print("reminder: this directory is gitignored on purpose — the reference figure is not ours")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
