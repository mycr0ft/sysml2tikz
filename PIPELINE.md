# sysml2tikz — TeX generation pipeline

Goal: take a SysML v2 model (or a pinned figure spec) and emit a TikZ `.tex`
whose PDF matches the notation of the reference-implementation figures, with
reviewable diffs and no runtime beyond a TeX engine.

Status: stages 1, 2, 3, 4 and 6 exist and are proven end to end —
`examples/vehicle.sysml` goes through parse → IR → measured layout → TikZ → PDF
with `tools/verify.py` green. Stage 5 (CI wiring of those gates) is a script,
not yet a pipeline job.

```
 .sysml ──①parse──> model IR ──②project──> notation IR ──③layout──> placed IR
                                                                     │
                                                            ④emit    ▼
                                                     out.tex ──⑤build──> out.pdf / out.png
                                                                     │
                                                            ⑥verify  ▼
                                                     golden .tex diff · compile · vision score
```

## ① Parse (not built here)

`sysmlpy` already parses SysML v2 into an element tree — that is stage 1 and it
lives in that repo. This pipeline consumes its output; it does not re-parse
text. Contract: every element carries `id`, `kind` (PartDefinition,
PartUsage, RequirementDefinition, …), `name`, `type` (for usages), owner,
members, and its relationships (`:>>` redefinitions, `subsets`, `satisfies`,
`composed of`).

## ② Notation projection — where the def/usage distinction is decided

This stage turns metamodel kinds into printed notation. It is a table, not
cleverness, and the table is grounded in the reference figures
(`SysML-v2-Release/doc/images/sysml/`, rendered here from
`fig-57-Part-Definition-for-Vehicle.svg` and
`fig-61-Part-Usage-for-vehicle_b.svg`):

| element | keyword | box | header | compartment labels | rows |
|---|---|---|---|---|---|
| definition | `«part def»` | square corners | name only | bare noun: `attributes`, `ports`, `actions`, `states` | `max :> temperature`, `brakePedalDepressed: Boolean` |
| usage | `«part»` | rounded corners | `name : Type` | verb + noun: `perform actions`, `exhibit states` | `cargoMass default 0 [kg]`, `:>>Vehicle::cargoMass`, `dryMass=sum(partMasses)` |

Every kind pair follows the same shape (`attribute def`/`attribute`, `port
def`/`port`, `item def`/`item`, `requirement def`/`requirement`, `action
def`/`perform`, `state def`/`exhibit`, `calc def`/`calc`, `constraint
def`/`assert`, `allocation def`/`allocate`, `interface def`/`connect`,
`view def`/`view`, `viewpoint def`/`viewpoint`). The corpus has a
`fig-NN-<Kind>-Definition-and-Usage.svg` for each — those files are the
acceptance criteria for the table, not general knowledge.

Projection output is the JSON IR documented below. Two modes:

* **model mode** — walk the model, emit every definition and usage in scope,
  plus relationships the view spec asks for.
* **figure mode** — a checked-in JSON file pins exactly what a book figure
  shows, with coordinates. This is how the existing corpus reproductions work
  in diagramboxes (`at=` pins); same idea, different renderer.

## ③ Layout (the seam TikZ does not have)

TikZ draws what you tell it to; it does not lay out a graph. Boxes size
themselves from their tabular content, so the layout stage only has to supply:

* a box origin per node (x, y in cm),
* a port side/offset per port,
* an edge router decision per edge (straight, arc, ortho waypoints).

Two implementations, in order of payoff:

1. **Reuse diagramboxes' layout.** `diagramboxes` already runs ELK/pyelk over
   a content model with ports and returns node rects and orthogonal routes —
   `render_svg(routing='elk', elk_options=...)` is the existing path. Feed it
   the notation IR as nodes/ports/edges and read back coordinates; it is
   battle-tested on exactly these figures and gives the Manhattan routing the
   corpus uses.
2. **Pinned coordinates.** For book figures, a `"place": "at={(3.2,-1.4)}"`
   per node, authored from the source page (the diagramboxes repro scripts
   already carry these numbers). No engine, byte-stable output.

Do not attempt layout in TikZ: `positioning` chains are fine for three boxes
and hopeless for a 30-node ladder.

## ④ Emit (.tex)

`gen/emit_tex.py` is the reference emitter (stdlib only, ~150 lines):

```
python3 gen/emit_tex.py gen/model.json gen/out.tex
```

Rules it enforces, which any future emitter must keep:

* **One macro call per element.** `\sysmldefnode`, `\sysmlusagenode`,
  `\sysmlport`, `\draw[sysml composition]`. The `.tex` stays readable and
  reviewable; nobody debugs raw PGF.
