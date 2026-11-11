# SysML v2 notation cards — for vision models

SysML v2 draws about a dozen kinds of diagram from one notation vocabulary. Two of them look almost identical at a glance (a parts tree and an interconnection view differ only by the connectors between ports), and several share the same rectangles. These cards describe what each kind looks like well enough for a vision model to classify it and read it, without the model text. Each card is grounded in a figure from the OMG SysML v2 reference implementation, and says so — or says it is not yet verified.

Machine-readable twin: [`notation.json`](notation.json). These cards are generated
from it by `tools/render_notation.py`; edit the JSON, not the markdown.

## Identifying a diagram type

1. Is there an enclosing frame with a header? Read the header's first word — it names the view kind: `ibd` (interconnection), `act` (action flow), `stm` (state transition), `uc` (use case), `req` (requirement), `vp` (viewpoint), `v` (view), `assume`/`assert` (constraint), `sd` (sequence). A frame with `«view»` and an `expose` note is a *view* — the diagram inside it is whatever the view renders.
2. No frame, or a frame without a kind word? Then classify by content:
   - small squares straddling box borders with `in`/`out` arrows, and lines joining square to square → interconnection view (ports + connectors).
   - no squares, and each line ends in a filled diamond at one box → parts tree / composition (a BDD restricted to usages).
   - boxes with `«part def»`/`«attribute def»` keyword lines and no connectors between boxes → definition view (a BDD of definitions).
   - thick bars splitting one flow into several, plus a filled circle at the start and a ring-around-dot at the end → action flow.
   - rounded rectangles named `X` with a small label in the corner, and arrows labelled `[guard]`/`event` between them → state transition.
   - vertical dashed lines with boxed names on top and horizontal arrows between lifelines → sequence view.
   - ovals with stick figures → use case view.
   - boxes whose second compartment says `id =` and `text =`, with a dotted arrow labelled «satisfy» into them → requirement view.
3. Text tells you the rest: `part def` vs `part`, `:>` (subset) vs `:>>` (redefine) vs `=` (bind), `[1..4]` multiplicities, `«allocate»`, `«satisfy»`, `«verify»`, `«derive»`.

## The cards

| view | also called | recognise by | figure | verified |
|---|---|---|---|---|
| [definition and usage](cards/definition-and-usage.md) | BDD, block definition diagram, definition view, structure | boxes carry a keyword line «part def», «attribute def», «item def», «port def», … for defi | `fig-57-Part-Definition-for-Vehicle.svg + fig-61-Part-Usage-for-vehicle_b.svg` | yes |

## Reading order for an agent

Classify first (decision tree above), then read in this order: frame header → keyword lines inside boxes → box titles and typing → compartment titles → edge ends (which end has the diamond/triangle/arrow) → edge labels and guards → any `id =`/`text =` rows. Never infer a relationship's direction from label placement; read the arrowhead. When two boxes have the same name, the one with `def` in its keyword is the definition and the other is a usage of it.
