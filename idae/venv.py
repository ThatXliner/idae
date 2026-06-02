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


@dataclass
class Python:
    """Object representing a Python executable."""

    version: Version
    executable: str | PathLike[str]


def _bin_dir(venv_path: Path) -> Path:
    return venv_path / ("Scripts" if platform.system() == "Windows" else "bin")


def is_venv_usable(venv_path: Path) -> bool:
    """Return True if ``venv_path`` looks like a working virtual environment."""
    # A venv is broken if its interpreter is missing (issue #11).
    return _bin_dir(venv_path).joinpath("python").exists()


def cache_venv_path(dep_hash: str, python: Python) -> Path:
    """Return the cache location for a venv with the given deps and Python."""
    return CACHE_DIR / f"{python.version.major}.{python.version.minor}" / dep_hash


def _populate_venv(
    venv_path: Path,
    requirements: list[Requirement],
    python: Python,
) -> None:
    """Create a venv at ``venv_path`` and install ``requirements`` into it.

    Removes the partially-built venv if creation or installation fails or is
    interrupted (issue #16).
    """
    try:
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
                    (_bin_dir(venv_path) / "pip").resolve(),
                    "install",
                    *map(str, requirements),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )
    except (subprocess.CalledProcessError, KeyboardInterrupt, OSError):
        shutil.rmtree(venv_path, ignore_errors=True)
        raise
    # The above works according to the Python docs:
    # > You don't specifically need to activate a virtual environment,
    # > as you can just specify the full path to that environment`s Python interpreter
    # > when invoking Python. Furthermore, all scripts installed in the environment
    # > should be runnable without activating it.
    # - https://docs.python.org/3/library/venv.html#how-venvs-work


def get_venv(requirements: list[Requirement], python: Python) -> Path:
    """Create or fetch a cached venv."""
    dep_hash = hash_dependencies(requirements)
    venv_path = cache_venv_path(dep_hash, python)
    if venv_path.is_dir():
        if is_venv_usable(venv_path):
            return venv_path
        # Broken leftover (e.g. missing bin/python); rebuild it (issue #11).
        shutil.rmtree(venv_path, ignore_errors=True)
    _populate_venv(venv_path, requirements, python)
    return venv_path


def clean_venvs() -> None:
    """CLI command to delete the cache."""
    # Ignore errors like the directory not existing
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
