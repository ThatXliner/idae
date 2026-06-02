"""CLI interface."""
import itertools
import logging
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
from rich.logging import RichHandler

from idae.dependencies import hash_dependencies
from idae.pep723 import read
from idae.resolver import get_python_or_exit
from idae.venv import Python, clean_venvs, get_venv

if sys.version_info < (3, 9):  # pragma: no cover
    from typing_extensions import Annotated
else:
    from typing import Annotated
cli = typer.Typer()

console = Console(stderr=True)
logger = logging.getLogger("idae")


def _setup_logging(verbose: int) -> None:
    """Configure logging from a -v count (0=warning, 1=info, 2+=debug)."""
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:  # noqa: PLR2004
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_path=False, rich_tracebacks=True)],
    )


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
            help="Create/reuse the venv at this directory instead of the cache",
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = None,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Increase verbosity (-v for info, -vv for debug + pip output)",
        ),
    ] = 0,
) -> None:
    """Automatically install necessary dependencies to run a Python script.

    --clean can be used without 'SCRIPT'
    """
    _setup_logging(verbose)
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
    if pyproject is not None:
        script_deps = (
            []
            if "dependencies" not in pyproject
            else list(map(Requirement, pyproject["dependencies"]))
        )
    dep_hash = hash_dependencies(script_deps)
    if force_version is not None:
        python = get_python_or_exit(force_version, console)
    elif (
        not ignore_version and pyproject is not None and "requires-python" in pyproject
    ):
        # Prefer an existing cached venv whose Python satisfies the clause (#14)
        python = get_python_or_exit(
            pyproject["requires-python"],
            console,
            dep_hash=dep_hash,
        )

    venv_path = get_venv(script_deps, python, venv_dir=venv_dir)

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
    logger.info("Running %s with %s", script, python.version)
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
