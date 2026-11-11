# constraint and assert

Also called: parametric diagram, constraint view, calc

SysML v2 view: `GeneralView with constraint/calculation elements`

## Purpose

Mathematical or logical constraints on the model, and the assertions that hold at a point in behaviour.

## How to recognise it

* boxes headed «constraint def» / «constraint» / «calc def» / «assert constraint»
* compartments titled `parameters` or `operator expressions` holding expressions
* binding edges labelled `=` between parameters and the values they bind

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rectangle, «constraint def», `parameters` compartment | a constraint definition | «constraint def» / `MassConstraint` / parameters `m: MassValue` |
| rectangle, «assert constraint», expression body | an assertion in force | «assert constraint» / `{ fuelMassActual == fuelMassMax }` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid | none | binding of a parameter to a value, labelled `=` |

## Keyword lines

`constraint def`, `constraint`, `assert constraint`, `calc`, `parameters`, `operator expressions`

## Do not confuse with

* **requirement** — requirements carry `id`/`doc`/`text`; constraints carry expressions and parameters

## Notes

Described from the view taxonomy; not yet checked against a rendered figure. Assertions also appear as a compartment inside state and case boxes (fig-68, fig-75), so their presence alone does not make a figure a constraint view.

## Evidence

* reference figure: `fig-35-Constraint-Definition-and-Usage.svg` (NOT yet verified against a figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
