# ruff: noqa: S603 (no untrusted)
"""The main CLI entry point."""

import atexit
import shutil
import signal
import subprocess
import sys
import venv
from pathlib import Path

import pexpect

from idae.pep772 import read_dependency_block

VENV_NAME = "idae-venv"


def main() -> None:
    """Run the app."""
    # Get scrip dependencies
    script = Path(sys.argv[1]).resolve()
    script_deps = list(read_dependency_block(str(script)))
    # Create a venv
    venv.create(VENV_NAME, with_pip=True)
    atexit.register(lambda: shutil.rmtree(str(Path(VENV_NAME).resolve())))
    venv_binary_path = Path(".") / VENV_NAME / "bin"
    # Install dependencies into the venv
    subprocess.run(
        [str((venv_binary_path / "pip").resolve()), "install", *script_deps],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    # The above works according to the Python docs:
    # > You don't specifically need to activate a virtual environment,
    # > as you can just specify the full path to that environment’s Python interpreter
    # > when invoking Python. Furthermore, all scripts installed in the environment
    # > should be runnable without activating it.
    # - https://docs.python.org/3/library/venv.html#how-venvs-work

    # Run the script inside the venv
    terminal = shutil.get_terminal_size()
    # Copied from poetry source, slightly modified
    child = pexpect.spawn(
        str((venv_binary_path / "python").resolve()),
        sys.argv[1:],
        dimensions=(terminal.lines, terminal.columns),
    )

    def resize(_, __) -> None:
        terminal = shutil.get_terminal_size()
        child.setwinsize(terminal.lines, terminal.columns)

    signal.signal(signal.SIGWINCH, resize)
    child.interact(escape_character=None)
    child.close()
    # End modified copy


if __name__ == "__main__":
    main()
