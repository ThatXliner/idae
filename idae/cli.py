"""CLI interface."""
import itertools
import platform
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer
from click.exceptions import UsageError
from packaging.requirements import Requirement
from packaging.version import Version
from rich.console import Console

from idae.pep723 import read
from idae.resolver import get_python_or_exit
from idae.venv import Python, clean_venvs, get_venv

if sys.version_info < (3, 9):  # pragma: no cover
    from typing_extensions import Annotated
else:
    from typing import Annotated
cli = typer.Typer()

console = Console(stderr=True)


@cli.command(context_settings={"ignore_unknown_options": True})
def run(  # noqa: PLR0913
    script: Annotated[
        Optional[Path],  # noqa: FA100  # Typer can't handle unions
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="The path of the script to run (modules only)",
        ),
    ] = None,
    args: Annotated[
        Optional[List[str]],  # noqa: FA100
        typer.Argument(
            help="Arguments to pass to the script",
        ),
    ] = None,
    python_flags: Annotated[
        Optional[List[str]],  # noqa: FA100
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
    clean: Annotated[
        bool,
        typer.Option(
            help="Clean the virtual environment caches",
        ),
    ] = False,
    force_version: Annotated[
        Optional[str],  # noqa: FA100
        typer.Option(
            "--force-version",
            "-f",
            help="Force idae to use a specific Python version",
        ),
    ] = None,
) -> None:
    """Automatically install necessary dependencies to run a Python script.

    --clean can be used without 'SCRIPT'
    """
    if clean:
        clean_venvs()
    if script is None:
        if clean:
            raise typer.Exit(code=0)
        msg = "Missing argument 'SCRIPT'."
        raise UsageError(msg)
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
        python = get_python_or_exit(force_version, console)
    if pyproject is not None:
        script_deps = (
            []
            if "dependencies" not in pyproject
            else list(map(Requirement, pyproject["dependencies"]))
        )

        if (
            not ignore_version
            and force_version is None
            and "requires-python" in pyproject
        ):
            python = get_python_or_exit(pyproject["requires-python"], console)

    venv_path = get_venv(script_deps, python)

    extra_flags = list(
        itertools.chain.from_iterable(
            map(shlex.split, python_flags or []),
        ),
    )
    extra_args = list(
        itertools.chain.from_iterable(
            map(shlex.split, args or []),
        ),
    )
    # Run the script inside the venv
    raise typer.Exit(
        code=subprocess.run(
            [  # noqa: S603  # idae is inherently "insecure"
                str(
                    venv_path
                    / ("Scripts" if platform.system() == "Windows" else "bin")
                    / "python",
                ),
                *extra_flags,
                str(script),
                *extra_args,
            ],
            check=False,
        ).returncode,
    )
