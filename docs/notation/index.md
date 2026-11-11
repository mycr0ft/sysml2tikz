# SysML v2 notation cards — for vision models

SysML v2 draws about a dozen kinds of diagram from one notation vocabulary. Several look alike at a glance: a parts tree and an interconnection view differ only by port squares and connectors; a definition view and a parts tree share the same rectangles but not the same corners. These cards describe what each kind looks like well enough for a vision model to classify it and read it, without the model text. Every card names a figure from the OMG SysML v2 reference implementation and states whether it was checked against that figure at 1200 px with zoomed crops, or written from the view taxonomy and not yet verified.

Machine-readable twin: [`notation.json`](notation.json). These cards are generated
from it by `tools/render_notation.py`; edit the JSON, not the markdown.

## Identifying a diagram type

1. Is there an enclosing frame? Read the frame's header. A tab with a clipped corner carrying `«view» Name : Some View` is a rendered view whose *contents* are whatever the view renders (fig-68 is a state machine inside a «view» tab; fig-72's frames are plain bold names). A frame whose header is just `«part» name : Type` or `«action» name : Type` is an interconnection or action flow of that element.
2. No frame? Then classify by marks, in this order:
   - small hollow squares straddling box borders, with names written outside the box → interconnection view (ports).
   - no squares, and every line has a small filled diamond at one box and nothing at the other → parts tree (or a variability tree if `«variation»`/`«variant»` appear).
   - boxes with `«part def»`/`«attribute def»` keyword lines, square corners → definition view.
   - thick dark bars splitting one flow, plus a `start`/`^done` pair → action flow.
   - a `«requirement»` tree with `<1>`, `<2>` ids and italic `doc`/`attributes`/`constraints` compartments → requirement view.
   - `«individual occurrence»`, `«snapshot occurrence»`, `«timeslice occurrence»` → object/instance view.
   - bold single-line names in plain boxes with hollow triangles up the page and dense `+/role  0..*  {subsets ...}` labels → abstract-syntax (metamodel) diagram, not a user diagram.
3. Text settles the rest: `part def` vs `part`, `:>` subset vs `:>>` redefine vs `=` bind, `[1..4]` multiplicity, `«satisfy»`/`«verify»`/`«require»`/`«perform»`/`«expose»`/`«import»` on dashed arrows.

## The cards

