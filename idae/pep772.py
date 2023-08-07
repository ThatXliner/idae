"""Slightly modified code from the example in PEP 772."""
import tokenize
from typing import Generator

DEPENDENCY_BLOCK_MARKER = "Script Dependencies:"


def read_dependency_block(filename: str) -> Generator[str]:
    """Read PEP 772 dependency block."""
    # ruff: noqa: PLW2901
    # Use the tokenize module to handle any encoding declaration.
    with tokenize.open(filename) as f:
        for line in f:
            if line.startswith("##"):
                line = line[2:].strip()
                if line == DEPENDENCY_BLOCK_MARKER:
                    for line in f:
                        if not line.startswith("##"):
                            break
                        line = line[2:].strip()
                        if not line:
                            continue
                        # Try to convert to a requirement. This will raise
                        # an error if the line is not a PEP 508 requirement
                        yield line
                    break
