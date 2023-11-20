"""Resolve Python versions."""

from __future__ import annotations

import findpython


def get_python(version: str) -> findpython.PythonVersion | None:
    """Resolve the version string"""
    return findpython.find(version)
