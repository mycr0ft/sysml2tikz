# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Check docs/notation/figures.json against the reference release checkout.

Answers the question "does this figure have a textual representation, and where"
by *proving* the claimed anchors exist in the claimed file. Without the release
checkout it validates the JSON and reports what it cannot verify, so CI (which
has no corpus) still passes.

    python3 tools/check_figure_sources.py
    python3 tools/check_figure_sources.py --release ~/proj/third_party/SysML-v2-Release

Exit 1 only when a claim is falsified — a claimed anchor missing from the file,
or a claimed figure that is not in the corpus. Missing checkout is a skip.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "docs", "notation", "figures.json")
DEFAULT_RELEASE = os.path.expanduser("~/proj/third_party/SysML-v2-Release")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", default=DEFAULT_RELEASE)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv[1:])

    doc = json.load(open(SPEC, encoding="utf-8"))
    entries = doc["entries"]
    have_text = [e for e in entries if e["text_available"]]
    no_text = [e for e in entries if not e["text_available"]]

    print("figures catalogued: %d (%d with a textual source, %d without)"
          % (len(entries), len(have_text), len(no_text)))

    problems = []
    corpus = os.path.join(args.release, doc["corpus_dir"])
    annex = os.path.join(args.release, doc["annex_a"])
    checked = 0

    if not os.path.isdir(args.release):
        print("release checkout not present at %s — skipping anchor proof" % args.release)
    else:
        for e in have_text:
            src = annex if e.get("source") == "annex_a" else os.path.join(args.release, e["source"])
            if not os.path.exists(src):
                problems.append("%s: source file missing: %s" % (e["figure"], src))
                continue
            text = open(src, encoding="utf-8", errors="replace").read()
            for anchor in e.get("anchors", []):
                checked += 1
                if anchor not in text:
                    problems.append("%s: anchor not found: %r" % (e["figure"], anchor))
            if not args.quiet:
                print("  ok   %-62s %d anchor(s) in %s"
                      % (e["figure"], len(e.get("anchors", [])), os.path.basename(src)))

        if os.path.isdir(corpus):
            present = set(os.listdir(corpus))
            for e in entries:
                if e["figure"] not in present:
                    problems.append("%s: not in the corpus directory" % e["figure"])
        else:
            print("corpus images not present at %s — figure presence not checked" % corpus)

    # a no-text entry must say why
    for e in no_text:
        if not e.get("note"):
            problems.append("%s: text_available=false but no note explaining it" % e["figure"])

    print("\nanchors proven: %d" % checked)
    if problems:
        for p in problems:
            print("  FAIL " + p)
        print("\nFAIL (%d)" % len(problems))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
