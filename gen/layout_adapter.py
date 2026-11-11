#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Compatibility shim: the code lives in src/sysml2tikz/layout.py.

Kept so the documented commands (`python3 gen/layout_adapter.py in out`) and
tools/verify.py keep working from a checkout with no install.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sysml2tikz.layout import main  # noqa: E402

raise SystemExit(main(sys.argv))
