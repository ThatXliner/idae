"""CLI interface."""

import itertools
import logging
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
from rich.logging import RichHandler

from idae.pep723 import read
from idae.resolver import get_python_or_exit
from idae.venv import Python, clean_venvs, get_venv, venv_python

if sys.version_info < (3, 9):  # pragma: no cover
    from typing_extensions import Annotated
else:
    from typing import Annotated
cli = typer.Typer()

console = Console(stderr=True)
logger = logging.getLogger("idae")


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
    venv_dir: Annotated[
        Optional[Path],  # noqa: FA100
        typer.Option(
            "--venv-dir",
            envvar="IDAE_VENV_DIR",
            help="Create/reuse the venv at this directory instead of the cache",
            file_okay=False,
            resolve_path=True,
        ),
    ] = None,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="-v logs venv decisions, -vv also streams uv output",
        ),
    ] = 0,
) -> None:
    """Automatically install necessary dependencies to run a Python script.

    --clean can be used without 'SCRIPT'
    """
    logging.basicConfig(
        level=[logging.WARNING, logging.INFO, logging.DEBUG][min(verbose, 2)],
        format="%(message)s",
        handlers=[RichHandler(console=console, show_path=False)],
    )
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
            python = get_python_or_exit(
                pyproject["requires-python"],
                console,
                requirements=script_deps,
            )

    try:
        venv_path = get_venv(script_deps, python, venv_dir)
    except FileExistsError as err:
        console.print(f"[red]error: {err}[/red]")
        raise typer.Exit(code=1) from err

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
    logger.info("Running %s with Python %s", script, python.version)
    # Run the script inside the venv
    raise typer.Exit(
        code=subprocess.run(
            [  # noqa: S603  # idae is inherently "insecure"
                str(venv_python(venv_path)),
                *extra_flags,
                str(script),
                *extra_args,
            ],
            check=False,
        ).returncode,
    )
