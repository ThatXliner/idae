import pytest
from packaging.specifiers import InvalidSpecifier

from idae.pep723 import read
from idae.resolver import get_python

DUPE_PYPROJECT = """
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///


# /// script
# requires-python = "69420"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///


import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")  # noqa: S113
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
"""
NO_PYPROJECT = """
import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")  # noqa: S113
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
"""
EXAMPLE = """
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///


import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")  # noqa: S113
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
"""


def test_multiple_deps():
    with pytest.raises(ValueError, match="(?i)multiple"):
        read(DUPE_PYPROJECT)


def test_no_deps():
    assert read(NO_PYPROJECT) is None


def test_normal_deps():
    assert read(EXAMPLE) == {
        "dependencies": ["requests<3", "rich"],
        "requires-python": ">=3.11",
    }


def test_invalid_specifier():
    with pytest.raises(InvalidSpecifier):
        get_python("~^&10")
