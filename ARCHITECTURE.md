# Architecture: what belongs where

Three artifacts, each usable without the others. The point of the split is that
a paper author who just wants figures never installs Python, a modeler who has a
model never hand-writes TikZ, and neither test suite needs the other's
dependencies.

```
                 ┌───────────────────────────────┐
                 │ sysml2tikz.sty   (LaTeX only) │   notation vocabulary:
                 │  \sysmldefnode \sysmlusagenode│   def/usage distinction,
                 │  \sysmlport \draw[sysml ...]  │   compartments, ports, 6 edges
                 └───────────────▲───────────────┘
                                 │ used by
        ┌────────────────────────┴─────────────────────────┐
        │                                                  │
┌───────┴────────────────┐                     ┌───────────┴──────────────┐
│ sysmlpy.tikz           │                     │ sysml2tikz (py, optional)│
│  as_tikz_view(model)   │  ── IR (JSON) ──▶   │  layout + emit + build   │
│  TikZGenerator         │                     │  deps: diagramboxes      │
│  deps: none added      │                     │  + tectonic              │
└───────▲────────────────┘                     └──────────────────────────┘
        │ parses
┌───────┴────────────────┐
│ sysmlpy core           │
└────────────────────────┘
```

## 1. `sysml2tikz.sty` — the LaTeX library

Owns: the notation. Keyword forms, square-vs-rounded definition/usage boxes,
compartment labels, row grammar, port glyphs, edge styles.

Who uses it without anything else: someone writing a SysML v2 figure in a paper
by hand. Today that is ~200 lines of `.sty` plus a demo, and it needs no Python,
no model, no layout engine.

Why it is the most durable artifact: TikZ itself is effectively frozen, so a
notation layer written against it still compiles in ten years. This is the piece
worth putting on CTAN, citing in a paper, and versioning on its own cadence
(`sysml2tikz v0.1`, `v0.2`, ...) independent of every Python release.

**Licensing (decided).** CTAN's upload form offers 53 licences: LPPL
1/1.2/1.3/1.3a/b/c, MIT, BSD variants, GPL/LGPL, CC, EUPL, ISC, Knuth — the LaTeX
norm is LPPL-1.3c, and **Mozilla Public License is not on that list**. So the
`.sty` is dual-licensed **MPL-2.0 OR LPPL-1.3c**: CTAN/TeX Live carry it under
LPPL, the share-alike posture survives under MPL, and the Python side stays
MPL-2.0. See `LICENSES/README.md`, including why tikz-uml's licence is not
inherited (it has none — the file grants nothing, and no code was copied).

Distribution, two channels for two audiences:

* CTAN → TeX Live/MiKTeX → `\usepackage{sysml2tikz}` just works for the LaTeX
  crowd, and the package gets a CTAN catalogue entry and a citable version.
* A wheel (`package_data` shipping the `.sty`) for pipeline users, so
  `pip install` puts both the tool and the package on disk; the CLI points
  `TEXINPUTS` at it. Same file, two homes, one source of truth.

## 2. `sysmlpy.tikz` — the view, inside sysmlpy

Owns: model → notation. This is a *view* in the sense sysmlpy already uses —
`as_interconnection_view`, `as_action_flow_view`, `as_browser_view` all take
`(model, focus=None, elements=None, style="bw", direction="TB", ...)` and return
text. `as_tabular_view(..., output_format="markdown")` is the precedent for a
format parameter.

So the idiomatic addition is:

```python
sysmlpy.as_tikz_view(model, focus=None, elements=None, style="bw",
                     direction="TB", layout="auto", include_legend=False)
# -> str:  a complete .tex fragment (\begin{tikzpicture} ... \end{tikzpicture})
sysmlpy.TikZGenerator(model).generate()
```

Why here rather than a separate package: the model objects are already in hand,
the kind table is a property of SysML (not of TikZ), and it keeps the projection
testable the way `plantuml_test.py` tests its 151 view cases — string assertions
against the emitted text, no TeX, no layout engine.

**Dependency discipline:** `layout="auto"` emits only `positioning`-based
placement (chains of `below=of`, which handles small views and book fragments).
Anything that needs real routing asks for `layout="elk"` and that is an optional
extra, or hands the IR to artifact 3. sysmlpy must not grow a mandatory
diagramboxes dependency for a rendering feature.

## 3. `sysml2tikz` (Python tool) — optional, and useful on its own

Owns: IR in, finished PDF out. Three stages that sysmlpy does not want:
measure-in-TeX, route with diagramboxes/ELK, emit absolute coordinates and
polyline edges.

Two ways it is used, both legitimate:

* **downstream of sysmlpy** — `as_tikz_view(...)` (or the IR JSON) → routed
  figure. This is what the repo does today end to end.
* **standalone** — a hand-written IR (or a fixture from a book figure) → `.tex`.
  Someone with a figure and no model still gets the generator, the golden-file
  tests and the compile gate.

So: yes, the Python side is useful on its own exactly as far as the `.sty` is —
which is the test for whether it deserves its own name.

## Versioning and test ownership

| artifact | version signal | its own gates |
|---|---|---|
| `.sty` | notation changes (new kind pair, new edge) | golden `.tex` + compile; corpus vision score |
| `sysmlpy.tikz` | view content changes | string assertions, no TeX |
| tool | IR schema + layout strategy | golden IR→`.tex`, compile, geometry, corpus score |

The `.sty` version is what a paper cites. The tool version means nothing to a
reader. sysmlpy's version means nothing to a LaTeX user. That independence is
the whole argument for the split.

## Sequencing

1. Freeze the `.sty` API here, dual-license, add `\ProvidesPackage` docs and a
   one-page manual, ship as its own repo (CTAN-shaped tree: `sysml2tikz.sty`,
   `sysml2tikz.pdf`, `README`, `examples/`).
2. Add `sysmlpy.tikz` with `as_tikz_view`/`TikZGenerator` emitting the same
   notation, tested by string assertions — no dependency on this repo.
3. Keep the router/measure adapter here; it becomes the optional tool that
   consumes IR. CI runs the gates already in `tools/verify.py`.
