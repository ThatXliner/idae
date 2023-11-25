"""Resolve Python versions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import findpython  # type: ignore[import-untyped]
import typer
from packaging.specifiers import InvalidSpecifier, SpecifierSet

if TYPE_CHECKING:
    from rich.console import Console


def get_python(version: str, console: Console) -> findpython.PythonVersion:
    """Resolve the version string or raise Exit."""
    # Order from latest version to earliest
    pythons = {python.version: python for python in findpython.find_all()}
    try:
        float(version)
    except ValueError:
        pass
    else:
        version = f"~={float(version)}"
    try:
        target = SpecifierSet(version)
    except InvalidSpecifier as err:
        console.print(f"[red]error: Python version {version} could not be parsed[/red]")
        raise typer.Exit(code=1) from err
    for python_version, python in pythons.items():
        if python_version in target:
            return python
    console.print(f"[red]error: Python version {version} not found[/red]")
    raise typer.Exit(code=1)
