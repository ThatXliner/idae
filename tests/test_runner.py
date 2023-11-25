# ruff: noqa: ANN003, ANN002, ANN001, ANN201
import shutil
import sys
import time

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


CACHE_DIR = platformdirs.user_cache_path("idae")


@pytest.fixture()
def empty_cache() -> None:
    if CACHE_DIR.is_dir():
        shutil.rmtree(CACHE_DIR, ignore_errors=True)


@pytest.mark.usefixtures("empty_cache")
def test_main(capfd):
    result = runner.invoke(
        cli,
        ["run", "tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out == EXAMPLE_OUTPUT


@pytest.mark.usefixtures("empty_cache")
def test_clean_venvs(capfd):
    result = runner.invoke(
        cli,
        ["run", "tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out == EXAMPLE_OUTPUT

    result = runner.invoke(
        cli,
        ["clean"],
    )
    assert result.exit_code == 0
    assert not CACHE_DIR.exists()


@pytest.mark.usefixtures("empty_cache")
def test_ignore_version(capfd):
    result = runner.invoke(
        cli,
        ["run", "--ignore-version", "tests/examples/impossible_python.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    # We have to use this instead of result.stdout
    # As Click doesn't capture the stdin fileno
    assert out == EXAMPLE_OUTPUT


@pytest.mark.usefixtures("empty_cache")
def test_caching(capfd):
    start = time.time()
    result = runner.invoke(
        cli,
        ["run", "tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out == EXAMPLE_OUTPUT
    without_cache = time.time() - start
    start = time.time()
    result = runner.invoke(
        cli,
        ["run", "tests/examples/rich_requests.py"],
    )
    out, _ = capfd.readouterr()
    assert result.exit_code == 0
    assert out == EXAMPLE_OUTPUT
    assert time.time() - start < without_cache


@pytest.mark.usefixtures("empty_cache")
def test_impossible_python():
    result = runner.invoke(
        cli,
        ["run", "tests/examples/impossible_python.py"],
    )
    assert result.exit_code == 1
    assert "not found" in result.stderr


class TestForceFlags:
    @pytest.mark.usefixtures("empty_cache")
    def test_force_version_impossible_python(self):
        result = runner.invoke(
            cli,
            [
                "run",
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
                "run",
                "--force-version",
                ".".join(map(str, sys.version_info[:2])),
                "tests/examples/impossible_python.py",
            ],
        )
        assert result.exit_code == 0
        out, _ = capfd.readouterr()
        assert out == EXAMPLE_OUTPUT

    @pytest.mark.usefixtures("empty_cache")
    def test_force_short_impossible_python(self):
        result = runner.invoke(
            cli,
            ["run", "-f", "69420", "tests/examples/rich_requests.py"],
        )
        assert result.exit_code == 1
        assert "not found" in result.stderr
