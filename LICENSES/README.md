# Licences

Two licences apply to this project, split by artifact rather than by file type.

| artifact | licence | why |
|---|---|---|
| `sysml2tikz.sty` and the examples that use it | **MPL-2.0 OR LPPL-1.3c** | dual: LPPL is the branch CTAN and TeX Live accept and the one LaTeX users expect; MPL keeps the project's share-alike posture and its explicit patent grant |
| `gen/*.py`, `tools/*.py` | **MPL-2.0** | no LaTeX distribution constraint applies to the Python side |

`SPDX-License-Identifier` appears in every source file, so a file always states
its own terms.

## Why not tikz-uml's licence

`tikz-uml.sty` — the package whose *notation* prompted this work — carries no
licence statement at all (5,375 lines, no "licence", "copyright", "LPPL" or
"GPL" anywhere), and its documentation site states none either. Under default
copyright that is all rights reserved, so there is nothing to adopt and nothing
was copied: `sysml2tikz.sty` is written from scratch on plain TikZ and shares no
macro names or implementation with it. The notation it reproduces is SysML v2's,
taken from the OMG reference figures, and notation is not a licensable work.

The dual-licence pattern is the one the neighbouring package uses —
`pgf-umlcd.sty` line 1 is `SPDX-License-Identifier: GPL-2.0-only OR LPPL-1.3c` —
and it is the standard way to satisfy both the LaTeX world and a project's own
terms.

## Full texts

* `MPL-2.0.txt` — Mozilla Public License 2.0 (mozilla.org/media/MPL/2.0/index.txt)
* `LPPL-1.3c.txt` — LaTeX Project Public License 1.3c (CTAN `macros/latex/base/lppl.txt`)

LPPL's practical consequence, worth knowing before forking: modified files must
be renamed, so a derivative of the `.sty` cannot keep the `sysml2tikz` name.
That rule is also why writing fresh rather than forking tikz-uml was the right
call.
