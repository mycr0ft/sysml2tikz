# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Build the model -> diagram corpus: .sysml in, one figure per package out.

Two interpreters, because the two halves have different dependencies:

  * sysmlpy's venv parses and projects (it owns antlr4),
  * this repo's .venv renders, because the layout adapter needs diagramboxes +
    drawille.

The parent process orchestrates and records. Renders go to the gitignored
`private/corpus/<label>/`; the committed part is `corpus/<label>/manifest.json`
plus `report.md` — counts, hashes and outcomes only, no model text and no
reference figures.

    python3 tools/build_corpus.py MODEL.sysml --label annex-a
    python3 tools/build_corpus.py MODEL.sysml --label annex-a --min-nodes 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE = os.path.join(ROOT, "private", "corpus")
PUBLIC = os.path.join(ROOT, "corpus")
TECTONIC = os.environ.get("TECTONIC") or os.path.expanduser("~/.local/bin/tectonic")
PY_SYSMLPY = os.environ.get("PY_SYSMLPY") or os.path.expanduser("~/proj/sysmlpy/venv/bin/python")
PY_LAYOUT = os.environ.get("PY_LAYOUT") or os.path.join(ROOT, ".venv", "bin", "python")
SYSMLPY_SRC = os.path.expanduser("~/proj/sysmlpy/src")

PROJECT_STAGE = r'''
import json, sys
sys.path.insert(0, __SRC__)
sys.path.insert(0, __OWN__)
import sysmlpy
from sysml2tikz.project import project_by_package

model_path, outdir = sys.argv[1], sys.argv[2]
model = sysmlpy.loads(open(model_path, encoding="utf-8").read())
out = []
for i, (path, ir) in enumerate(project_by_package(model)):
    slug = "pkg-%02d" % i
    with open(outdir + "/" + slug + ".json", "w", encoding="utf-8") as fh:
        json.dump(ir, fh, indent=1)
    out.append({"slug": slug, "package": path,
                "nodes": len(ir["nodes"]), "edges": len(ir["edges"])})
print(json.dumps(out))
'''


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=1800, **kw)


def slugify(path: str) -> str:
    tail = path.split("::")[-1] or "package"
    return re.sub(r"\W+", "-", tail).strip("-").lower()


def project(model: str, workdir: str) -> list[dict]:
    code = (PROJECT_STAGE
            .replace("__SRC__", repr(SYSMLPY_SRC))
            .replace("__OWN__", repr(os.path.join(ROOT, "src"))))
    r = run([PY_SYSMLPY, "-c", code, model, workdir])
    if r.returncode != 0:
        raise SystemExit("projection failed:\n%s\n%s" % (r.stdout[-800:], r.stderr[-1500:]))
    return json.loads(r.stdout.strip().splitlines()[-1])


