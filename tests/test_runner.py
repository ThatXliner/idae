# ruff: noqa: ANN003, ANN002, ANN001, ANN201

from typer.testing import CliRunner

from idae.cli import cli, run
import pytest
import typer
from contextlib import redirect_stdout
import io


import pexpect
from pathlib import Path

runner = CliRunner(mix_stderr=False)

EXAMPLE_OUTPUT_WITH_COLOR = """\033[1m[\033[0m
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'1'\033[0m, \033[32m'PEP Purpose and Guidelines'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'2'\033[0m, \033[32m'Procedure for Adding New Modules'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'3'\033[0m, \033[32m'Guidelines for Handling Bug Reports'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'4'\033[0m, \033[32m'Deprecation of Standard Modules'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'5'\033[0m, \033[32m'Guidelines for Language Evolution'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'6'\033[0m, \033[32m'Bug Fix Releases'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'7'\033[0m, \033[32m'Style Guide for C Code'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'8'\033[0m, \033[32m'Style Guide for Python Code'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'9'\033[0m, \033[32m'Sample Plaintext PEP Template'\033[0m\033[1m)\033[0m,
\033[2;32m│   \033[0m\033[1m(\033[0m\033[32m'10'\033[0m, \033[32m'Voting Guidelines'\033[0m\033[1m)\033[0m
\033[1m]\033[0m
"""  # noqa: E501: line-too-long
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
]"""


def patched_init(self, *args, **kwargs):
    kwargs["encoding"] = "utf-8"  # Specify the encoding parameter
    self._original_init(*args, **kwargs)


def test_main(monkeypatch):
    monkeypatch.setattr(
        pexpect.spawn,
        "interact",
        lambda self, *_, **__: self.expect(EXAMPLE_OUTPUT),
    )
    original_init = pexpect.spawn.__init__
    monkeypatch.setattr(pexpect.spawn, "__init__", patched_init)
    pexpect.spawn._original_init = original_init  # noqa: SLF001
    f = io.StringIO()
    with redirect_stdout(f), pytest.raises(typer.Exit) as exc_info:
            run(Path("tests/examples/rich_requests.py"))
    assert exc_info.value.args == 0, (exc_info, exc_info.value.code, exc_info.traceback[-1])
    assert f.getvalue() == EXAMPLE_OUTPUT


def test_impossible_python():
    result = runner.invoke(
        cli,
        ["run", "tests/examples/impossible_python.py"],
    )
    print(result)
    assert result.exit_code == 1
    assert "not found" in result.stderr
