"""Slightly modified code from the example in PEP 723."""

import re
from typing import Any

try:
    import tomllib  # type: ignore[import, unused-ignore]
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[import, unused-ignore, no-redef]

REGEX = r'(?ms)^__pyproject__ *= *"""\\?$(.+?)^"""$'


def read(script: str) -> Any:  # noqa: ANN401
    """Return the contents of the __pyproject__ variable."""
    matches = list(re.finditer(REGEX, script))
    if len(matches) > 1:
        msg = "Multiple __pyproject__ definitions found"
        raise ValueError(msg)
    if len(matches) == 1:
        return tomllib.loads(matches[0][1])
    return None
