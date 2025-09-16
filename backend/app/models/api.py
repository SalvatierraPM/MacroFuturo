from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    scenario_yaml: str = Field(..., description="YAML string describing the scenario inputs")
    world_yaml: str = Field(..., description="YAML string describing the world context")
    seed: Optional[int] = Field(None, description="Optional deterministic seed")


class GenerateResponse(BaseModel):
    run_id: str
    outline_path: str
    novel_path: str
    ledger_path: str
    world_path: str
    scenario_path: str
    diegetic_paths: Optional[Dict[str, str]] = None
    run_metadata_path: Optional[str] = None
    export_zip_path: Optional[str] = None
    outline_preview: Optional[str] = None
    novel_preview: Optional[str] = None
    documents_preview: Optional[Dict[str, str]] = None
    ledger_preview: Optional[Dict[str, Any]] = None


class AskWhyRequest(BaseModel):
    run_id: str
    question: str


class AskWhyResponse(BaseModel):
    answer: str
    citations: List[str] = Field(default_factory=list)
