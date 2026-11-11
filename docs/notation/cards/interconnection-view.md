# interconnection view

Also called: IBD, internal block diagram, parts interconnection, structure

SysML v2 view: `InterconnectionView`

## Purpose

The internal structure of one part: its parts shown inside the owner's frame, wired port to port.

## How to recognise it

* An enclosing frame whose header reads rounded frame, header band with «part» over `name : Vehicle` (bold, spaces around the colon).
* one frame around everything, headed by the owner part
* boxes nested inside boxes to show ownership
* small hollow squares straddling box borders with the port name printed OUTSIDE the box
* connectors run port-to-port and have NO arrowheads; direction, where shown, is a tiny chevron inside the port square

## Nodes

| shape | what it means | text inside |
|---|---|---|
| rounded rectangle inside the frame, «part» over bold name, optional italic `attributes` compartment | a part of the owner | «part» / **engine**; «part» / `frontAxle : FrontAxle` |
| hollow small square straddling a border, name outside | port | `wheelToAxlePort`, `ignitionCmdPort`, `fuelInPort` |
| port square on the frame border itself | a port of the owner, exposed at its boundary | `vehicleToRoadPort`, `wheelToRoadPort1`, `wheelToRoadPort2` |

## Edges

| style | ends | what it means |
|---|---|---|
| solid thin, orthogonal | none (no arrowheads) | connector between two ports |

## Keyword lines

`part`, `port`

## Do not confuse with

* **parts tree** — ports and port-to-port wiring are present here and absent there; here boxes nest inside a frame
* **action flow** — action flows have arrowheads and often dashed lines; interconnection connectors have none

## Notes

A three-line stack of squares on the frame's left border (two `wheelToRoadPort` squares plus one `vehicleToRoadPort` label) reads as a single label until zoomed.

## Evidence

* reference figure: `fig-64-Parts-Interconnection-for-vehicle_b.svg` (verified against the figure)
* corpus: `sysml/SysML-v2-Release/doc/images/sysml/`
