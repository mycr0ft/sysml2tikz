# definition and usage

Also called: BDD, block definition diagram, definition view, structure

SysML v2 view: `GeneralView / PackageView (definitions and usages of structure)`

## Purpose

Declares types (definitions) and the roles that use them (usages). A definition names a kind of thing and its features; a usage says a thing of that kind exists in a particular place, possibly redefining values.

## How to recognise it

* boxes carry a keyword line «part def», «attribute def», «item def», «port def», … for definitions, and «part», «attribute», «item», «port», … for usages
* a definition's box has SQUARE corners; a usage's box has ROUNDED corners (this is the single most reliable visual tell in the reference figures)
* a usage's header reads `name : Type`; a definition's header reads only the name
* compartment titles are bare nouns on definitions (`attributes`, `parts`, `ports`, `actions`, `states`) and verb+noun on usages (`perform actions`, `exhibit states`)

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rectangle, square corners, keyword line + centred name, then rule-separated compartments | definition — a type | «part def» / Vehicle / attributes: `mass :> mass` / ports: `ignitionCmdPort : IgnitionCmdPort` |
| rectangle, ROUNDED corners, keyword line + `name : Type`, then compartments | usage — a role in a context | «part» / `vehicle_b : Vehicle` / attributes: `cargoMass default 0 [kg]`, `:>>Vehicle::cargoMass` |
| small square on a box border, labelled in or out | port | `fuelIn` with an `in` arrow beside it |

## Edges

| style | ends | what it means |
|---|---|---|
| solid | filled diamond at the whole end, plain at the part end | composition — the part end is owned by the whole |
| solid | hollow triangle at the parent end | specialisation (`:>` subtype) |
| solid | open arrow | reference / subsetting between usages |
| dotted | open arrow with «satisfy»/«derive»/«verify» | cross-cutting relationship to a requirement |

## Keyword lines

`part def`, `part`, `attribute def`, `attribute`, `item def`, `item`, `port def`, `port`, `action def`, `state def`, `requirement def`

## Do not confuse with

* **parts tree** — a parts tree shows only usages (all boxes rounded) and every edge is a composition; a definition/usage view mixes square definition boxes with rounded usage boxes
* **interconnection view** — interconnection views add port squares on the borders and connect square-to-square; here edges run box-to-box with no ports

## Notes

Row grammar carries meaning and is worth reading literally: `:>` subsets, `:>>` redefines (italic row), `=` binds, `default` gives a default value, `[n..m]` is multiplicity. `perform` and `exhibit` appear in bold at the start of action/state rows.

## Evidence

* reference figure: `fig-57-Part-Definition-for-Vehicle.svg + fig-61-Part-Usage-for-vehicle_b.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
