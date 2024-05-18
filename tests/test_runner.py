# ruff: noqa: ANN003, ANN002, ANN001, ANN201
import platform
import shutil
import sys
import time
from pathlib import Path

import platformdirs
import pytest
from typer.testing import CliRunner

from idae.cli import cli

runner = CliRunner(mix_stderr=False)

EXAMPLE_OUTPUT = """[
│   ('1', 'PEP Purpose and Guidelines'),
│   ('2', 'Procedure for Adding New Modules'),
│   ('3', 'Guidelines for Handling Bug Reports'),
│   ('4', 'Deprecation of Standard Modules'),
│   ('5', 'Guidelines for Language Evolution'),
│   ('6', 'Bug Fix Releases'),
│   ('7', 'Style Guide for C Code'),
│   ('8', 'Style Guide for Python Code'),
│   ('9', 'Sample Plaintext PEP Template'),
│   ('10', 'Voting Guidelines')
]
"""
EXAMPLE_OUTPUT_ASCII = """[
    ('1', 'PEP Purpose and Guidelines'),
    ('2', 'Procedure for Adding New Modules'),
    ('3', 'Guidelines for Handling Bug Reports'),
    ('4', 'Deprecation of Standard Modules'),
    ('5', 'Guidelines for Language Evolution'),
    ('6', 'Bug Fix Releases'),
    ('7', 'Style Guide for C Code'),
    ('8', 'Style Guide for Python Code'),
    ('9', 'Sample Plaintext PEP Template'),
    ('10', 'Voting Guidelines')
]
"""
if platform.system() == "Windows":
    EXAMPLE_OUTPUT = EXAMPLE_OUTPUT_ASCII

CACHE_DIR = platformdirs.user_cache_path("idae")


@pytest.fixture()
def empty_cache() -> None:
    if CACHE_DIR.is_dir():
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
    if Path(".idae").is_dir():
        shutil.rmtree(Path(".idae"), ignore_errors=True)


@pytest.mark.usefixtures("empty_cache")
def test_main(capfd):
    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out.replace("\r", "") == EXAMPLE_OUTPUT


def test_args(capfd):
    result = runner.invoke(
        cli,
        ["tests/examples/echo.py", "hello world"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out.replace("\r", "") == "hello world\n"


def test_exotic_args(capfd):
    result = runner.invoke(
        cli,
        ["tests/examples/echo.py", "hello world -- -h 237"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out.replace("\r", "") == "hello world -- -h 237\n"


@pytest.mark.usefixtures("empty_cache")
def test_clean_venvs(capfd):
    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out.replace("\r", "") == EXAMPLE_OUTPUT

    result = runner.invoke(
        cli,
        ["--clean"],
    )
    assert result.exit_code == 0
    assert not CACHE_DIR.exists()


@pytest.mark.usefixtures("empty_cache")
def test_use_current_dir(capfd):
    old_files = set(Path().iterdir())

    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py", "--in-cwd"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out.replace("\r", "") == EXAMPLE_OUTPUT

    new_files = set(Path().iterdir())
    assert Path(".idae") in new_files - old_files


@pytest.mark.usefixtures("empty_cache")
def test_ignore_version(capfd):
    result = runner.invoke(
        cli,
        ["--ignore-version", "tests/examples/impossible_python.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out.replace("\r", "") == EXAMPLE_OUTPUT


@pytest.mark.usefixtures("empty_cache")
def test_caching(capfd):
    start = time.time()
    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "") == EXAMPLE_OUTPUT
    without_cache = time.time() - start
    start = time.time()
    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "") == EXAMPLE_OUTPUT
    assert time.time() - start < without_cache


@pytest.mark.usefixtures("empty_cache")
def test_clean_cache(capfd):
    # Initial to fill up cache
    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "") == EXAMPLE_OUTPUT

    start = time.time()
    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "") == EXAMPLE_OUTPUT
    with_cache = time.time() - start

    start = time.time()
    result = runner.invoke(
        cli,
        ["tests/examples/rich_requests.py", "--clean"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out.replace("\r", "") == EXAMPLE_OUTPUT
    assert time.time() - start > with_cache


@pytest.mark.usefixtures("empty_cache")
def test_impossible_python():
    result = runner.invoke(
        cli,
        ["tests/examples/impossible_python.py"],
    )
    assert result.exit_code == 1
    assert "not found" in result.stderr


@pytest.mark.usefixtures("empty_cache")
def test_force_version_impossible_python():
    result = runner.invoke(
        cli,
        [
            "tests/examples/rich_requests.py",
            "--force-version",
            "~&%29",
        ],
    )
    assert result.exit_code == 1
    assert "parsed" in result.stderr


class TestForceFlags:
    @pytest.mark.usefixtures("empty_cache")
    def test_force_version_impossible_python(self):
        result = runner.invoke(
            cli,
            [
                "tests/examples/rich_requests.py",
                "--force-version",
                "69420",
            ],
        )
        assert result.exit_code == 1
        assert "not found" in result.stderr

    @pytest.mark.usefixtures("empty_cache")
    def test_force_version_python(self, capfd):
        result = runner.invoke(
            cli,
            [
                "--force-version",
                ".".join(map(str, sys.version_info[:2])),
                "tests/examples/impossible_python.py",
            ],
        )
        assert result.exit_code == 0
        out, _ = capfd.readouterr()
        assert out.replace("\r", "") == EXAMPLE_OUTPUT

    @pytest.mark.usefixtures("empty_cache")
    def test_force_short_impossible_python(self):
        result = runner.invoke(
            cli,
            ["-f", "69420", "tests/examples/rich_requests.py"],
        )
        assert result.exit_code == 1
        assert "not found" in result.stderr
