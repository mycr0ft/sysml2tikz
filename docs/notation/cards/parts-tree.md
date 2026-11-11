# parts tree

Also called: BOM tree, decomposition tree, part usage tree

SysML v2 view: `GeneralView restricted to composition of usages`

## Purpose

Whole–part decomposition of one part: the root box is the whole, every other box is a part it owns, and nesting shows sub-parts.

## How to recognise it

* every box has the same rounded shape and the same «part» keyword — no definition boxes at all
* every edge is a composition: small filled diamond at the parent, nothing at the child
* no ports, no arrowheads, no guards; very wide and shallow (one band of boxes per ownership level)
* `name : Type` on every box; a box that owns sub-parts may omit the `: Type`

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded rectangle, «part» italic above, `name : Type` below, thin rule and empty strip | a part usage | «part» / `engine : Engine`; «part» / `vehicle_b: Vehicle` at the root |
| same, containing other boxes | a part that itself has parts | `rearAxleAssembly` containing `differential`, `rearAxle`, `rearWheel1`, `rearWheel2` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid straight, fanned radially from the parent's corners | filled diamond at the parent, plain at the child | ownership; read the diamond to find the parent |

## Keyword lines

`part`

## Do not confuse with

* **definition and usage** — no square-cornered definition boxes here, and no non-composition edges
* **interconnection view** — no port squares and no connectors between siblings
* **variability model** — if boxes carry «variation» or «variant» it is a variability tree

## Notes

Diamonds from adjacent children can overlap into a dark blob at the parent's edge — count them by following each line, not by counting blobs.

## Evidence

* reference figure: `fig-62-Parts-Tree-for-vehicle_b.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
