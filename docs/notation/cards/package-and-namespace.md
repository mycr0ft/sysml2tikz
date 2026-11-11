# package and namespace

Also called: package view, model organisation, pkg

SysML v2 view: `PackageView`

## Purpose

How the model is organised: packages, their members and the imports between them.

## How to recognise it

* An enclosing frame whose header reads package-shaped box (tab at the top left) carrying the package name.
* folded-corner or tabbed rectangles holding other boxes
* dashed arrows labelled «import» between packages
* member boxes inside, often the definitions themselves

## Nodes

| shape | what it means | text inside |
|---|---|---|
| tabbed rectangle | package | `SimpleVehicleModel` |
| small box inside | member element | `«part def» Vehicle` |

## Edges

| style | ends | what it means |
|---|---|---|
| dashed | open arrow | import / membership dependency |

## Keyword lines

`package`, `import`

## Do not confuse with

* **view and viewpoint** — view frames carry «view»/«viewpoint def» keywords and «expose»/«satisfy» labels

## Notes

Described from the view taxonomy; not yet checked against a rendered figure.

## Evidence

* reference figure: `fig-56-Model-Organization-for-SimpleVehicleModel.svg` (NOT yet verified against a figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
