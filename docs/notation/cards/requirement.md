# requirement

Also called: req, requirement diagram, requirements tree

SysML v2 view: `RequirementView`

## Purpose

A tree of requirements with their subject, documentation, values and assumptions.

## How to recognise it

* boxes headed «requirement» with a number in angle brackets: `<1> vehicleMassRequirement : MassRequirement`
* italic compartment titles `doc`, `attributes`, `constraints`, `subject`, `references`
* `doc` holds prose; `attributes` mixes `x = 2000 [kg]` with `:>>Type::x` redefinition rows
* bold `assume` inside a `constraints` compartment, holding `{...}`
* composition edges to child requirements carry a small `*` near the child

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded rectangle, «requirement», `<n> name : Type`, ruled compartments | a requirement | «requirement» / `<2_1> cityFuelEconomyRequirement: FuelEconomyRequirement` |
| rounded rectangle headed «subject» | the thing the requirement is about | «subject» / `vehicle` / `dryMass:> ISQBase::mass` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid thin | filled diamond at the parent requirement, plain at the child | requirement ownership / grouping |
| solid thin | hollow diamond at the requirement end | subject membership |
| dotted | open arrow labelled «satisfy»/«verify»/«derive» | cross-cutting relationship between requirements or to a design element |

## Keyword lines

`requirement`, `subject`, `doc`, `assume`, `references`

## Do not confuse with

* **verification case** — verification figures add «verification»/«verification def» boxes and «perform»/«objective»/«require» arrows

## Notes

This figure is the counter-example to 'hollow diamond = subject everywhere': here it does, and hollow-vs-filled is the only visual difference between requirement ownership and subject membership.

## Evidence

* reference figure: `fig-70-Requirements-Group-vehicleSpecification.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
