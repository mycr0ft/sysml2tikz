# view and viewpoint

Also called: v, vp, view definition, viewpoint, rendering

SysML v2 view: `ViewView / ViewpointView / RenderingView`

## Purpose

Declares concerns, viewpoints and view definitions, and shows which view exposes or imports what; a rendering is the picture a view produces.

## How to recognise it

* An enclosing frame whose header reads several floating tabbed frames with BOLD roman headers (`ViewpointDefinitions`, `VehicleSafetyView`, `ViewDefinitions`, `PartsTree`) — no guillemets.
* `«concern def»`, `«viewpoint def»`, `«view def»`, `«view»` keywords
* dashed edges labelled «import»*, «satisfy», «expose»* — the asterisk is superscript and easy to miss
* solid edges ending in hollow triangles between view definitions (specialisation)
* a rendering figure that is JUST the tagged boxes the view selected — no frame, no arrows, `«#Safety»`-style tags over part names

## Nodes

| shape | what it means | text inside |
|---|---|---|
| box «concern def» with italic `doc` and `stakeholders` | a concern and who cares about it | «concern def» / `VehicleSafety` / doc 'identify system safety features' / stakeholders `se: SafetyEngineer` |
| box «viewpoint def» with italic `concerns` holding bold `require` | a viewpoint | «viewpoint def» / `SafetyViewpoint` / require `vs: VehicleSafety` |
| rounded box «view» with `name : SomeView` | a view instance | «view» / `vehiclePartsTree_Safety: PartsTreeView` |
| square-cornered box «view def» | a view definition; may hold a `renderings` compartment | «view def» / `TreeView` / `asTreeDiagram:> Views::asTreeDiagram` |
| rounded box «#Safety» over a bare name, empty lower compartment | a rendering: the elements the view selected | «#Safety» / `bumper` |

## Edges

| style | ends | what it means |
|---|---|---|
| dashed | small filled arrowhead | «import»* or «expose»* between view, viewpoint and rendering |
| dashed | small filled arrowhead | «satisfy» from a view to a viewpoint |
| solid | hollow triangle at the general view definition | specialisation of view definitions |

## Keyword lines

`concern def`, `viewpoint def`, `view def`, `view`, `import`, `expose`, `satisfy`, `renderings`

## Do not confuse with

* **definition and usage** — the keywords are about views and concerns, and the edges are dashed with «import»/«expose»
* **parts tree** — a rendering may look like a parts tree with no edges at all; it has tags over names and no diamonds

## Notes

Dashed runs may share one horizontal and read as a T-junction; follow each label to its arrowhead instead of assuming one edge.

## Evidence

* reference figure: `fig-73-Vehicle-Safety-View.svg + fig-74-Rendering-of-view-vehiclePartsTree_Safety.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
