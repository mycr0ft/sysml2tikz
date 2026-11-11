# abstract syntax (metamodel)

Also called: metamodel fragment, M1/M2 diagram, specification figure

SysML v2 view: `not a user view — a specification figure`  ·  kind: **metamodel**

## Purpose

Defines the language itself: classes, their specialisations and their associations. Appears in the specification, not in models you are asked to read.

## How to recognise it

* plain square-cornered boxes with BOLD single-word names and no keyword lines, no compartments
* vertical ladders joined by hollow triangles (specialisation)
* association labels of the form `+/role  0..*  {subsets feature}` — role name, multiplicity, constraint
* greyed boxes with grey text among black ones
* one hollow triangle may serve several subclasses on a shared bus line

## Nodes

| shape | what it means | text inside |
|---|---|---|
| plain square box, bold name | a metaclass | `ActionUsage`, `ControlNode`, `TransitionUsage` |
| grey-filled box with grey bold name | class from another package or abstract class | `Expression`, `Succession` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid vertical | large hollow triangle at the general class | specialisation |
| solid orthogonal | small solid dot at the owning class plus a tiny open arrow at the target | association, navigable the other way |

## Keyword lines

`subsets`, `redefines`, `owning`

## Do not confuse with

* **definition and usage** — no «keyword» lines, no compartments, and the role labels use `+/` and `{subsets ...}`

## Notes

If a figure looks like a family tree of types with dense role labels on both sides of every line, it is the specification defining the language, not a model of a system.

## Evidence

* reference figure: `fig-24-Control-Nodes.svg + fig-33-Transition-Usage.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
