import pytest
from idae.pep723 import read

DUPE_PYPROJECT = '''
__pyproject__ = """
[project]
requires-python = ">=3.11"
dependencies = [
  "requests<3",
  "rich",
]
"""

__pyproject__ = """
[project]
requires-python = "69420"
dependencies = [
]
"""

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")  # noqa: S113
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
'''
NO_PYPROJECT = """
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
