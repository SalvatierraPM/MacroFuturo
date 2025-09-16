from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..models.api import AskWhyRequest, AskWhyResponse, GenerateRequest, GenerateResponse
from ..services.ask_why import AskWhyService
from ..services.pipeline_runner import pipeline_runner

router = APIRouter()

_repo_root = Path(__file__).resolve().parents[3]
ask_service = AskWhyService(pipeline_runner.base_output_dir)


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, _repo_root)
    except ValueError:
        return path


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    try:
        state = pipeline_runner.run(
            scenario_yaml=request.scenario_yaml,
            world_yaml=request.world_yaml,
            seed=request.seed,
        )
    except Exception as exc:  # pragma: no cover - surfaced in API response
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    diegetic_paths = {
        key: _rel(path) for key, path in state.exported_paths.items() if key in {"memo", "mou", "postmortem"}
    }

    response = GenerateResponse(
        run_id=state.run_id,
        outline_path=_rel(state.exported_paths["outline"]),
        novel_path=_rel(state.exported_paths["novela"]),
        ledger_path=_rel(state.exported_paths["ledger"]),
        world_path=_rel(state.exported_paths["world"]),
        scenario_path=_rel(state.exported_paths["scenario"]),
        diegetic_paths=diegetic_paths,
        run_metadata_path=_rel(state.exported_paths["run"]),
        export_zip_path=_rel(state.exported_paths["export_zip"]),
        outline_preview=state.outline_markdown,
        novel_preview=state.novel_markdown,
        documents_preview=state.diegetic_documents,
        ledger_preview=state.ledger,
    )
    return response


@router.post("/ask-why", response_model=AskWhyResponse)
def ask_why(request: AskWhyRequest) -> AskWhyResponse:
    try:
        answer, citations = ask_service.answer(request.run_id, request.question)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - keep debugging info minimal
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AskWhyResponse(answer=answer, citations=citations)
