"""Resolve Python versions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import findpython  # type: ignore[import-untyped]
import typer
from packaging.specifiers import InvalidSpecifier, SpecifierSet

from .venv import CACHE_DIR, Python, cache_venv_path, is_venv_usable

if TYPE_CHECKING:  # pragma: no cover
    from rich.console import Console

logger = logging.getLogger("idae")


def get_python_or_exit(
    version: str,
    console: Console,
    dep_hash: str | None = None,
) -> findpython.PythonVersion:
    """Return a PythonVersion or raise Exit.

    When ``dep_hash`` is given, an already-cached venv whose Python satisfies
    ``version`` is preferred over creating a brand new one (issue #14).
    """
    try:
        output = get_python(version, dep_hash)
    except InvalidSpecifier as err:
        console.print(f"[red]error: Python version {version} could not be parsed[/red]")
        raise typer.Exit(code=1) from err
    if output is None:
        console.print(f"[red]error: Python version {version} not found[/red]")
        raise typer.Exit(code=1)
    return output


def _normalize_spec(version: str) -> SpecifierSet:
    try:
        float(version)
    except ValueError:
        pass
    else:
        version = f"~={float(version)}"
    return SpecifierSet(version)


def _cached_python_for(
    target: SpecifierSet,
    dep_hash: str,
    pythons: list[findpython.PythonVersion],
) -> findpython.PythonVersion | None:
    """Find a Python that satisfies ``target`` and already has a cached venv."""
    if not CACHE_DIR.is_dir():
        return None
    for python in pythons:
        if python.version not in target:
            continue
        venv_path = cache_venv_path(
            dep_hash,
            Python(python.version, python.executable),
        )
        if venv_path.is_dir() and is_venv_usable(venv_path):
            logger.debug("Reusing cached %s venv for %s", python.version, target)
            return python
    return None


def get_python(
    version: str,
    dep_hash: str | None = None,
) -> findpython.PythonVersion | None:
    """Resolve the version string and return a valid Python.

    If ``dep_hash`` is provided and an existing cached venv's Python satisfies
    the clause, that Python is reused instead of picking the newest match.
    """
    # Order from latest version to earliest
    pythons = list(findpython.find_all())
    target = _normalize_spec(version)
    if dep_hash is not None:
        cached = _cached_python_for(target, dep_hash, pythons)
        if cached is not None:
            return cached
    for python in pythons:
        if python.version in target:
            return python
    return None
