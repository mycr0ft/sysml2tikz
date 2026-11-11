# Changelog

## 0.0.2

* `sysml2tikz install-sty` — copies the bundled `sysml2tikz.sty` into
  `$TEXMFHOME/tex/latex/sysml2tikz/` (resolved with `kpsewhich -var-value
  TEXMFHOME`), so `\usepackage{sysml2tikz}` works from any directory with a
  normal TeX Live install. No sudo; a system-wide install belongs to the
  distribution or CTAN. Idempotent: reports "already current" instead of
  rewriting, `--force` to overwrite.
* `sysml2tikz.sty` is located in a source checkout too (repo root fallback), so
  `sty`/`install-sty` work without installing the wheel.

## 0.0.1

First public release: the `.sty` notation layer (definition/usage distinction,
compartments, ports, composition/reference/item-flow/satisfy/generalization
edges) plus the pipeline — `project` (SysML v2 → IR), `emit` (IR → `.tex`),
`layout` (TeX-measured sizes → routed coordinates) — with the `.sty` bundled in
the wheel.
