# use case

Also called: uc, use case diagram

SysML v2 view: `UseCaseView`

## Purpose

What actors get from the system: use cases, actors and their include/extends relationships.

## How to recognise it

* An enclosing frame whose header reads «use case» frame named after the use case under study.
* «use case» boxes, typically rounded
* actor boxes or stick figures at the boundary
* dashed arrows labelled «include» / «extends» between use cases

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded box «use case» | a use case | `transportPassenger_1` |
| stick figure or box marked as actor | an actor | `driver`, `passenger` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid | open arrow | association between actor and use case |
| dashed | open arrow labelled «include»/«extends» | use-case relationship |

## Keyword lines

`use case`, `actor`, `include`, `extends`

## Do not confuse with

* **action flow** — an action flow can carry a `«use case»` frame header yet contain «action» boxes with ports and bars — that is a flow, not a use-case diagram

## Notes

Described from the view taxonomy; not yet checked against a rendered figure. fig-67 is a trap: it is headed «use case» but is an action flow.

## Evidence

* reference figure: `fig-47-Use-Case-Definition-and-Usage.svg` (NOT yet verified against a figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
