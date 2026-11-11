# 02 — Diagramming rules

Hard invariants for drawing SysML v2 diagrams. These are the rules a diagram violates or it does not — the equivalent of the textual prompting rules, but for pictures. Each rule states what to draw, why the notation requires it, a correct and a wrong form, and whether a machine can check it (and how). Evidence is a figure from the OMG SysML v2 reference implementation or one of this repo's own renders.

Conventions: ✅ correct · ❌ wrong · ⚠️ gotcha. Rule ids are stable (D1, D2, …) so a checklist can cite them. `checkable` values: `ir` (a machine check exists against the notation IR / emitted .tex), `geometry` (checkable from box and port coordinates), `visual` (needs a human or a vision model).

Rule ids are cited by the checklist in [`04-validation-checklist.md`](04-validation-checklist.md).

---

## Definition vs usage

### Rule D1 — Draw a definition with SQUARE corners and a usage with ROUNDED corners

*Why:* The keyword line is small; the corner is visible at a glance and is the reference implementation's only reliable shape-level tell.

```
✅ «part def» Vehicle — square box
«part» vehicle_b : Vehicle — rounded box

❌ both boxes drawn the same shape, so the reader must zoom to tell a type from a role
```

*Evidence:* fig-57 vs fig-61

### Rule D2 — A definition's header is its name; a usage's header is `name : Type`. Put the type in the header, never in a compartment row

*Why:* Typing a usage is what makes it a usage of something; a row cannot express it and readers will not find it.

```
✅ «part»
vehicle_b : Vehicle

❌ «part»
vehicle_b
  type : Vehicle
```

*Evidence:* fig-61

---

## Boxes

### Rule D3 — Every box carries its keyword line inside it, in guillemets, italic: «part», «attribute def», «requirement». Do not rely on the reader inferring it from context

*Why:* Without the keyword a box is ambiguous: the same rectangle is a part, an item or an occurrence depending on one word.

```
✅ «requirement def»
MassRequirement

❌ MassRequirement
```

*Evidence:* fig-57, fig-70

---

## Compartments

### Rule D4 — Separate compartments with a full-width rule and title each with an italic centred noun. On definitions use the bare noun (`attributes`, `ports`, `parts`); on usages use verb + noun (`perform actions`, `exhibit states`)

*Why:* The compartment title says what kind of membership the rows express; a bare noun on a usage hides that the rows are performed or exhibited.

```
✅ attributes / parts / ports on a definition
perform actions / exhibit states on a usage

❌ one undivided box of rows, or `actions` on a usage
```

*Evidence:* fig-57 vs fig-61

---

## Rows

### Rule D5 — Express relationships in rows with the notation's own operators: `:>` subsetting, `:>>` redefinition, `=` binding, `default` for a default value, `[n]`/`[n..m]` for multiplicity. Never draw an arrow to say what a row says

*Why:* Those operators are the model's semantics; an arrow between two rows cannot carry `:>>` and invents a connection the model does not have.

```
✅ mass :> ISQBase::mass
:>>Vehicle::cargoMass
fuelMassMax :> ISQBase::mass = 60 [kg]

❌ mass —arrow→ ISQBase::mass
```

*Evidence:* fig-61, fig-70

---

## Ports

### Rule D6 — Draw a port as a small square straddling the box border, with the port name outside the box beside it. Show direction with a small chevron inside the square (`in` / `out`), not with an arrowhead on the connector

*Why:* A port is a feature of the boundary, not an icon on the box; and in an interconnection view connectors carry no arrowheads, so the chevron is the only direction signal.

```
✅ □ on the border, `fuelIn` written outside, `←` inside the square

❌ port drawn as a dot inside the box, or direction shown by an arrowhead on the connector
```

*Evidence:* fig-64, fig-66

---

## Composition

### Rule D7 — Put the filled diamond at the WHOLE end. The part end gets no arrowhead and no diamond

*Why:* The diamond marks ownership; putting it on the part end inverts the model, and readers take the diamond end as the owner.

