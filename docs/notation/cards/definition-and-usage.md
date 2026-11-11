# definition and usage

Also called: BDD, block definition diagram, definition view, structure

SysML v2 view: `GeneralView / PackageView of structure`

## Purpose

Declares types (definitions) and the roles that use them (usages). A definition names a kind of thing and its features; a usage says a thing of that kind exists in a context, possibly redefining values.

## How to recognise it

* keyword line inside each box: «part def», «attribute def», «item def», … for definitions; «part», «attribute», «item», … for usages
* a definition's box has SQUARE corners, a usage's box has ROUNDED corners — the single most reliable visual tell in the reference figures
* a usage's header reads `name : Type`; a definition's header reads only the name
* compartment titles are bare nouns on definitions (`attributes`, `parts`, `ports`, `actions`) and verb+noun on usages (`perform actions`, `exhibit states`)

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rectangle, square corners, keyword + centred name, rule-separated compartments | definition (a type) | «part def» / Vehicle / attributes `mass :> mass` / ports `ignitionCmdPort : IgnitionCmdPort` |
| rectangle, ROUNDED corners, keyword + `name : Type`, then compartments | usage (a role in a context) | «part» / `vehicle_b : Vehicle` / `cargoMass default 0 [kg]` / `:>>Vehicle::cargoMass` |
| small square on a box border | port | `fuelIn` with an in-arrow beside it |

## Edges

| style | ends | what it means |
|---|---|---|
| solid | filled diamond at the whole end | composition |
| solid | hollow triangle at the parent | specialisation (`:>`) |
| solid | open arrow | reference / subsetting |
| dotted | open arrow labelled «satisfy»/«derive»/«verify» | relationship to a requirement |

## Keyword lines

`part def`, `part`, `attribute def`, `attribute`, `item def`, `item`, `port def`, `port`, `action def`, `state def`, `requirement def`

## Do not confuse with

* **parts tree** — a parts tree has only rounded usage boxes and only composition edges; here square definition boxes sit among the rounded ones
* **interconnection view** — interconnection views add port squares on borders and connect square-to-square

## Notes

Row grammar carries meaning: `:>` subsets, `:>>` redefines (italic row), `=` binds, `default` value, `[n..m]` multiplicity; `perform`/`exhibit` are bold at the start of action/state rows.

## Evidence

* reference figure: `fig-57-Part-Definition-for-Vehicle.svg + fig-61-Part-Usage-for-vehicle_b.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
