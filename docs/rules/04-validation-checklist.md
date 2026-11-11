# 04 — Validation checklist (diagrams)

Run this **before** returning a diagram, the way the textual checklist is run before
returning `.sysml` text. Each gate cites the rule it enforces. Gates marked
**[auto]** are checked by `tools/check_rules.py` against the notation IR and the
layout geometry; the rest need eyes or a vision model.

---

## A. Definition vs usage

- [ ] **A1.** Draw a definition with SQUARE corners and a usage with ROUNDED corners **[auto]**
- [ ] **A2.** A definition's header is its name; a usage's header is `name : Type`. Put the type in the header, never in a compartment row **[auto]**

---

## B. Boxes

- [ ] **B1.** Every box carries its keyword line inside it, in guillemets, italic: «part», «attribute def», «requirement». Do not rely on the reader inferring it from context **[auto]**

---

## C. Compartments

- [ ] **C1.** Separate compartments with a full-width rule and title each with an italic centred noun. On definitions use the bare noun (`attributes`, `ports`, `parts`); on usages use verb + noun (`perform actions`, `exhibit states`) **[auto]**

---

## D. Rows

- [ ] **D1.** Express relationships in rows with the notation's own operators: `:>` subsetting, `:>>` redefinition, `=` binding, `default` for a default value, `[n]`/`[n..m]` for multiplicity. Never draw an arrow to say what a row says

---

## E. Ports

- [ ] **E1.** Draw a port as a small square straddling the box border, with the port name outside the box beside it. Show direction with a small chevron inside the square (`in` / `out`), not with an arrowhead on the connector **[auto]**

---

## F. Composition

- [ ] **F1.** Put the filled diamond at the WHOLE end. The part end gets no arrowhead and no diamond **[auto]**
- [ ] **F2.** Place a multiplicity at the end it quantifies: at the part end when the part is the many side, at the whole end when the whole is (as in a usage composed of one definition) **[auto]**

---

## G. Specialisation

- [ ] **G1.** Draw specialisation as a solid line with a HOLLOW triangle at the general type. One triangle may serve several subclasses joined by a bus **[auto]**

---

## H. Requirements

- [ ] **H1.** Give a requirement an id in angle brackets in its name line, and use `doc`, `attributes` and `constraints` compartments. Write `assume` and `require` in bold inside `constraints` **[auto]**

---

## I. Cross cutting edges

- [ ] **I1.** Draw satisfy / verify / derive / allocate / perform / expose / import as DASHED or DOTTED edges carrying the keyword in guillemets as the label **[auto]**

---

## J. Frames

- [ ] **J1.** When a diagram is enclosed in a frame, the header names the view kind (`ibd`, `act`, `stm`) or the owning element (`«part» vehicle_b : Vehicle`). A frame header describes the container, never the boxes inside

---

## K. Marks

- [ ] **K1.** Use only SysML v2 marks. No crow's feet, no ERD multiplicities, no UML-style `*` for many, no activity pins, no stick figures inside a block

---

## L. Metamodel

- [ ] **L1.** Do not present a specification (metamodel) figure as a diagram of a system. If the boxes carry bold class names, hollow triangles and `+/role 0..* {subsets …}` labels, it defines the language

---

## Summary of what a machine can enforce

| rule | area | how it is checked |
|---|---|---|
| D1 | definition vs usage | def nodes use the square-corner macro, usage nodes the rounded one |
| D2 | definition vs usage | usage nodes carry a non-empty type |
| D3 | boxes | every node's kind is rendered as a keyword line |
| D4 | compartments | compartment labels follow the definition/usage table |
| D6 | ports | every port glyph centre lies within 2pt of its box wall |
| D7 | composition | composition edges route to the whole node with the diamond style and no extra arrowhead |
| D8 | composition | labels on composition edges are attached as end labels, not mid-edge labels |
| D9 | specialisation | generalisation edges use the hollow-triangle style |
| D10 | requirements | requirement nodes carry an id and a doc/attributes compartment |
| D11 | cross-cutting edges | cross-cutting edges use a dashed style and a keyword label |

Everything else is visual: a vision model or a human must look. The cards in
[`../notation/`](../notation/index.md) describe what to look for.
