# ruff: noqa: S603
"""The main CLI entry point."""

import shutil
import signal
import sys
from pathlib import Path

import pexpect  # type: ignore[import]
from packaging.requirements import Requirement
from packaging.version import Version

from idae.pep723 import read
from idae.venv import Python, clean_venvs, get_venv
from idae.resolver import get_python


def main() -> None:
    """Run the app."""
    if len(sys.argv) != 2:  # noqa: PLR2004
        print(f"Usage: {sys.argv[0]} (<script>|clean)")
        sys.exit(1)

    if sys.argv[1] == "clean":
        clean_venvs()
        return

    # Get scrip dependencies
    script = Path(sys.argv[1]).resolve()
    pyproject = read(str(script.read_text()))
    script_deps = []
    python_version = Version(
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )
    python_executable = sys.executable
    if pyproject is not None and "run" in pyproject:
        script_deps = (
            []
            if "dependencies" not in pyproject["run"]
            else list(map(Requirement, pyproject["run"]["dependencies"]))
        )
        if "requires-python" in pyproject["run"]:
            python = get_python(pyproject["run"]["requires-python"])
            # TODO(ThatXliner): A flag for ignoring this
            # https://github.com/ThatXliner/idae/issues/1
            if not python:
                msg = f"Python version {pyproject['run']['requires-python']} not found"
                raise RuntimeError(msg)
            python_version = python.version
            # python.executable may be a symlink
            # which shouldn't cause problems.
            # If it does, then change this code to use
            # python.real_path
            python_executable = str(python.executable)

    venv_path = get_venv(
        script_deps,
        Python(version=python_version, executable=python_executable),
    )

    # Run the script inside the venv
    terminal = shutil.get_terminal_size()
    # Copied from poetry source, slightly modified
    child = pexpect.spawn(
        str((venv_path / "bin/python").resolve()),
        sys.argv[1:],
        dimensions=(terminal.lines, terminal.columns),
    )

    def resize(_: object, __: object) -> None:
        terminal = shutil.get_terminal_size()
        child.setwinsize(terminal.lines, terminal.columns)

    signal.signal(signal.SIGWINCH, resize)
    child.interact(escape_character=None)
    child.close()
    # End modified copy


if __name__ == "__main__":
    main()
