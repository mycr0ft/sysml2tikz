# Releasing

## PyPI

```bash
uv build                       # -> dist/sysml2tikz-<ver>-py3-none-any.whl + .tar.gz
uv publish --token "$PYPI_API_TOKEN"
# or: uv publish            (reads UV_PUBLISH_TOKEN / keyring)
```

Checks before every upload:

```bash
python3 -c "import zipfile,sys; z=zipfile.ZipFile(sorted(__import__('glob').glob('dist/*.whl'))[-1]); print('\n'.join(z.namelist()))"
# must contain sysml2tikz/sysml2tikz.sty — that file is force-included from the repo root
```

The first upload of a name reserves it; PyPI names are first-come, and a 404 only
means "free today". For repeat releases, wire a Trusted Publisher
(pypi.org → project → Publishing) rather than keeping a token on disk.

Version lives in two places and both must move together: `pyproject.toml`
(`version`) and `src/sysml2tikz/__init__.py` (`__version__`).

## CTAN

The LaTeX subset only — no Python. Upload a flat directory containing:

```
sysml2tikz.sty
sysml2tikz.pdf        (manual)
README.md
LICENSES/             (MPL-2.0.txt, LPPL-1.3c.txt, README.md)
examples/
```

Licence to select in the CTAN form: **LaTeX Project Public License 1.3c** (the
`OR MPL-2.0` branch is ours; CTAN's list has no MPL entry).

## GitHub

`gh release create v<ver> --notes-file CHANGELOG.md` once a changelog exists.
