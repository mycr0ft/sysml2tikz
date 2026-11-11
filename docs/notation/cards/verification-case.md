# verification case

Also called: case view, verification, analysis case

SysML v2 view: `CaseView (verification)`

## Purpose

How a verification case is performed: the system of parts and actions that run the test, the objective, and the requirement it verifies.

## How to recognise it

* An enclosing frame whose header reads several plain tabbed frames with BOLD roman headers and no guillemets, e.g. `VerificationSystem`, `VerificationCases1`, `VerificationCaseDefinitions`.
* multiple tabbed frames arranged side by side, headers bold with no «»
* «verification» box with a `: TestType` and a `metadata` compartment
* «verification def» boxes with square corners and large roman names
* bold guillemet edge labels «perform», «objective», «require»

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded box, «verification», `name : Type`, italic `metadata` compartment | the case | «verification» / `massTests: MassTest` / `kind = VerificationMethodKind::test` |
| square-cornered box, «verification def» over a large name | the case definition | «verification def» / `MassTest` |
| small box «requirement» | objective or verified requirement | `obj`, `vehicleMassRequirement` |
| «part» and «perform action» boxes | the performing system | `massVerificationSystem`, `operator`, `scale`, `evaluatePassFail`, `weighVehicle` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid thin | hollow diamond at the owner end | part decomposition in the performing system |
| solid thin | filled diamond at the case end | the case owns those actions |
| solid thin | open arrow labelled «perform» | which case the system performs |
| solid thin | open arrow labelled «objective» or «require» | objective / verified requirement |
| solid thin | hollow triangle at the general case definition | specialisation |

## Keyword lines

`verification`, `verification def`, `perform action`, `objective`, `require`, `metadata`

## Do not confuse with

* **requirement** — requirement figures show only requirement boxes; this one adds the performing system and actions
* **interconnection view** — case frames have bold plain headers; interconnection frames are headed «part» name : Type

## Notes

Both hollow and filled diamonds appear in this single figure for what look like the same relationship; trust the keyword lines over the diamond style.

## Evidence

* reference figure: `fig-72-Vehicle-Mass-Verification-Test.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
