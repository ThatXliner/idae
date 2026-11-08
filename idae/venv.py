"""Utils for venv creation."""

from __future__ import annotations

import hashlib
import logging
import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import platformdirs
from filelock import FileLock, Timeout
from uv import find_uv_bin

if TYPE_CHECKING:  # pragma: no cover
    from os import PathLike
    from pathlib import Path

    from packaging.requirements import Requirement
    from packaging.version import Version

from .dependencies import hash_dependencies

CACHE_DIR = platformdirs.user_cache_path("idae")

logger = logging.getLogger("idae")


@dataclass
class Python:
    """Object representing a Python executable."""

    version: Version
    executable: str | PathLike[str]


def venv_python(venv_path: Path) -> Path:
    """Return the interpreter inside ``venv_path``."""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def cache_key(requirements: list[Requirement], python: Python) -> str:
    """Return the key identifying a venv for these deps and Python."""
    # Do not reuse environments installed with pre-compromise bundled pip.
    dep_hash = "tls-2026-10-19-" + hash_dependencies(requirements)
    return f"{python.version.major}.{python.version.minor}/{dep_hash}"


def is_venv_usable(venv_path: Path, key: str) -> bool:
    """Return True if ``venv_path`` finished installing ``key`` and has Python."""
    # .idae-ready is empty while installing and holds the key once done.
    ready = venv_path / ".idae-ready"
    return (
        ready.is_file() and ready.read_text() == key and venv_python(venv_path).exists()
    )


def get_venv(
    requirements: list[Requirement],
    python: Python,
    venv_dir: Path | None = None,
) -> Path:
    """Create or fetch a venv, cached unless ``venv_dir`` is given."""
    key = cache_key(requirements, python)
    venv_path = CACHE_DIR / key if venv_dir is None else venv_dir
    # Concurrent runs on one venv would delete each other's half-built venv.
    # The lock lives outside the venv, which gets rmtree'd on rebuild.
    digest = hashlib.sha256(str(venv_path.resolve()).encode()).hexdigest()
    lock_path = CACHE_DIR / "locks" / f"{digest}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(lock_path)
    try:
        lock.acquire(timeout=0)
    except Timeout:
        logger.info("Waiting for another idae process to set up %s", venv_path)
        lock.acquire()
    try:
        return _ensure_venv(requirements, python, venv_path, key, venv_dir)
    finally:
        lock.release()


def _ensure_venv(
    requirements: list[Requirement],
    python: Python,
    venv_path: Path,
    key: str,
    venv_dir: Path | None,
) -> Path:
    ready = venv_path / ".idae-ready"
    if is_venv_usable(venv_path, key):
        logger.debug("Reusing venv at %s", venv_path)
        return venv_path
    if (
        venv_dir is not None
        and venv_dir.is_dir()
        and not ready.is_file()
        and any(venv_dir.iterdir())
    ):
        msg = f"{venv_dir} is not empty and was not created by idae"
        raise FileExistsError(msg)
    if venv_path.exists():
        logger.info("Rebuilding venv at %s", venv_path)
        shutil.rmtree(venv_path)
    else:
        logger.info("Creating venv at %s", venv_path)
    quiet: dict[str, Any] = (
        {}
        if logger.isEnabledFor(logging.DEBUG)
        else {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
    )
    venv_path.mkdir(parents=True)
    ready.write_text("")
    try:
        subprocess.run(
            [python.executable, "-m", "venv", "--without-pip", venv_path],  # noqa: S603
            check=True,
            **quiet,
        )
        # Dependency installation uses the patched uv bundled with idae.
        if requirements:
            subprocess.run(
                [  # noqa: S603
                    find_uv_bin(),
                    "pip",
                    "install",
                    "--python",
                    venv_python(venv_path),
                    *map(str, requirements),
                ],
                check=True,
                **quiet,
            )
    except BaseException:
        shutil.rmtree(venv_path, ignore_errors=True)
        raise
    # The above works according to the Python docs:
    # > You don't specifically need to activate a virtual environment,
    # > as you can just specify the full path to that environment`s Python interpreter
    # > when invoking Python. Furthermore, all scripts installed in the environment
    # > should be runnable without activating it.
    # - https://docs.python.org/3/library/venv.html#how-venvs-work
    ready.write_text(key)
    return venv_path


def clean_venvs() -> None:
    """CLI command to delete the cache."""
    # Ignore errors like the directory not existing
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
