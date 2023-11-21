"""Resolve Python versions."""

from __future__ import annotations

import findpython  # type: ignore[import]
from packaging.specifiers import SpecifierSet


def get_python(version: str) -> findpython.PythonVersion | None:
    """Resolve the version string."""
    # Order from latest version to earliest
    pythons = {python.version: python for python in findpython.find_all()}
    print(pythons)
    target = SpecifierSet(version)
    for python_version, python in pythons.items():
        if python_version in target:
            return python
    return None
