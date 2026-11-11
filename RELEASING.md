# Releasing

## PyPI — automated (preferred)

Publishing runs in `.github/workflows/release.yml` on GitHub release, through
**OIDC trusted publishing** — no API token is stored anywhere.

One-time setup, in this order:

1. Publish 0.0.1 by hand (already the plan) so the project exists on PyPI and the
   name is yours.
2. pypi.org → your project → *Publishing* → add a trusted publisher:
   owner `mycr0ft`, repository `sysml2tikz`, workflow `release.yml`,
   environment `pypi`.
3. In the GitHub repo, confirm the `pypi` environment exists (Settings →
   Environments); no secrets needed.

Then every release is:

```bash
# bump both version fields, commit, then:
git tag v0.0.2 && git push origin v0.0.2
gh release create v0.0.2 --notes-file CHANGELOG.md     # triggers publish
```

The workflow refuses to publish if the tag disagrees with `__version__` or if
`tools/verify.py` fails, and it attaches the sdist/wheel to the release.

## PyPI — manual fallback

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

## CI

`.github/workflows/ci.yml` runs on every push to `master` and on pull requests:
build, install the wheel and exercise the CLI, then `tools/verify.py` (golden
`.tex` diff, compile of the four documents, geometry sidecars) with a pinned
tectonic 0.17.0. A tag push additionally runs `version-check`, which fails if the
tag and the package version disagree.

## GitHub releases

`gh release create v<ver> --notes-file CHANGELOG.md` — and that is also the
trigger for the PyPI publish.
