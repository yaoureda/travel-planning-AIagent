from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Scenario:
    id: str
    prompt: str
    tags: list[str] = field(default_factory=list)
    must_include_any: list[list[str]] = field(default_factory=list)
    must_not_include: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)
    critical_fields: list[str] = field(default_factory=list)
    expect_clarification: bool = False
    budget_expectation: str = "mention"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Scenario":
        return Scenario(
            id=data["id"],
            prompt=data["prompt"],
            tags=list(data.get("tags", [])),
            must_include_any=[list(group) for group in data.get("must_include_any", [])],
            must_not_include=list(data.get("must_not_include", [])),
            required_fields=list(data.get("required_fields", [])),
            critical_fields=list(data.get("critical_fields", [])),
            expect_clarification=bool(data.get("expect_clarification", False)),
            budget_expectation=data.get("budget_expectation", "mention"),
        )


def load_scenarios(file_path: str | Path) -> list[Scenario]:
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Scenario.from_dict(item) for item in data]
