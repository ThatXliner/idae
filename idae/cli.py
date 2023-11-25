"""CLI interface."""
from __future__ import annotations

import itertools
import shlex
import subprocess
import sys
from pathlib import Path  # noqa: TCH003  # Likely required for Typer
from typing import List, Optional

import typer
from packaging.requirements import Requirement
from packaging.version import Version
from rich.console import Console

from idae.pep723 import read
from idae.resolver import get_python
from idae.venv import Python, clean_venvs, get_venv

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated
cli = typer.Typer()

console = Console(stderr=True)


@cli.command()
def clean() -> None:
    """Clean the virtual environment caches."""
    clean_venvs()


@cli.command()
def run(
    script: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="The path of the script to run (module only)",
        ),
    ],
    python_flags: Annotated[
        Optional[List[str]],  # noqa: UP007,UP006  # Typer is old
        typer.Option(help="Extra flags to pass to Python"),
    ] = None,
    ignore_version: Annotated[
        bool,
        typer.Option(
            "--ignore-version",
            "-i",
            help="Ignore Python version requirements specified in the script",
        ),
    ] = False,
    force_version: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(
            "--force-version",
            "-f",
            help="Force idae to use a specific Python version",
        ),
    ] = None,
) -> None:
    """Automatically install necessary dependencies to run a Python script."""
    # Get script dependencies
    pyproject = read(str(script.read_text()))
    script_deps = []
    python = Python(
        version=Version(
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        ),
        executable=sys.executable,
    )
    if force_version is not None:
        python = get_python(force_version)
        # I should probably shove this into the `get_python`
        # function to avoid code duplication
        if not python:
            console.print(f"[red]error: Python version {force_version} not found[/red]")
            raise typer.Exit(code=1)
    if pyproject is not None and "run" in pyproject:
        script_deps = (
            []
            if "dependencies" not in pyproject["run"]
            else list(map(Requirement, pyproject["run"]["dependencies"]))
        )

        if (
            not ignore_version
            and force_version is None
            and "requires-python" in pyproject["run"]
        ):
            python = get_python(pyproject["run"]["requires-python"])
            if not python:
                console.print(
                    "[red]error: Python version "
                    + pyproject["run"]["requires-python"]
                    + " not found[/red]",
                )
                raise typer.Exit(code=1)

    venv_path = get_venv(script_deps, python)

    extra_flags = list(
        itertools.chain.from_iterable(
            map(shlex.split, python_flags or []),
        ),
    )
    # Run the script inside the venv
    raise typer.Exit(
        code=subprocess.run(
            [  # noqa: S603  # idae is inherently "insecure"
                str(venv_path / "bin/python"),
                *extra_flags,
                str(script),
            ],
            check=False,
        ).returncode,
    )
