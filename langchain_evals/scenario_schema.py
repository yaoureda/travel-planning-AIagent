"""Minimal scenario schema for local LangChain evals."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Scenario:
    """Single benchmark scenario configuration.

    The fields are used to evaluate the trajectory and responses.
    """

    id: str
    prompt: str
    expected_tools: list[str] = field(default_factory=list)
    expect_clarification: bool = False
    budget_expectation: str = ""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Scenario":
        return Scenario(
            id=data["id"],
            prompt=data["prompt"],
            expected_tools=list(data.get("expected_tools", [])),
            expect_clarification=data.get("expect_clarification", False),
            budget_expectation=data.get("budget_expectation", "")
        )


def load_scenarios(file_path: str | Path) -> list[Scenario]:
    """Load scenarios from a JSON file into ``Scenario`` objects."""

    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Scenario.from_dict(item) for item in data]
