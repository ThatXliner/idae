"""Dependency utils lifted from Hatch."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from packaging.requirements import Requirement


def _normalize_project_name(project_name: str) -> str:
    # https://peps.python.org/pep-0503/#normalized-names
    return re.sub(r"[-_.]+", "-", project_name).lower()


def _get_normalized_dependency(requirement: Requirement) -> str:
    # Changes to this function affect reproducibility between versions
    from packaging.specifiers import SpecifierSet

    requirement.name = _normalize_project_name(requirement.name)

    if requirement.specifier:
        requirement.specifier = SpecifierSet(str(requirement.specifier).lower())

    if requirement.extras:
        requirement.extras = {
            _normalize_project_name(extra) for extra in requirement.extras
        }

    # All TOML writers use double quotes,
    # so allow direct writing or copy/pasting to avoid escaping
    return str(requirement).replace('"', "'")


def get_normalized_dependencies(requirements: list[Requirement]) -> list[str]:
    """Get normalized dependencies."""
    normalized_dependencies = {
        _get_normalized_dependency(requirement) for requirement in requirements
    }
    return sorted(normalized_dependencies)


def hash_dependencies(requirements: list[Requirement]) -> str:
    """Create a hash of the dependencies."""
    from hashlib import sha256

    data = "".join(
        sorted(
            # Internal spacing is ignored by PEP 440
            normalized_dependency.replace(" ", "")
            for normalized_dependency in {
                _get_normalized_dependency(req) for req in requirements
            }
        ),
    ).encode("utf-8")

    return sha256(data).hexdigest()
