# individuals and snapshots

Also called: object diagram, instance view, occurrence view

SysML v2 view: `GeneralView of occurrence usages`

## Purpose

A concrete instance over time: one individual, its time slice, and per-time snapshots of its parts.

## How to recognise it

* keywords «individual occurrence», «timeslice occurrence», «snapshot occurrence»
* names of the form `t0_a`, `t0_r: Road_1` — instance names with types
* strict column repeat, one column per snapshot time, each column the same shape
* small filled diamond at the container end of every line, rotated to lie along diagonal lines

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded box, «individual occurrence», `a: VehicleRoadContext_1` | the object | «individual occurrence» / `a: VehicleRoadContext_1` |
| rounded box, «timeslice occurrence» | the object's lifetime | `t0_t2_a` |
| rounded box, «snapshot occurrence», with `attributes` holding `tN =N [s]` and `:>>Context::time` | one instant of the object | `t0_a` |
| rounded box, «snapshot occurrence», `tN_part: Type_N` | a part at that instant | `t0_leftFront: Wheel_1`, `t0_rightFront: Wheel_2` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid straight, sometimes 45° | filled diamond at the container end, none at the child | composition between instances |

## Keyword lines

`individual occurrence`, `timeslice occurrence`, `snapshot occurrence`

## Do not confuse with

* **parts tree** — instance names with `_1`/`_2` suffixes and snapshot keywords; parts trees use definition types
* **definition and usage** — no definitions here at all

## Notes

Diamonds on 45° lines read as black squares; that is one marker rotated, not two different markers.

## Evidence

* reference figure: `fig-76-Vehicle-Individuals-and-Snapshots.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
