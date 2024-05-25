"""Resolve Python versions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import findpython  # type: ignore[import-untyped]
import typer
from packaging.specifiers import InvalidSpecifier, SpecifierSet

if TYPE_CHECKING:  # pragma: no cover
    from rich.console import Console
from .venv import is_python_cached


def get_python_or_exit(
    version: str, console: Console, use_latest: bool,
) -> findpython.PythonVersion:
    """Return a PythonVersion or raise Exit."""
    try:
        output = get_python(version, use_latest)
    except InvalidSpecifier as err:
        console.print(f"[red]error: Python version {version} could not be parsed[/red]")
        raise typer.Exit(code=1) from err
    if output is None:
        console.print(f"[red]error: Python version {version} not found[/red]")
        raise typer.Exit(code=1)
    return output


def get_python(version: str, use_latest: bool) -> findpython.PythonVersion | None:
    """Resolve the version string and return a valid Python."""
    # Order from latest version to earliest
    pythons = {python.version: python for python in findpython.find_all()}
    try:
        float(version)
    except ValueError:
        pass
    else:
        version = f"~={float(version)}"
    target = SpecifierSet(version)
    cached_candidates = None
    uncached_candidates = None
    for python_version, python in pythons.items():
        if python_version in target:
            if use_latest:
                return python
            if is_python_cached(python.version) and cached_candidates is None:
                cached_candidates = python
            elif uncached_candidates is None:
                uncached_candidates = python
    return cached_candidates or uncached_candidates
