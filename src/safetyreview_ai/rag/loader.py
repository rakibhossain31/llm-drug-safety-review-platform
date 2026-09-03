from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from safetyreview_ai.core.config import PROJECT_ROOT


@dataclass
class Document:
    source: str
    text: str


def load_guidance_documents(directory: Path | None = None) -> list[Document]:
    base = directory or PROJECT_ROOT / "data" / "pv_guidance"
    return [Document(source=path.name, text=path.read_text(encoding="utf-8")) for path in sorted(base.glob("*.md"))]
