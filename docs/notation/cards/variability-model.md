# variability model

Also called: feature model, variant model, 150% model

SysML v2 view: `GeneralView with variation/variant membership`

## Purpose

Which parts of a family are variable, which alternatives exist, and what selects among them.

## How to recognise it

* boxes carrying BOTH `«variation»` and `«part»`, and boxes carrying BOTH `«variant»` and `«part»`
* small circles hanging off a variation box's bottom edge: ⊗ (circle with ×) and ⊕ (circle with +) selecting alternatives
* one large `«assert constraint»` box holding an `xor` expression over the alternatives
* the usual composition diamonds from the family box to each part, with italic multiplicity `1`

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded box, two keyword lines «variation» «part», `name : Type` | a variable part | «variation» «part» / `engine: Engine` |
| rounded box, «variant» «part» | one alternative | «variant» «part» / `engine4Cyl: Engine4Cyl` |
| rectangle, «assert constraint», `operator expressions` compartment | a selection constraint | `{ (engine==engine::engine4Cyl and …) xor (engine==engine::engine6Cyl and …) }` |
| small circle with ×, small circle with + | variant selection markers | ⊗ / ⊕ |

## Edges

| style | ends | what it means |
|---|---|---|
| solid, gently curved | filled diamond at the family end, plain at the part | the family owns the part |
| solid short | filled diamond above a large hollow triangle | typing to the part definition |

## Keyword lines

`variation`, `variant`, `assert constraint`, `xor`

## Do not confuse with

* **parts tree** — «variation»/«variant» keywords and the constraint box are present only here

## Notes

The ⊗/⊕ circles are the only 'port-like' marks on these boxes; do not report them as ports.

## Evidence

* reference figure: `fig-75-Variability-Model-for-vehicleFamily.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
