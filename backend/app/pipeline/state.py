from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from random import Random
from typing import Any, Dict, List


@dataclass
class PipelineState:
    scenario: Dict[str, Any]
    world: Dict[str, Any]
    scenario_yaml: str
    world_yaml: str
    seed: int
    rng: Random
    run_id: str
    output_dir: Path
    normalization_report: Dict[str, Any] = field(default_factory=dict)
    outline_beats: List[Dict[str, Any]] = field(default_factory=list)
    outline_markdown: str = ""
    diegetic_documents: Dict[str, str] = field(default_factory=dict)
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    novel_markdown: str = ""
    ledger: Dict[str, Any] = field(default_factory=lambda: {"claims": []})
    run_metadata: Dict[str, Any] = field(default_factory=dict)
    exported_paths: Dict[str, str] = field(default_factory=dict)

    def register_output(self, name: str, path: Path) -> None:
        self.exported_paths[name] = str(path)
