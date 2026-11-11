# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""Command line entry points.

    sysml2tikz emit     model.json out.tex     IR -> .tex
    sysml2tikz layout   model.json out.tex     IR -> measured + routed .tex
    sysml2tikz project  model.sysml out.json   SysML v2 text -> IR
    sysml2tikz sty                             print the bundled .sty path
    sysml2tikz install-sty                     copy it into TEXMFHOME (TeX Live/MiKTeX)
    sysml2tikz version
"""
from __future__ import annotations

import sys

from . import __version__


def _usage() -> int:
    print(__doc__.strip())
    return 2


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        return _usage()
    cmd, rest = argv[0], argv[1:]
    if cmd == "version":
        print(__version__)
        return 0
    if cmd == "sty":
        from . import sty_path
        print(sty_path())
        return 0
    if cmd == "install-sty":
        from .install import install
        return install(rest)
    if cmd == "emit":
        from .emit import main as run
        return run(["emit"] + rest)
    if cmd == "layout":
        from .layout import main as run
        return run(["layout"] + rest)
    if cmd == "project":
        from .project import main as run
        return run(["project"] + rest)
    if cmd in ("-h", "--help", "help"):
        return _usage()
    print("unknown subcommand: %s\n" % cmd, file=sys.stderr)
    return _usage()


if __name__ == "__main__":
    raise SystemExit(main())
