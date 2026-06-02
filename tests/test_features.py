# ruff: noqa: ANN001, ANN202
"""Tests for venv-dir, broken-venv handling, and verbosity (issues #10/#11/#15)."""
import platform
import shutil
import subprocess
import sys

import platformdirs
import pytest
from packaging.version import Version
from typer.testing import CliRunner

from idae.cli import cli
from idae.venv import Python, get_venv, is_venv_usable

runner = CliRunner()

CACHE_DIR = platformdirs.user_cache_path("idae")


def _bin(venv_path):
    return venv_path / ("Scripts" if platform.system() == "Windows" else "bin")


@pytest.fixture()
def empty_cache():  # noqa: PT004
    if CACHE_DIR.is_dir():
        shutil.rmtree(CACHE_DIR, ignore_errors=True)


@pytest.mark.usefixtures("empty_cache")
def test_venv_dir(capfd, tmp_path):
    target = tmp_path / "myvenv"
    result = runner.invoke(
        cli,
        ["--venv-dir", str(target), "tests/examples/echo.py", "hi"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "") == "hi\n"
    # The venv was created at the requested location, not the cache.
    assert is_venv_usable(target)
    assert not CACHE_DIR.exists()


def test_broken_venv_is_recreated(tmp_path):
    python = Python(
        version=Version("3.12.0"),
        executable=sys.executable,
    )
    # Build a real venv, then break it by deleting the interpreter.
    venv_path = get_venv([], python, venv_dir=tmp_path / "v")
    assert is_venv_usable(venv_path)
    for name in ("python", "python.exe"):
        (_bin(venv_path) / name).unlink(missing_ok=True)
    assert not is_venv_usable(venv_path)
    # get_venv should notice the breakage and rebuild a usable venv.
    venv_path = get_venv([], python, venv_dir=tmp_path / "v")
    assert is_venv_usable(venv_path)


@pytest.mark.usefixtures("empty_cache")
def test_verbose_flag():
    # Rich's Console doesn't play well with CliRunner's stream capture, so run
    # idae as a real subprocess to observe the -v logging on stderr.
    proc = subprocess.run(
        [sys.executable, "-m", "idae", "-v", "tests/examples/echo.py", "hello"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stdout.replace("\r", "") == "hello\n"
    # -v enables info logging, which reports the run on stderr.
    assert "Running" in proc.stderr
