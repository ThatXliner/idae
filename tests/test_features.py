# ruff: noqa: ANN001
import shutil
import subprocess
import sys

import findpython
import platformdirs
import pytest
from packaging.requirements import Requirement
from packaging.version import Version
from typer.testing import CliRunner

from idae.cli import cli
from idae.resolver import get_python
from idae.venv import Python, get_venv, venv_python

runner = CliRunner(mix_stderr=False)

CACHE_DIR = platformdirs.user_cache_path("idae")

PYTHON = Python(
    version=Version(f"{sys.version_info.major}.{sys.version_info.minor}"),
    executable=sys.executable,
)

SIX_SCRIPT = """\
# /// script
# dependencies = ["six"]
# ///
import six
print(six.__name__)
"""


@pytest.fixture()
def empty_cache() -> None:  # noqa: PT004
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
    assert venv_python(target).exists()
    assert not list(CACHE_DIR.rglob(".idae-ready")), "no venv built in the cache"


@pytest.mark.usefixtures("empty_cache")
def test_venv_dir_envvar(capfd, tmp_path):
    target = tmp_path / "fromenv"
    result = runner.invoke(
        cli,
        ["tests/examples/echo.py", "hi"],
        env={"IDAE_VENV_DIR": str(target)},
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "") == "hi\n"
    assert venv_python(target).exists()
    assert not list(CACHE_DIR.rglob(".idae-ready")), "no venv built in the cache"


def test_venv_dir_rebuilds_when_dependencies_change(capfd, tmp_path):
    target = tmp_path / "v"
    script = tmp_path / "six_script.py"
    script.write_text(SIX_SCRIPT)
    first = runner.invoke(cli, ["--venv-dir", str(target), "tests/examples/echo.py"])
    assert first.exit_code == 0
    result = runner.invoke(cli, ["--venv-dir", str(target), str(script)])
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "").endswith("six\n")


def test_venv_dir_refuses_foreign_directory(tmp_path):
    keep = tmp_path / "keep.txt"
    keep.write_text("mine")
    result = runner.invoke(cli, ["--venv-dir", str(tmp_path), "tests/examples/echo.py"])
    assert result.exit_code == 1
    assert keep.read_text() == "mine"


@pytest.mark.parametrize("damage", ["interpreter", "marker"])
def test_broken_venv_is_recreated(tmp_path, damage):
    venv_path = get_venv([], PYTHON, tmp_path / "v")
    if damage == "interpreter":
        venv_python(venv_path).unlink()
    else:
        (venv_path / ".idae-ready").write_text("")
    venv_path = get_venv([], PYTHON, tmp_path / "v")
    assert venv_python(venv_path).exists()
    assert (venv_path / ".idae-ready").read_text()


def test_failed_install_removes_partial_venv(tmp_path):
    with pytest.raises(subprocess.CalledProcessError):
        get_venv(
            [Requirement("idae-test-package-that-does-not-exist==0.0.0")],
            PYTHON,
            tmp_path / "v",
        )
    assert not (tmp_path / "v").exists()


@pytest.mark.usefixtures("empty_cache")
def test_requires_python_reuses_cached_venv():
    oldest = [p for p in findpython.find_all() if p.version >= Version("3.8")][-1]
    get_venv([], Python(oldest.version, oldest.executable))
    chosen = get_python(f">={oldest.version}", requirements=[])
    assert chosen is not None
    assert chosen.version.release[:2] == oldest.version.release[:2]


@pytest.mark.usefixtures("empty_cache")
def test_verbose_flag():
    proc = subprocess.run(
        [sys.executable, "-m", "idae", "-v", "tests/examples/echo.py", "hello"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stdout.replace("\r", "") == "hello\n"
    assert "Creating venv" in proc.stderr
    assert "Running" in proc.stderr
