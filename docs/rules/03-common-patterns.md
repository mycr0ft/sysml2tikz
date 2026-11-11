# 03 — Common patterns

Each pattern is the smallest diagram that answers its question. Copy the skeleton,
then apply the rules in [`02-drawing-rules.md`](02-drawing-rules.md). The `.sty`
calls are those of this repo's notation layer; the notation itself is
renderer-independent.

---

## P1 — Definition plus one usage (the default structural figure)

*Use when:* introducing vocabulary, or answering "what kinds of thing exist and
how is one of them configured".

```tex
\sysmldefnode{v}{part def}{Vehicle}{%           % D1 square, D3 keyword
  \sysmlcomp{attributes}                         % D4 bare noun on a definition
  mass :> ISQBase::mass\\                        % D5 subsetting in the row
  \sysmlcomp{parts}
  engine : Engine [1]\\
}
\sysmlusagenode[below=of v]{vb}{part}{vehicle_b}{Vehicle}{%   % D1 rounded, D2 header type
  \sysmlcomp{attributes}
  :>>Vehicle::mass\\                             % D5 redefinition stays in a row
}
\draw[sysml composition] (vb) -- node[right, pos=0.15]{1} (v);   % D7 diamond at whole, D8 end label
```

*Do not add:* an arrow from a row to a type (D5), a second diamond at the part end
(D7), a compartment titled `type` (D2).

---

## P2 — Parts tree

*Use when:* the question is "what is this made of". No ports, no behaviours.

```tex
\sysmldefnode... % not used: every box is a usage
\sysmlusagenode{root}{part}{vehicle_b}{Vehicle}{}
\sysmlusagenode[r]{part}{engine}{Engine}{}
\sysmlusagenode[t]{part}{fuelTank}{FuelTank}{}
\draw[sysml composition] (r) -- (root);
\draw[sysml composition] (t) -- (root);
```

*Do not add:* definition boxes, ports, arrowheads (D7), or a legend.

---

## P3 — Interconnection with ports

*Use when:* parts exist **and** what matters is what flows between them.

```tex
\sysmlusagenode{eng}{part}{engine}{Engine}{}
\sysmlport{eng}{east}{fuelIn}{above right}       % D6 square on the wall, name outside
\sysmlport{tank}{east}{fuelOut}{above right}
\draw[sysml itemflow] (tank-p-east) -- (eng-p-east);   % no arrowhead on the connector
```

*Do not add:* arrowheads on connectors (D6), ports as dots inside boxes (D6), a
frame headed by the part when the figure is really about actions (D12).

---

## P4 — Action flow

*Use when:* the question is order, not structure.

Skeleton: frame `«action» name : Type`; action boxes `name : Type`; ports only
where an item crosses the boundary; a bar where one flow becomes several; flows as
filled-triangle edges.

*Do not add:* a start state drawn as a filled circle (SysML v2 uses `start`/`^done`
boxes in the reference figures — see the action-flow card), entry/do/exit
compartments (those are state syntax), guards without brackets.

---

## P5 — State machine

*Use when:* the question is "what states, what wakes it up".

Skeleton: frame tab `«view» Name : State Transition View`; one region per
concurrent submachine, each with its own small filled initial dot; state boxes
with `entry`/`do`/`exit`; transitions labelled
`trigger [guard] / effect`.

*Do not add:* action boxes with ports (P4), a transition without the trigger, or a
guard outside brackets.

---

## P6 — Requirement tree

*Use when:* the question is "what must be true, and why".

Skeleton: `«requirement»` root, children with `<1>`, `<2>`, `<2_1>` ids in the
name line; `doc` prose; `attributes` with `= 2000 [kg]` values; `constraints` with
bold `assume { … }`; composition edges to children carrying `*` (D10).

*Do not add:* the design, the test, or the analysis — connect them with dashed
`«satisfy»`/«verify» edges (D11).

---

## P7 — Verification case

*Use when:* the question is "how do we prove the requirement".

Skeleton: a `«verification»` box with `: TestType` and a `metadata` compartment;
the performing `«part»` system and its `«perform action»` steps; `«requirement»
obj` for the objective; a `«verification def»` for the case type; edges labelled
`«perform»`, `«objective»`, `«require»` in bold guillemets (D11).

*Do not add:* pass/fail results (a run, not a model), or the requirement's text
duplicated inside the case.

---

## P8 — View plus its rendering

*Use when:* the question is "what does this view show and who cares".

Skeleton: `«concern def»` → `«viewpoint def»` (with `concerns` requiring the
concern) → `«view»` (dashed `«satisfy»`) → `«view def»` specialisations
(hollow triangles) → a rendering that contains only the selected boxes, tagged
(`«#Safety»`), with no edges at all.

*Do not add:* relationship edges inside the rendering (S6), guillemets on frame
headers (the reference uses bold roman names for view frames), or the rendering
mixed into the definition figure.