* **Escaping is the emitter's job**, not the author's: `_ & % # $ \ ~ ^` are
  escaped in one place (`esc()`). A name like `vehicle_b` appearing raw is the
  bug class that produced `Missing $ inserted`.
* **Row mini-syntax** is deliberately tiny: leading `:>>` → italic
  redefinition row; `*keyword*` anywhere → `\kw{keyword}` (bold, as printed);
  everything else is escaped text with `:>` `=` `[mult]` left literal.
* **Deterministic output**: sorted ids, fixed float formatting, no timestamps.
  Re-emitting an unchanged model must produce a byte-identical file, so a
  `.tex` diff is a semantic diff.
* **Edges carry their operator.** `(a) -- node{...} (b)`; a missing `--` draws
  nothing while still placing the label — silent and expensive to spot.

## ⑤ Build

* **tectonic** (`~/.local/bin/tectonic`, 0.17.0 here) — hermetic: fetches only
  the packages a document uses into its cache, no system TeX, reproducible on
  a fresh machine, and fast enough for CI. `tectonic out.tex`.
* **latexmk + TeX Live** when the figure is embedded in a paper that already
  builds with pdfLaTeX/luaLaTeX; the `.sty` is engine-agnostic.
* Rasterize for review with `pdftoppm -r 190 -png` (or `dvisvgm` for SVG).
  Keep the PNG step in the build script — a stale PNG behind a fresh PDF
  costs a scoring round (the diagramboxes corpus learned this the hard way).

## ⑥ Verify

Three gates, cheapest first:

1. **Golden .tex**: emitter output committed, `diff` in the test. Catches
   escaping/ordering/operator regressions without a TeX install.
2. **Compile smoke test**: `tectonic -o /tmp` on every golden file; exit code
   plus "no warnings about missing characters" (the `nullfont` class of error).
3. **Vision score against the corpus**: render the corpus SVG
   (`inkscape fig-57-...svg --export-type=png -w 1400`) and the generated PNG,
   score notation fidelity /10 with the standing loop. Numeric pre-checks
   before scoring: port squares on the border, no label inside a box rect,
   diamond at the whole end.

## Repo layout

```
tikz-sysml/
  sysml2tikz.sty        notation macros (def/usage/port/edges/frame)
  demo.tex              hand-authored proof of the macro API
  gen/emit_tex.py       IR -> .tex reference emitter
  gen/model.json        small IR: part def, part usage, requirement def, ports, 3 edges
  gen/out.tex,out.pdf   generated + compiled
  PIPELINE.md           this file
```

## Milestones

| # | step | state |
|---|---|---|
| 1 | `.sty` with def/usage distinction, compartments, ports, 6 edge styles | done, compiled |
| 2 | IR + emitter, escaping + determinism | done, compiled |
| 3 | layout adapter: TeX-measured sizes → diagramboxes router → `at=` coords | done (`gen/layout_adapter.py`) |
| 4 | sysmlpy → notation IR projection with the kind table | done, scoped (`gen/from_sysml.py`) |
| 5 | golden tests + corpus vision gate in CI | gates written (`tools/verify.py`), CI not wired |
| 6 | paper integration (one `\input` per figure, fonts inherited) | trivial once 1-4 land |

## Running it

```bash
# hand-authored IR -> tex -> pdf
python3 gen/emit_tex.py gen/model.json gen/out.tex
tectonic gen/out.tex

# IR -> measured, router-placed tex -> pdf
.venv/bin/python gen/layout_adapter.py gen/model.json gen/laid_out.tex
tectonic gen/laid_out.tex

# SysML v2 text -> IR -> layout -> pdf  (the whole pipeline)
~/proj/sysmlpy/venv/bin/python gen/from_sysml.py examples/vehicle.sysml gen/veh.json
.venv/bin/python gen/layout_adapter.py gen/veh.json gen/veh.tex
tectonic gen/veh.tex

# gates
python3 tools/verify.py            # golden diff + compile + geometry
python3 tools/verify.py --vision   # + corpus-vs-render VLM score
```

Two things the first cut of the projection deliberately does not do, so nobody
mistakes scope: nested part trees stay as compartment rows rather than their own
boxes, and ports are drawn as notation without being taken from the model as
routing anchors. Both are the next increments, and both are IR/schema changes
rather than renderer changes.

One sysmlpy-side gap found while wiring this: `perform providePower;` parses to
an Action whose `dump()` is `"perform action ;"` with no name, so the row cannot
be printed. `from_sysml.py` records such members under `projection_notes` instead
of printing noise — the fix belongs in sysmlpy.
