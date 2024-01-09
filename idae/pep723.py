"""Custom parser following the specification from PEP 723.

Copy+pasted from the PEP 723 reference implementation
"""
from __future__ import annotations

import re
from typing import Any

try:
    import tomllib  # type: ignore[import, unused-ignore]
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[import, unused-ignore, no-redef]

# Copy+pasted from the PEP 723
REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"


def read(script: str) -> dict | None:
    name = "script"
    matches = list(
        filter(lambda m: m.group("type") == name, re.finditer(REGEX, script))
    )
    if len(matches) > 1:
        raise ValueError(f"Multiple {name} blocks found")
    elif len(matches) == 1:
        content = "".join(
            line[2:] if line.startswith("# ") else line[1:]
            for line in matches[0].group("content").splitlines(keepends=True)
        )
        return tomllib.loads(content)
    else:
        return None
