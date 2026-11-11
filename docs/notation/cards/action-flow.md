# action flow

Also called: activity diagram, behaviour view, action definition, use case flow

SysML v2 view: `ActionFlowView`

## Purpose

How actions consume and produce items and control: a flow from inputs through actions to outputs, with forks and joins.

## How to recognise it

* An enclosing frame whose header reads rounded frame titled «action» over `name : Type`, or «use case» over the use-case name when the flow belongs to a use case.
* «action» boxes with `name : Type` and no pins inside
* ports as squares with a small chevron for direction; labels sit outside the box, split over two lines (`engineTorque :` / `Torque`)
* thick dark horizontal bars where one flow becomes several, or several become one
* `start` and `^done` as rounded «use case» boxes (not the UML filled circle / bullseye)
* one swallowtail (right edge pulled inward to a point) box for `«accept action»`

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded rectangle, «action», stacked name and bold type | an action | «action» / `generateTorque :` / `GenerateTorque` |
| rectangle with a concave right edge (swallowtail) | accept action — waits for a signal | «accept action» / `ignitionCmd:IgnitionCmd` |
| thick dark grey horizontal bar | fork (one in, many out) or join (many in, one out) | none |
| rounded «use case» box | flow start / done marker | `start`, `^done` |

## Edges

| style | ends | what it means |
|---|---|---|
| dashed in fig-67, solid in fig-66 | small filled triangle at the target | control flow |
| solid, straddling a port label | no arrowhead; direction from the port chevron | item flow between ports |

## Keyword lines

`action`, `accept action`, `use case`

## Do not confuse with

* **state transition** — states are boxes with entry/do/exit compartments and edges carrying `[guard]`/`when`; actions here have no such compartments
* **interconnection view** — arrowheads and bars here; connectors without arrowheads there

## Notes

In fig-67 every box says `«use case»` or `«action»` while the frame says `«use case»` — the frame keyword describes the owning behaviour, not the boxes.

## Evidence

* reference figure: `fig-66-Action-flow-for-providePower.svg + fig-67-Action-flow-for-transportPassenger.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
