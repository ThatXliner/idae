# ruff: noqa: ANN003, ANN002, ANN001, ANN201
import sys

import pexpect
import pytest

from idae.__main__ import main

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
    if sys.version_info < (3, 11):
        monkeypatch.setattr(
            sys,
            "argv",
            ["idae", "tests/examples/rich_requests_big_python.py"],
        )
        monkeypatch.setattr(
            pexpect.spawn,
            "interact",
            lambda self, *_, **__: self.expect(EXAMPLE_OUTPUT),
        )
        original_init = pexpect.spawn.__init__
        monkeypatch.setattr(pexpect.spawn, "__init__", patched_init)
        pexpect.spawn._original_init = original_init  # noqa: SLF001
        if sys.version_info < (3, 8):  # noqa: UP036
            with pytest.raises(RuntimeError):
                main()
        else:
            main()
    else:
        monkeypatch.setattr(sys, "argv", ["idae", "tests/examples/rich_requests.py"])
        monkeypatch.setattr(
            pexpect.spawn,
            "interact",
            lambda self, *_, **__: self.expect(EXAMPLE_OUTPUT),
        )
        original_init = pexpect.spawn.__init__
        monkeypatch.setattr(pexpect.spawn, "__init__", patched_init)
        pexpect.spawn._original_init = original_init  # noqa: SLF001
        main()