| view | also called | recognise by | figure | verified |
|---|---|---|---|---|
| [definition and usage](cards/definition-and-usage.md) | BDD, block definition diagram, definition view, structure | keyword line inside each box: «part def», «attribute def», «item def», … for definitions;  | `fig-57-Part-Definition-for-Vehicle.svg + fig-61-Part-Usage-for-vehicle_b.svg` | yes |
| [parts tree](cards/parts-tree.md) | BOM tree, decomposition tree, part usage tree | every box has the same rounded shape and the same «part» keyword — no definition boxes at  | `fig-62-Parts-Tree-for-vehicle_b.svg` | yes |
| [interconnection view](cards/interconnection-view.md) | IBD, internal block diagram, parts interconnection, structure | one frame around everything, headed by the owner part | `fig-64-Parts-Interconnection-for-vehicle_b.svg` | yes |
| [action flow](cards/action-flow.md) | activity diagram, behaviour view, action definition, use case flow | «action» boxes with `name : Type` and no pins inside | `fig-66-Action-flow-for-providePower.svg + fig-67-Action-flow-for-transportPassenger.svg` | yes |
| [state transition](cards/state-transition.md) | state machine, stm, statechart | one big rounded region per concurrent sub-machine, each with its own small filled initial  | `fig-68-Vehicle-States.svg` | yes |
| [requirement](cards/requirement.md) | req, requirement diagram, requirements tree | boxes headed «requirement» with a number in angle brackets: `<1> vehicleMassRequirement :  | `fig-70-Requirements-Group-vehicleSpecification.svg` | yes |
| [verification case](cards/verification-case.md) | case view, verification, analysis case | multiple tabbed frames arranged side by side, headers bold with no «» | `fig-72-Vehicle-Mass-Verification-Test.svg` | yes |
| [view and viewpoint](cards/view-and-viewpoint.md) | v, vp, view definition, viewpoint, rendering | `«concern def»`, `«viewpoint def»`, `«view def»`, `«view»` keywords | `fig-73-Vehicle-Safety-View.svg + fig-74-Rendering-of-view-vehiclePartsTree_Safety.svg` | yes |
| [variability model](cards/variability-model.md) | feature model, variant model, 150% model | boxes carrying BOTH `«variation»` and `«part»`, and boxes carrying BOTH `«variant»` and `« | `fig-75-Variability-Model-for-vehicleFamily.svg` | yes |
| [individuals and snapshots](cards/individuals-and-snapshots.md) | object diagram, instance view, occurrence view | keywords «individual occurrence», «timeslice occurrence», «snapshot occurrence» | `fig-76-Vehicle-Individuals-and-Snapshots.svg` | yes |
| [abstract syntax (metamodel)](cards/abstract-syntax-metamodel.md) | metamodel fragment, M1/M2 diagram, specification figure | plain square-cornered boxes with BOLD single-word names and no keyword lines, no compartme | `fig-24-Control-Nodes.svg + fig-33-Transition-Usage.svg` | yes |
| [package and namespace](cards/package-and-namespace.md) | package view, model organisation, pkg | folded-corner or tabbed rectangles holding other boxes | `fig-56-Model-Organization-for-SimpleVehicleModel.svg` | no |
| [use case](cards/use-case.md) | uc, use case diagram | «use case» boxes, typically rounded | `fig-47-Use-Case-Definition-and-Usage.svg` | no |
| [constraint and assert](cards/constraint-and-assert.md) | parametric diagram, constraint view, calc | boxes headed «constraint def» / «constraint» / «calc def» / «assert constraint» | `fig-35-Constraint-Definition-and-Usage.svg` | no |

## Reading order for an agent

Classify first (decision tree). Then: frame header → keyword line inside each box → box title and `: Type` → compartment titles → which end of each edge carries the diamond, triangle or arrow → edge labels and guards → `id =` / `text =` rows. Never infer direction from label placement; read the end marks. When two boxes share a name, the one with `def` in its keyword is the definition.

## Marks glossary

| mark | means | gotcha |
|---|---|---|
| small filled black diamond at one end | composition — that end owns the other. In a parts tree the diamond is at the PARENT. | on diagonal lines the rotated diamond reads as a small black square |
| hollow (white) diamond | in the reference figures this appears on `«subject»` membership (fig-70) and on some part decompositions (fig-72) | the corpus is inconsistent here — do not infer ownership kind from hollow-vs-filled alone; read the keyword lines |
| hollow triangle pointing at a box | specialisation; the pointed-at box is the general type | several subclasses may share ONE triangle on a bus line (fig-24) — do not expect one per edge |
| small open V / open arrowhead | reference, satisfy, require, perform, expose, import — the label says which | plain connectors between ports in an interconnection view have NO arrowheads at all |
| filled triangle arrowhead | directed flow (action flows, item flows) | action flow edges are dashed in fig-67 and solid in fig-66 |
| small chevron `>` or `←` inside a port square | port direction (in / out) | the chevron, not the arrowhead, gives direction when the connector has no arrowhead |
| thick dark bar across a flow | fork or join — several flows split from, or merge into, this point | two bars stacked close together are two separate forks |
| small `*` beside a box or line | membership/ownership marker in requirement and decomposition figures | easy to mistake for a footnote or multiplication sign |
| grey box, grey text, no bold | a class from another package or an abstract class in abstract-syntax figures | in diagrams proper, grey is only used for `«keyword»` lines |

## Coverage

Verified against reference figures: definition/usage, parts tree, interconnection, action flow, state transition, requirement, verification case, view and rendering, variability, individuals/snapshots, abstract syntax. Written from the view taxonomy but NOT yet checked against a figure: package/namespace, use case, constraint/assert. Not covered at all: tabular and relationship-matrix views, sequence views (no reference figure inspected).