```
✅ Vehicle ◆——— Engine

❌ Vehicle ———◆ Engine   (ownership inverted)
Vehicle ◆———▶ Engine (diamond plus arrowhead)
```

*Evidence:* fig-62, fig-70

### Rule D8 — Place a multiplicity at the end it quantifies: at the part end when the part is the many side, at the whole end when the whole is (as in a usage composed of one definition)

*Why:* A multiplicity floating near the middle reads as belonging to the relationship, not to an end.

```
✅ frontAxleAssembly ◆——— frontWheels   2

❌ frontAxleAssembly ◆—2— frontWheels   (ambiguous end)
```

*Evidence:* fig-62

---

## Specialisation

### Rule D9 — Draw specialisation as a solid line with a HOLLOW triangle at the general type. One triangle may serve several subclasses joined by a bus

*Why:* Filled triangles mean flow; a filled triangle here makes a type hierarchy look like a data flow.

```
✅ FrontAxle △——— Axle   (hollow, pointing at Axle)

❌ FrontAxle ▲——— Axle   (filled triangle)
```

*Evidence:* fig-24, fig-72

---

## Requirements

### Rule D10 — Give a requirement an id in angle brackets in its name line, and use `doc`, `attributes` and `constraints` compartments. Write `assume` and `require` in bold inside `constraints`

*Why:* Requirements are read by reviewers looking for text and thresholds; prose in an untitled compartment is unreadable as a requirement.

```
✅ «requirement»
<1> vehicleMassRequirement : MassRequirement
  doc  …
  attributes  massRequired = 2000 [kg]
  constraints  assume { fuelMassActual == fuelMassMax }

❌ «requirement» VehicleMass  {The vehicle shall weigh less than 2000 kg}
```

*Evidence:* fig-70

---

## Cross cutting edges

### Rule D11 — Draw satisfy / verify / derive / allocate / perform / expose / import as DASHED or DOTTED edges carrying the keyword in guillemets as the label

*Why:* These are not structural connections; drawing them solid makes them indistinguishable from composition and connector edges.

```
✅ massTests - - «verify» - -▶ vehicleMassRequirement

❌ massTests ———▶ vehicleMassRequirement   (solid, unlabelled)
```

*Evidence:* fig-72, fig-73

---

## Frames

### Rule D12 — When a diagram is enclosed in a frame, the header names the view kind (`ibd`, `act`, `stm`) or the owning element (`«part» vehicle_b : Vehicle`). A frame header describes the container, never the boxes inside

*Why:* fig-67 is headed «use case» yet contains actions — the header says what the diagram is a view of. Agents that classify by header alone mislabel the contents.

```
✅ «part» vehicle_b : Vehicle  →  contents are parts and ports
«view» Vehicle States : State Transition View  →  contents are states

❌ «action»  →  contents are states (header contradicts contents)
```

*Evidence:* fig-64, fig-67, fig-68

---

## Marks

### Rule D13 — Use only SysML v2 marks. No crow's feet, no ERD multiplicities, no UML-style `*` for many, no activity pins, no stick figures inside a block

*Why:* Borrowed notation reads as a different language; a crow's foot in a SysML diagram is a defect, not a dialect.

```
✅ 1 / 0..* / [1..4] as text labels at edge ends

❌ —< (crow's foot), * (UML many), ● inside a box for a pin
```

*Evidence:* all corpus figures use text multiplicities

---

## Metamodel

### Rule D14 — Do not present a specification (metamodel) figure as a diagram of a system. If the boxes carry bold class names, hollow triangles and `+/role 0..* {subsets …}` labels, it defines the language

*Why:* Metamodel figures share the visual vocabulary but answer a different question; quoting one as a system design is a category error.

```
✅ (in a design review) a parts tree, interconnection or flow
(in the specification) ControlNode ◁— ForkNode

❌ using fig-33's TransitionUsage ladder to explain how a vehicle changes state
```

*Evidence:* fig-24, fig-33
