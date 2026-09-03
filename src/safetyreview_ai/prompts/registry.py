from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from safetyreview_ai.core.config import PROJECT_ROOT

PROMPT_ROOT = PROJECT_ROOT / "src" / "safetyreview_ai" / "prompts" / "literature"


@dataclass(frozen=True)
class PromptTemplate:
    id: str
    name: str
    strategy: str
    system: str
    user_template: str

    def render(self, abstract: str) -> tuple[str, str]:
        return self.system, self.user_template.format(abstract=abstract)


class PromptRegistry:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or PROMPT_ROOT
        self._prompts = self._load()

    def _load(self) -> dict[str, PromptTemplate]:
        prompts: dict[str, PromptTemplate] = {}
        for path in sorted(self.root.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            prompt = PromptTemplate(**raw)
            prompts[prompt.id] = prompt
        if not prompts:
            raise RuntimeError(f"No prompt templates found in {self.root}")
        return prompts

    def get(self, prompt_id: str) -> PromptTemplate:
        if prompt_id not in self._prompts:
            available = ", ".join(sorted(self._prompts))
            raise KeyError(f"Unknown prompt_id '{prompt_id}'. Available: {available}")
        return self._prompts[prompt_id]

    def list(self) -> list[PromptTemplate]:
        return list(self._prompts.values())
