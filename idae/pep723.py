"""Slightly modified code from the example in PEP 723."""
from __future__ import annotations

import re

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

REGEX = r'(?ms)^__pyproject__ *= *"""\\?$(.+?)^"""$'


def read(script: str) -> dict | None:
    """Return the contents of the __pyproject__ variable."""
    matches = list(re.finditer(REGEX, script))
    if len(matches) > 1:
        msg = "Multiple __pyproject__ definitions found"
        raise ValueError(msg)
    if len(matches) == 1:
        return tomllib.loads(matches[0][1])
    return None