def render(ir_path: str, out_dir: str) -> dict:
    tex = os.path.join(out_dir, os.path.splitext(os.path.basename(ir_path))[0] + ".tex")
    r = run([PY_LAYOUT, os.path.join(ROOT, "gen", "layout_adapter.py"), ir_path, tex])
    if r.returncode != 0:
        return {"ok": False, "stage": "layout", "error": (r.stderr or r.stdout).strip()[-400:]}
    r = run([TECTONIC, "--outdir", out_dir, tex])
    if r.returncode != 0:
        return {"ok": False, "stage": "compile", "error": (r.stdout + r.stderr).strip()[-400:]}
    pdf = os.path.splitext(tex)[0] + ".pdf"
    png = os.path.splitext(tex)[0]
    run(["pdftoppm", "-r", "150", "-png", "-singlefile", pdf, png])
    routing = run([sys.executable, os.path.join(ROOT, "tools", "check_routing.py"), tex])

    # a 9000x400 strip is technically a render and practically unreadable
    dims = run(["identify", "-format", "%w %h", png + ".png"]).stdout.split()
    width, height = (int(dims[0]), int(dims[1])) if len(dims) == 2 else (0, 0)
    # a 9000x400 smear is unreadable; a 900x140 row of four boxes is fine
    readable = bool(width and height) and width <= 4000 and (
        (width / height) <= 6 or width <= 1600)
    return {"ok": True, "tex": tex, "pdf": pdf, "png": png + ".png",
            "px": "%dx%d" % (width, height), "readable": readable,
            "routing_clean": routing.returncode == 0,
            "routing_detail": "" if routing.returncode == 0 else routing.stdout.strip()[-300:]}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--label", required=True)
    ap.add_argument("--max-nodes", type=int, default=60)
    ap.add_argument("--min-nodes", type=int, default=2,
                    help="skip figures with fewer nodes (a one-box figure teaches nothing)")
    args = ap.parse_args(argv[1:])

    model = os.path.abspath(args.model)
    if not os.path.exists(model):
        raise SystemExit("no such model: %s" % model)
    work = os.path.join(PRIVATE, args.label, "_ir")
    out = os.path.join(PRIVATE, args.label)
    os.makedirs(work, exist_ok=True)
    os.makedirs(out, exist_ok=True)

    digest = hashlib.sha256(open(model, "rb").read()).hexdigest()
    packages = project(model, work)

    results = []
    for pkg in packages:
        entry = dict(pkg)
        entry["slug"] = slugify(pkg["package"]) + "-" + pkg["slug"]
        if pkg["nodes"] > args.max_nodes:
            entry.update(status="skipped",
                         why="%d nodes exceeds --max-nodes %d (a single rank becomes a strip)"
                             % (pkg["nodes"], args.max_nodes))
            results.append(entry)
            continue
        if pkg["nodes"] < args.min_nodes:
            entry.update(status="skipped", why="fewer than %d nodes" % args.min_nodes)
            results.append(entry)
            continue
        ir_path = os.path.join(work, pkg["slug"] + ".json")
        r = render(ir_path, out)
        entry.update(status="rendered" if r["ok"] else "failed", **r)
        results.append(entry)

    ok = [r for r in results if r["status"] == "rendered"]
    failed = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] == "skipped"]

    manifest = {"model": os.path.basename(model), "sha256": digest,
                "packages": len(packages), "rendered": len(ok),
                "failed": len(failed), "skipped": len(skipped),
                "routing_clean": sum(1 for r in ok if r.get("routing_clean")),
                "readable": sum(1 for r in ok if r.get("readable")),
                "entries": results}
    public = os.path.join(PUBLIC, args.label)
    os.makedirs(public, exist_ok=True)
    json.dump(manifest, open(os.path.join(public, "manifest.json"), "w", encoding="utf-8"),
              indent=1, sort_keys=True)

    lines = ["# Corpus run — %s" % args.label, "",
             "* model: `%s` (sha256 %s…)" % (os.path.basename(model), digest[:12]),
             "* packages with elements: %d · rendered: %d · failed: %d · skipped: %d"
             % (len(packages), len(ok), len(failed), len(skipped)),
             "* routing clean: %d/%d rendered" % (manifest["routing_clean"], len(ok)),
             "* readable (≤4000 px wide, aspect ≤6:1): %d/%d"
             % (sum(1 for r in ok if r.get("readable")), len(ok)),
             "* renders live in `private/corpus/%s/` (gitignored — model content is EPL-2.0 "
             "and not redistributed here)" % args.label, "",
             "| package | nodes | edges | status | note |", "|---|---|---|---|---|"]
    for r in results:
        note = ""
        if r["status"] == "failed":
            note = "%s: %s" % (r.get("stage", "?"), (r.get("error") or "").replace("|", "/")[:80])
        elif r["status"] == "rendered" and not r.get("readable"):
            note = "unreadable strip (%s) — layout puts every sibling at one rank" % r.get("px")
        elif r["status"] == "rendered" and not r.get("routing_clean"):
            note = "routing not clean"
        elif r["status"] == "skipped":
            note = r.get("why", "")
        lines.append("| `%s` | %d | %d | %s | %s |"
                     % (r["package"].split("::")[-1] or r["package"], r["nodes"],
                        r["edges"], r["status"], note))
    lines += ["", "Regenerate with:", "", "```",
              "python3 tools/build_corpus.py %s --label %s" % (args.model, args.label), "```", ""]
    open(os.path.join(public, "report.md"), "w", encoding="utf-8").write("\n".join(lines))

    print("packages %d | rendered %d | failed %d | skipped %d"
          % (len(packages), len(ok), len(failed), len(skipped)))
    print("manifest: %s" % os.path.relpath(os.path.join(public, "manifest.json"), ROOT))
    print("report:   %s" % os.path.relpath(os.path.join(public, "report.md"), ROOT))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
