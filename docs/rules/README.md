# Diagramming rules for agents

The companion to a textual-notation knowledge base, for the other half of the
job: producing a **diagram** instead of a `.sysml` file. Same genre, same
audience — an agent that has to emit a drawing and cannot ask whether it looks
right.

| if you are… | read |
|---|---|
| an agent asked to draw a SysML v2 diagram | [`01-diagram-selection.md`](01-diagram-selection.md) → [`02-drawing-rules.md`](02-drawing-rules.md) |
| about to return a diagram | [`04-validation-checklist.md`](04-validation-checklist.md) |
| looking for a starting shape | [`03-common-patterns.md`](03-common-patterns.md) |
| reading someone else's diagram | [`../notation/`](../notation/index.md) — the descriptive cards |
| wiring the rules into a tool | [`rules.json`](rules.json) — ids, statements, checkability |

## What is here

| file | what it is |
|---|---|
| [01-diagram-selection.md](01-diagram-selection.md) | intent → view kind, and the selection rules S1–S7 |
| [02-drawing-rules.md](02-drawing-rules.md) | the hard invariants D1–D14 (generated from `rules.json`) |
| [03-common-patterns.md](03-common-patterns.md) | eight minimal skeletons P1–P8 |
| [04-validation-checklist.md](04-validation-checklist.md) | yes/no gates before returning a figure (generated) |
| [rules.json](rules.json) | the source of truth: id, statement, why, ✅/❌, checkability, evidence |

`02` and `04` are rendered from `rules.json` by `tools/render_rules.py` and gated
by `--check`, so the checklist cannot drift from the rules it cites.

## What makes these different from a style guide

Three things, each of which a static document usually gets wrong:

**Every rule names its evidence.** Each one points at a figure from the OMG
SysML v2 reference implementation that was inspected at 1200 px with zoomed crops
(fig-57, 61, 62, 64, 66, 67, 68, 70, 72, 73, 24, 33) — not at "common practice".

**Seven rules are machine-checked.** `tools/check_rules.py` evaluates the rule
against the notation IR, the emitted `.tex`, the `.sty` style definitions and the
layout geometry, and fails the build if a generated diagram breaks one. Rules
D1–D4, D6–D11 currently pass on both example IRs. The rules marked `visual` (D5,
D12, D13, D14) need eyes — and the notation cards describe what to look for.

**The rules describe the notation, not this renderer.** D1–D14 hold whether the
figure is drawn with this repo's `.sty`, by hand, or by a different tool. Only
`03-common-patterns.md` shows `.sty` code.

## Conventions

* ✅ correct form · ❌ wrong form · ⚠️ gotcha worth reading twice.
* Rule ids (`D1`…`D14`) and selection rules (`S1`…`S7`) and patterns (`P1`…`P8`)
  are stable; cite them in prompts and reviews.
* `«keyword»` means a SysML keyword rendered in guillemets inside the box.
* Source authority: the OMG SysML v2 specification figures, as rendered in
  `SysML-v2-Release/doc/images/sysml/`. Where a rule and a figure disagree, the
  figure wins and the rule is a bug.
