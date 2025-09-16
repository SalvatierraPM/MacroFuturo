from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

from ..pipeline.jobs import (
    build_ledger,
    craft_diegetics,
    normalize_inputs,
    package_export,
    plan_outline,
    stylepass,
    write_chapters,
)
from ..pipeline.state import PipelineState


class PipelineRunner:
    """Coordinates the sequential generation pipeline."""

    def __init__(self, base_output_dir: Optional[Path] = None) -> None:
        self.base_output_dir = Path(base_output_dir or Path(__file__).resolve().parents[2] / "runs")
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, scenario_yaml: str, world_yaml: str, seed: Optional[int] = None) -> PipelineState:
        scenario = yaml.safe_load(scenario_yaml) or {}
        world = yaml.safe_load(world_yaml) or {}
        actual_seed = int(seed) if seed is not None else random.randint(1, 1_000_000_000)
        rng = random.Random(actual_seed)
        run_id = self._build_run_id(rng)
        output_dir = self.base_output_dir / run_id
        output_dir.mkdir(parents=True, exist_ok=True)

        state = PipelineState(
            scenario=scenario,
            world=world,
            scenario_yaml=scenario_yaml,
            world_yaml=world_yaml,
            seed=actual_seed,
            rng=rng,
            run_id=run_id,
            output_dir=output_dir,
        )

        normalize_inputs(state)
        plan_outline(state)
        craft_diegetics(state)
        write_chapters(state)
        stylepass(state)
        build_ledger(state)
        package_export(state)

        return state

    def _build_run_id(self, rng: random.Random) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        suffix = "".join(rng.choice(string.ascii_lowercase + string.digits) for _ in range(4))
        return f"run-{timestamp}-{suffix}"


pipeline_runner = PipelineRunner()
