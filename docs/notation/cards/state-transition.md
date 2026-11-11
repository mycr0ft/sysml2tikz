# state transition

Also called: state machine, stm, statechart

SysML v2 view: `StateTransitionView`

## Purpose

The lifecycle of one exhibited state: its regions, states, entry/do/exit behaviour, guards and transitions.

## How to recognise it

* An enclosing frame whose header reads tab with clipped corner: «view» `Name : State Transition View`.
* one big rounded region per concurrent sub-machine, each with its own small filled initial dot
* state boxes with italic `actions` compartment holding bold `entry` / `do` / `exit` lines
* edges labelled with `trigger [guard] / effect`, where `send` and `when` appear in bold
* `«exhibit state»` above the region name, with bold `parallel` when regions run concurrently

## Nodes

| shape | what it means | text inside |
|---|---|---|
| large rounded region labelled with the substate name | a composite state / concurrent region | `operatingStates`, `healthStates`; outer region «exhibit state» / `vehicleStates` / **parallel** |
| rounded state box with `actions` compartment | a state with behaviour | `on` with entry `performSelfTest`, do `providePower`, exit `applyParkingBrake` |
| state box carrying `assert constraints` | a state with a constraint | `on` / `{electricalPower <= 500 [W]}` |
| small filled black circle | initial pseudostate | none |
| rounded box with a `ref parts` compartment | the state's referenced part | `controller:VehicleController` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid thin | small OPEN V arrowhead | transition |

## Keyword lines

`exhibit state`, `entry`, `do`, `exit`, `when`, `send`, `parallel`

## Do not confuse with

* **action flow** — state boxes carry entry/do/exit; action boxes carry ports and item labels instead
* **definition and usage** — states are rounded and grouped in regions; definitions are not

## Notes

Guard text can be truncated at the figure edge; quote what is legible and flag the missing `]` rather than inventing it.

## Evidence

* reference figure: `fig-68-Vehicle-States.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
