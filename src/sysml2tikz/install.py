# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Install the bundled ``sysml2tikz.sty`` where a TeX distribution will find it.

`--copy-sty` is the zero-configuration route (the file lands beside your
document). This is the other one: put it in the user tree once, then
``\\usepackage{sysml2tikz}`` works from every document, in every directory.

Target is ``$TEXMFHOME/tex/latex/sysml2tikz/sysml2tikz.sty`` where TEXMFHOME comes
from ``kpsewhich -var-value TEXMFHOME`` (usually ``~/texmf``). No sudo anywhere —
a system-wide install belongs to the distribution package manager or CTAN.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

TEX_SUBDIR = os.path.join("tex", "latex", "sysml2tikz")


def texmfhome() -> str:
    try:
        out = subprocess.run(["kpsewhich", "-var-value", "TEXMFHOME"],
                             capture_output=True, text=True, timeout=30)
        path = out.stdout.strip()
        if path:
            return os.path.expanduser(path)
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return os.path.expanduser("~/texmf")


def install(argv: list[str]) -> int:
    dest_root = texmfhome()
    force = "--force" in argv
    from . import sty_path

    src = sty_path()
    dest_dir = os.path.join(dest_root, TEX_SUBDIR)
    dest = os.path.join(dest_dir, "sysml2tikz.sty")

    if os.path.exists(dest) and not force:
        same = open(src, "rb").read() == open(dest, "rb").read()
        print("%s %s" % ("already current:" if same else "differs (use --force):", dest))
        return 0 if same else 1

    os.makedirs(dest_dir, exist_ok=True)
    shutil.copyfile(src, dest)
    # a user tree without ls-R is still searched, but refreshing costs nothing
    for cmd in (["texhash", dest_root], ["mktexlsr", dest_root]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if r.returncode == 0:
                break
        except (FileNotFoundError, subprocess.SubprocessError):
            continue

    print("installed", dest)
    try:
        found = subprocess.run(["kpsewhich", "sysml2tikz.sty"],
                               capture_output=True, text=True, timeout=30).stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        found = ""
    if found:
        print("kpsewhich resolves sysml2tikz.sty ->", found)
        return 0
    print("note: kpsewhich does not see it yet. TEXMFHOME is %s — check that your TeX\n"
          "distribution searches the user tree (TeX Live does by default; MiKTeX needs\n"
          "the directory registered in its settings)." % dest_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(install(sys.argv[1:]))
