# Name research (2026-11-11)

Question: what do we call the Python side so it doesn't collide with anything?

Checked live, this session, in the three registries that actually matter to this
project — PyPI (the Python side), CTAN (the `.sty`), GitHub (the source and the
`pip install` URL).

| candidate | PyPI | GitHub repos named that | CTAN |
|---|---|---|---|
| **sysml2tikz** | free (404) | 0 | free (404) |
| sysmltikz | free | 0 | free |
| tikzsysml | free | 0 | free |
| sysml-tikz | free | 0 | free |
| tikz-sysml | free | 0 | free |
| sysml2tex | free | 0 | free |
| sysmlfig | free | 0 | free |
| sysmlatex | free | 0 | free |
| tikzfig | free | **9** — taken | free |

Surrounding namespace, for context:

* `sysmlpy` — taken, and by you; that is the parent project.
* `sysml`, `sysmlv2` — taken by others on PyPI; `sysml2` is free.
* **CTAN has no package matching "sysml" at all** (0 hits across the whole
  package index). SysML v2 notation in LaTeX is an empty niche, not a crowded one.
* GitHub org name `sysml2tikz` is unclaimed (404).

## Recommendation: one name, `sysml2tikz`, for all three surfaces

    CTAN package       sysml2tikz        \usepackage{sysml2tikz}
    PyPI distribution  sysml2tikz        pip install sysml2tikz   (ships the .sty)
    GitHub repo        mycr0ft/sysml2tikz
    import             import sysml2tikz

Reasons it's the right one rather than merely available:

* It names both halves of what it does — the model side and the renderer — the
  same way `tikz-uml` and `pgf-umlcd` name their lineage. Searchable by someone
  who has never heard of the project.
* One name means one thing to learn. A user who reads a paper citing
  "sysml2tikz" and types either `\usepackage` or `pip install` lands in the same
  place. Splitting names (`sysml2tikz` on CTAN, `tikzsysml` on PyPI) would tax
  every user to no benefit.
* `pip install` can put the `.sty` on disk too, so the Python user needs no TeX
  distribution and the LaTeX user needs no Python. Same package, two doors.
* The import name is a legal Python identifier; the CTAN name is lowercase with
  no reserved characters.

The one caveat that isn't about the name: **PyPI names are first-come.** A 404
today is availability, not a reservation — the cheap lock is to upload 0.0.1 (or
wire a Trusted Publisher) early. Same for the GitHub org, if you want one.

Trademark note: "SysML" is an OMG mark. Descriptive package names like
`sysmlpy` and `sysml2tikz` are normal in the wild, but the README should say
"renders SysML v2 notation" and not imply OMG endorsement or conformance.

## Repo shape if the name is accepted

One repo, two build roots, because the artifacts ship to different registries
but share a version story:

```
sysml2tikz/
  sysml2tikz.sty            <- CTAN file 1
  sysml2tikz.pdf            <- manual (CTAN file 2)
  examples/                 <- CTAN extras
  LICENSES/                 <- MPL-2.0, LPPL-1.3c, README
  pyproject.toml            <- PyPI distribution; ships the .sty via package_data
  src/sysml2tikz/           <- emit, layout adapter, sysmlpy projection
  tools/verify.py           <- golden/compile/geometry/vision gates
```

A CTAN submission is a directory subset (`.sty`, manual, examples, licences) —
the Python tree simply isn't part of the upload.
