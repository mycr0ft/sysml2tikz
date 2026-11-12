# Notation cards

Descriptive cards for reading SysML v2 diagrams — one per view kind, plus an
index with the identification decision tree and a marks glossary.

| file | what it is |
|---|---|
| [index.md](index.md) | the decision tree, the card table, the marks glossary, coverage |
| [cards/](cards/) | 14 cards; 11 verified against reference figures, 3 flagged unverified |
| [notation.json](notation.json) | the source of truth the cards are rendered from |
| [figures.json](figures.json) | which reference figure has a SysML v2 textual source, and where |

## Figures and their textual sources

`figures.json` answers "is there `.sysml` text behind this figure". Figures 56–76
are renderings of a single model — `sysml/src/examples/Vehicle Example/SysML v2
Spec Annex A SimpleVehicleModel.sysml`, 1,582 lines, in the SysML v2 release repo
— so one file backs all of them; 21 of the 38 catalogued figures have a textual
source and 17 do not (metamodel figures and notation-clause illustrations).
`tools/check_figure_sources.py` proves every claimed anchor exists in the claimed
file rather than trusting the table.

No figure content is stored here: the specification's figures are copyrighted by
the organisations listed in the specification and their licence forbids posting
them on a network computer. Use `tools/compare_corpus.py`, whose output goes to
the gitignored `private/` directory, to compare a reference figure with a render.
