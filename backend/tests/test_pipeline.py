from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from backend.app.services.ask_why import AskWhyService
from backend.app.services.pipeline_runner import PipelineRunner


@pytest.fixture()
def preset_inputs() -> tuple[str, str]:
    preset_path = Path(__file__).resolve().parents[2] / "presets" / "valparaiso.yaml"
    data = yaml.safe_load(preset_path.read_text(encoding="utf-8"))
    return data["scenario"], data["world"]


def _word_count(text: str) -> int:
    return len([token for token in text.replace("\n", " ").split(" ") if token.strip()])


def test_pipeline_generates_core_artifacts(tmp_path, preset_inputs) -> None:
    scenario_yaml, world_yaml = preset_inputs
    runner = PipelineRunner(base_output_dir=tmp_path / "runs")

    state = runner.run(scenario_yaml=scenario_yaml, world_yaml=world_yaml, seed=1234)

    assert len(state.outline_beats) == 12
    assert _word_count(state.novel_markdown) >= 2000
    assert set(state.diegetic_documents.keys()) == {"memo", "mou", "postmortem"}
    assert any("Asistentes de voz offline" in claim["statement"] for claim in state.ledger["claims"])

    # Files exist
    for key in ["outline", "novela", "ledger", "scenario", "world", "run", "export_zip"]:
        path = Path(state.exported_paths[key])
        assert path.exists()

    # Ask-why integration
    service = AskWhyService(runner.base_output_dir)
    answer, citations = service.answer(state.run_id, "¿Cómo puede un asistente de voz funcionar offline en 2026?")
    assert "Pasos causales" in answer
    assert any("VOICE" in citation or "ledger:" in citation for citation in citations)


def test_run_metadata_matches_schema(tmp_path, preset_inputs) -> None:
    scenario_yaml, world_yaml = preset_inputs
    runner = PipelineRunner(base_output_dir=tmp_path / "runs")
    state = runner.run(scenario_yaml=scenario_yaml, world_yaml=world_yaml, seed=2)

    run_path = Path(state.exported_paths["run"])
    run_data = json.loads(run_path.read_text(encoding="utf-8"))

    assert run_data["run_id"] == state.run_id
    assert run_data["seed"] == state.seed
    assert Path(run_data["inputs_ref"]).exists()
    assert Path(run_data["world_ref"]).exists()
    assert "outline" in run_data["outputs"]
