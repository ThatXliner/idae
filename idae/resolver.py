"""Resolve Python versions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import findpython  # type: ignore[import-untyped]
import typer
from packaging.specifiers import InvalidSpecifier, SpecifierSet

if TYPE_CHECKING:  # pragma: no cover
    from rich.console import Console


def get_python_or_exit(version: str, console: Console) -> findpython.PythonVersion:
    """Return a PythonVersion or raise Exit."""
    try:
        output = get_python(version)
    except InvalidSpecifier as err:
        console.print(f"[red]error: Python version {version} could not be parsed[/red]")
        raise typer.Exit(code=1) from err
    if output is None:
        console.print(f"[red]error: Python version {version} not found[/red]")
        raise typer.Exit(code=1)
    return output


def get_python(version: str) -> findpython.PythonVersion | None:
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
    for python_version, python in pythons.items():
        if python_version in target:
            return python
    return None
