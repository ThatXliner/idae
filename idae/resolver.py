"""Resolve Python versions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import findpython  # type: ignore[import-untyped]
import typer
from packaging.specifiers import InvalidSpecifier, SpecifierSet

from .venv import CACHE_DIR, Python, cache_key, is_venv_usable

if TYPE_CHECKING:  # pragma: no cover
    from packaging.requirements import Requirement
    from rich.console import Console

logger = logging.getLogger("idae")


def get_python_or_exit(
    version: str,
    console: Console,
    requirements: list[Requirement] | None = None,
) -> findpython.PythonVersion:
    """Return a PythonVersion or raise Exit."""
    try:
        output = get_python(version, requirements)
    except InvalidSpecifier as err:
        console.print(f"[red]error: Python version {version} could not be parsed[/red]")
        raise typer.Exit(code=1) from err
    if output is None:
        console.print(f"[red]error: Python version {version} not found[/red]")
        raise typer.Exit(code=1)
    return output


def get_python(
    version: str,
    requirements: list[Requirement] | None = None,
) -> findpython.PythonVersion | None:
    """Resolve the version string and return a valid Python.

    With ``requirements``, prefer a Python that already has a usable cached venv
    for them over the newest match.
    """
    # Order from latest version to earliest
    pythons = list(findpython.find_all())
    try:
        float(version)
    except ValueError:
        pass
    else:
        version = f"~={float(version)}"
    target = SpecifierSet(version)
    matches = [python for python in pythons if python.version in target]
    if requirements is not None:
        for python in matches:
            key = cache_key(requirements, Python(python.version, python.executable))
            if is_venv_usable(CACHE_DIR / key, key):
                logger.debug("Reusing cached Python %s venv", python.version)
                return python
    return matches[0] if matches else None
