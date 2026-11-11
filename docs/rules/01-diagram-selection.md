# 01 — Choosing the diagram

The first rule of drawing is choosing: nine tenths of wrong diagrams are the right
facts drawn as the wrong view. Pick the view from the question being asked, not
from the shape of the model in your head.

---

## What the user asked for → what to draw

| the intent | draw | frame header | key marks |
|---|---|---|---|
| "what kinds of thing are in this system?" / a type taxonomy | **definition and usage** | none | square `«x def»` boxes, rounded `«x»` usages, composition + hollow triangles |
| "what is this one composed of?" | **parts tree** | none | only rounded `«part»` boxes, only composition diamonds |
| "how do these parts wire together?" | **interconnection** | `«part» owner : Type` | port squares on borders, connectors with no arrowheads |
| "what happens, in what order?" | **action flow** | `«action» name : Type` | action boxes, bars for forks, filled triangles on flows |
| "what states can it be in?" | **state transition** | `«view» Name : State Transition View` | regions, entry/do/exit compartments, open-V arrowheads, `[guard]` labels |
| "what must be true?" | **requirement** | none | `<n> name : Type`, `doc`/`attributes`/`constraints`, bold `assume` |
| "how will we prove it?" | **verification case** | bold plain frames | `«verification»`, `«verification def»`, `«perform»`/`«objective»`/`«require»` |
| "which parts are optional / configurable?" | **variability model** | none | `«variation»`/`«variant»`, ⊗/⊕, one `xor` constraint box |
| "what did it look like at t0, t1?" | **individuals and snapshots** | none | `«individual/timeslice/snapshot occurrence»`, one column per time |
| "what does this view show, and who cares?" | **view and viewpoint** | bold plain frames | `«concern def»`/`«viewpoint def»`/`«view def»`/`«view»`, dashed `«expose»`/«import»/«satisfy» |
| "how is the model organised?" | **package and namespace** | package tab | nested package boxes, dashed `«import»` |
| "what does the language itself say?" | **nothing** — that is a metamodel figure | none | bold class names, `{subsets …}` labels |

---

## Selection rules

**S1 — One view per question.** If the answer needs two questions ("what is it
made of?" and "how does it behave?"), produce two diagrams. A parts tree with
state boxes glued on is neither.

**S2 — Never draw a definition you are not also going to use.** A definition
view with no usage leaves the reader unable to see how the types are applied; add
at least one usage per definition you introduce.

**S3 — Interconnection only when there are ports.** If nothing has a port, the
figure is a parts tree: connectors between boxes without port squares are wrong
(see D6 in [`02-drawing-rules.md`](02-drawing-rules.md)).

**S4 — Behaviour views get a behaviour frame.** Action flows and state machines
are framed by the behaviour they describe (`«action» providePower : ProvidePower`),
not by the part that owns it. Putting an action flow in a `«part»` frame makes it
read as structure.

**S5 — Requirements do not carry design.** A requirement box holds text,
thresholds and assumptions. The design that satisfies it belongs in another
diagram, connected by a dashed `«satisfy»` edge (D11).

**S6 — Renderings are not diagrams you draw.** A rendering (what a view selects)
contains only the selected elements and no relationship edges. If you are asked
for "the safety view", produce the view definitions *and* the rendering, not one
figure mixing both.

**S7 — When in doubt, choose the definition/usage view.** It carries the most
information per box and everything else is a restriction of it.
