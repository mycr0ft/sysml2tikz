# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Jon R. Fox and Hermes Agent
"""sysml2tikz — SysML v2 notation for LaTeX/TikZ.

Two halves, usable separately:

* ``sysml2tikz.sty`` (shipped inside this distribution) is the LaTeX notation
  layer, licensed MPL-2.0 OR LPPL-1.3c. Use it directly with
  ``\\usepackage{sysml2tikz}`` if you only want figures in a paper.
* this Python package turns a SysML v2 model (or a notation IR) into a ``.tex``
  file: ``project`` (sysmlpy -> IR), ``emit`` (IR -> .tex), ``layout``
  (TeX-measured sizes -> routed coordinates).

Nothing here is required to use the ``.sty``, and the ``.sty`` is not required
to emit IR.
"""
from importlib.resources import files

__version__ = "0.0.1"

def sty_path() -> str:
    """Absolute path of the bundled ``sysml2tikz.sty`` (for TEXINPUTS)."""
    return str(files(__name__).joinpath("sysml2tikz.sty"))

__all__ = ["__version__", "sty_path"]
