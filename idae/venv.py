"""Utils for venv creation."""

from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

import platformdirs

if TYPE_CHECKING:  # pragma: no cover
    from os import PathLike
    from pathlib import Path

    from packaging.requirements import Requirement
    from packaging.version import Version

from .dependencies import hash_dependencies

CACHE_DIR = platformdirs.user_cache_path("idae")
IDAE_VENV_DIR_NAME = ".idae"


@dataclass
class Python:
    """Object representing a Python executable."""

    version: Version
    executable: str | PathLike[str]


def get_venv(
    requirements: list[Requirement],
    python: Python,
    in_dir: PathLike | None = None,
    venv_name: str = IDAE_VENV_DIR_NAME,
) -> Path:
    """Create or fetch a cached venv."""
    dep_hash = hash_dependencies(requirements)
    venv_path = (
        (in_dir / venv_name if in_dir is not None else CACHE_DIR)
        / f"{python.version.major}.{python.version.minor}"
        / dep_hash
    )
    if venv_path.is_dir():
        return venv_path
    # This automatically includes pip
    subprocess.run(
        [python.executable, "-m", "venv", venv_path],  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    # Install dependencies into the venv (if any)
    if requirements:
        subprocess.run(
            [  # noqa: S603
                (
                    venv_path
                    / ("Scripts" if platform.system() == "Windows" else "bin")
                    / "pip"
                ).resolve(),
                "install",
                *map(str, requirements),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
    # The above works according to the Python docs:
    # > You don't specifically need to activate a virtual environment,
    # > as you can just specify the full path to that environment`s Python interpreter
    # > when invoking Python. Furthermore, all scripts installed in the environment
    # > should be runnable without activating it.
    # - https://docs.python.org/3/library/venv.html#how-venvs-work
    return venv_path


def clean_venvs() -> None:
    """CLI command to delete the cache."""
    # Ignore errors like the directory not existing
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
