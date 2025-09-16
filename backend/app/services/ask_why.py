from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple


class AskWhyService:
    def __init__(self, base_output_dir: Path) -> None:
        self.base_output_dir = base_output_dir

    def answer(self, run_id: str, question: str) -> Tuple[str, List[str]]:
        run_dir = self.base_output_dir / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"No se encontró el run_id {run_id}")
        ledger_path = run_dir / "ledger.json"
        if not ledger_path.exists():
            raise FileNotFoundError(f"No se encontró ledger.json para {run_id}")

        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        claims = ledger.get("claims", [])
        if not claims:
            raise ValueError("Ledger sin claims")

        claim = self._select_claim(question, claims)
        answer = self._compose_answer(claim)
        citations = [f"ledger:{claim.get('id', 'sin-id')}", f"run:{run_id}"]
        return answer, citations

    def _select_claim(self, question: str, claims: List[Dict[str, object]]) -> Dict[str, object]:
        normalized_question = _normalize_text(question)
        best_score = -1
        best_claim = claims[0]
        for claim in claims:
            statement = claim.get("statement", "")
            score = _keyword_overlap(normalized_question, _normalize_text(statement))
            if score > best_score:
                best_score = score
                best_claim = claim
        return best_claim

    def _compose_answer(self, claim: Dict[str, object]) -> str:
        confidence = claim.get("confidence")
        steps = claim.get("because", [])
        signals = claim.get("signals", [])
        costs = claim.get("costs", [])
        statement = claim.get("statement", "")

        lines: List[str] = []
        if confidence is not None:
            lines.append(f"**Claim:** {statement} (confianza {confidence:.2f})")
        else:
            lines.append(f"**Claim:** {statement}")
        lines.append("**Pasos causales:**")
        for item in steps:
            step = item.get("step") if isinstance(item, dict) else str(item)
            lines.append(f"- {step}")
        if signals:
            lines.append("**Señales en escena:**")
            for signal in signals:
                lines.append(f"- {signal}")
        if costs:
            lines.append("**Costos y trade-offs:**")
            for cost in costs:
                lines.append(f"- {cost}")
        return "\n".join(lines)


def _normalize_text(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    cleaned = re.sub(r"[^a-z0-9\s]", " ", without_accents.lower())
    tokens = [token for token in cleaned.split() if token]
    return " ".join(tokens)


def _keyword_overlap(text_a: str, text_b: str) -> int:
    set_a = set(text_a.split())
    set_b = set(text_b.split())
    return len(set_a & set_b)
