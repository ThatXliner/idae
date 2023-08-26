"""Custom parser following the specification from PEP 723."""
from __future__ import annotations

import re
from typing import Any

try:
    import tomllib  # type: ignore[import, unused-ignore]
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[import, unused-ignore, no-redef]
COMMENT_BLOCK_REGEX = re.compile(
    r"^\s*#\s*///\s*(?P<type>[a-zA-Z0-9-]+)$\s*(?P<content>(?:^#.*$\s)+)^\s*#\s*///$",
    flags=re.MULTILINE,
)
COMMENT_REGEX = re.compile(r"^\s*#\s*(.+)$", flags=re.MULTILINE)


def read_comment_block(script: str, name: str) -> str | None:
    """Find and returns the contents of the metadata comment block."""
    matches = list(
        filter(
            lambda m: m.group("type") == name,
            re.finditer(COMMENT_BLOCK_REGEX, script),
        ),
    )
    if len(matches) > 1:
        msg = f"Multiple {name} blocks found"
        raise ValueError(msg)
    if len(matches) == 1:
        return "\n".join(COMMENT_REGEX.findall(matches[0].group("content")))
    return None


def read(script: str) -> Any:  # noqa: ANN401
    """Find and returns the value of the pyproject comment block."""
    comment_block = read_comment_block(script, "pyproject")

    return tomllib.loads(comment_block) if comment_block is not None else comment_block
