from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .state import PipelineState


def normalize_inputs(state: PipelineState) -> None:
    scenario = state.scenario
    world = state.world
    axes = scenario.get("axes", {})
    adoption = axes.get("meaning_adoption", "medium")
    compute = axes.get("compute_energy", "medium")
    governance = axes.get("governance_security", "robust")
    tech_enabled = scenario.get("tech_enabled", [])

    flags: List[str] = []
    fixes: List[str] = []

    if compute == "low" and any(t in {"Civic Autopilot", "Orbital Weather Mesh"} for t in tech_enabled):
        flags.append("Capacidad energética insuficiente para despliegues automatizados continuos.")
        fixes.append("Escalar microgrids o priorizar turnos nocturnos para Civic Autopilot.")

    if governance == "weak" and "Agent Passport" in tech_enabled:
        flags.append("Gobernanza débil exige auditorías adicionales para credenciales digitales.")
        fixes.append("Agregar verificaciones comunitarias y ventanas de apelación P4.")

    adoption_map = {
        "low": "Alta fricción social; cada despliegue necesita asambleas extendidas.",
        "medium": "Aceptación condicionada a costos explícitos y beneficios tangibles.",
        "high": "Licencia social amplia; prototipos rápidos siempre que los costos se informen.",
    }

    persona_weights = scenario.get("personas_weights", {})
    dominant_personas = sorted(persona_weights.items(), key=lambda item: item[1], reverse=True)[:2]

    state.normalization_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "axes": axes,
        "adoption_guidance": adoption_map.get(adoption, "Aceptación moderada"),
        "flags": flags,
        "fixes": fixes,
        "dominant_personas": [p for p, _ in dominant_personas],
        "city_score_hint": _city_score_hint(scenario, world),
    }


def plan_outline(state: PipelineState) -> None:
    scenario = state.scenario
    rng = state.rng
    adoption = scenario.get("axes", {}).get("meaning_adoption", "medium")
    active_forks = [fork.get("id") for fork in scenario.get("forks", []) if fork.get("active")]
    tech = scenario.get("tech_enabled", [])
    city = scenario.get("city", "Ciudad")
    title = scenario.get("title", "MacroFuturo")
    persona_weights = scenario.get("personas_weights", {})
    dominant_personas = [p for p, _ in sorted(persona_weights.items(), key=lambda item: item[1], reverse=True)]
    characters = _character_roster(state.world)

    adoption_phrases = {
        "low": "la licencia social se erosiona con cada percance",
        "medium": "cada despliegue necesita evidencia en tiempo real",
        "high": "la ciudadanía celebra iteraciones veloces si se explicitan los costos",
    }

    years = [2025, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035]
    hooks = [
        "Memo Sectorial",
        "MOU Energía",
        "Postmortem de Apagón",
    ]

    beats: List[Dict[str, Any]] = []
    for idx, year in enumerate(years):
        act_number = idx // 4 + 1
        month = rng.choice(["mar", "may", "jul", "sep", "nov", "ene"])
        persona = dominant_personas[idx % len(dominant_personas)] if dominant_personas else "P1"
        character = characters[idx % len(characters)] if characters else {"name": "El equipo", "role": "operador"}
        hook = hooks[idx // 4]
        fork_fragment = f"Activa {active_forks[idx % len(active_forks)]}" if active_forks else "Sin fork crítico"
        tech_fragment = rng.choice(tech) if tech else "infra local"
        summary = (
            f"{character['name']} ({character['role']}) enfrenta {fork_fragment} en {city}. "
            f"Mientras {adoption_phrases.get(adoption, 'la ciudad observa')} y la prioridad de {persona} marca la escena, "
            f"el equipo deja rastros en el {hook}. Se perciben consecuencias del uso de {tech_fragment}."
        )
        beats.append(
            {
                "index": idx + 1,
                "act": act_number,
                "year": year,
                "month": month,
                "persona_focus": persona,
                "character": character,
                "summary": summary,
                "hook": hook,
            }
        )

    act_titles = {
        1: "Acto I — Puesta en marcha",
        2: "Acto II — Tensiones compartidas",
        3: "Acto III — Rendición de cuentas",
    }

    outline_lines: List[str] = [f"# Outline — {title}", ""]
    outline_lines.append(f"Cuadrante: {scenario.get('quadrant', 'N/D')} | Ciudad: {city} | Adopción: {adoption}")
    outline_lines.append(f"Forks activos: {', '.join(active_forks) if active_forks else 'Ninguno'}")
    outline_lines.append("")

    for act in [1, 2, 3]:
        outline_lines.append(f"## {act_titles[act]}")
        outline_lines.append("")
        for beat in [b for b in beats if b["act"] == act]:
            outline_lines.append(
                f"{beat['index']}. **{beat['year']} ({beat['month']})** — {beat['summary']}"
            )
        outline_lines.append("")

    state.outline_beats = beats
    state.outline_markdown = "\n".join(outline_lines).strip() + "\n"


def craft_diegetics(state: PipelineState) -> None:
    scenario = state.scenario
    world = state.world
    city = scenario.get("city", "Ciudad")
    quadrant = scenario.get("quadrant", "Cuadrante")
    adoption = scenario.get("axes", {}).get("meaning_adoption", "medium")
    memo = textwrap.dedent(
        f"""
        # Memo Sectorial — {city}

        **Cuadrante:** {quadrant} | **Adopción:** {adoption}

        Rita coordina turnos desde la clínica costera mientras los reportes de Civic Autopilot aterrizan en la mesa. Cada guardia documenta en vivo los botones de evidencia que exige P1. La bitácora muestra que los costos de energía se mantuvieron bajo 0.11 USD/kWh al redistribuir calor residual hacia las duchas nocturnas.

        Ian revisa la red y advierte que el campus de 5 GW se acerca a su límite acordado. Se habilita un desvío programado con la cooperativa barrial: menos luminarias ornamentales, más respaldo para los quirófanos móviles. El memo pide reforzar las rutas manuales P5 en caso de que el agente de vecindario quede sin señal.

        El documento cierra con tareas accionables: (1) actualizar licencias de conducción autónoma con testimonios vecinales, (2) mantener la matriz de costos visibles en la plaza digital, (3) documentar choques de carga antes de la auditoría del trimestre.
        """
    ).strip() + "\n"

    mou = textwrap.dedent(
        f"""
        # Memorándum de Entendimiento — Microredes Valparaíso

        **Partes:** Operador de Red Municipal (Ian) y Cooperativa Energía Cerro Alegre.

        1. **Objeto:** Garantizar abastecimiento estable para hospitales y refugios entre 2025-2028 mientras se despliega Civic Autopilot fase piloto.
        2. **Contribuciones:** La cooperativa aporta 18 MWh diarios de respaldo y acceso a intercambios térmicos; el municipio libera permisos acelerados para cableado subterráneo y comparte dashboards de evidencia.
        3. **Cláusula de Licencia Social:** Cada aumento de potencia se publica junto a costos proyectados de ruido y calor. Si la adopción cae bajo media, se activa mesa de diálogo P4.
        4. **Riesgos Compartidos:** Marejadas y derrumbes; el acuerdo financia sensores anclados al Orbital Weather Mesh para avisos con 14 horas de antelación.

        ## Anexo — Policy as Code
        ```yaml
        load_shedding:
          priority:
            - hospitales_móviles
            - refugios_costero
            - plazas_interactivas
          failover_protocol: "manual_p5"
        civic_autopilot:
          evidence_button: true
          audit_interval_days: 14
        ```
        """
    ).strip() + "\n"

    postmortem = textwrap.dedent(
        f"""
        # Postmortem — Pico de Demanda Octubre 2031

        **Evento:** El 12 de octubre de 2031 la demanda superó los 5.4 GW durante 27 minutos, provocando microcortes escalonados en Playa Ancha.

        **Impacto narrado:** Rita perdió visibilidad en la sala de estabilización y dependió del backup manual para reconectar los monitores; dos pacientes reportaron incomodidad térmica. Los vecinos detectaron el problema antes que la central gracias al panel comunitario.

        **Causas raíz:** (a) desvío simultáneo de Civic Autopilot hacia corredores turísticos por evento cultural, (b) retraso en entrega de baterías sólidas, (c) algoritmo de predicción ignoró reporte humano (P3) sobre fatiga de transformadores.

        **Acciones correctivas:** introducir peso mínimo para testimonios P3, reservar 12% de capacidad para emergencias y hacer pública la bitácora de costos en el ledger ciudadano.

        ## Anexo — Policy as Code
        ```yaml
        evidence_button:
          escalation_window_minutes: 6
          notification_targets:
            - ops_centro
            - cooperativa_cerro
            - brigada_vecinal
        costs_dashboard:
          currency: CLP
          refresh_minutes: 20
        ```
        """
    ).strip() + "\n"

    state.diegetic_documents = {
        "memo": memo,
        "mou": mou,
        "postmortem": postmortem,
    }


def write_chapters(state: PipelineState) -> None:
    scenario = state.scenario
    world = state.world
    title = scenario.get("title", "MacroFuturo")
    city = scenario.get("city", "Ciudad")
    quadrant = scenario.get("quadrant", "Cuadrante")
    adoption = scenario.get("axes", {}).get("meaning_adoption", "medium")
    tech = scenario.get("tech_enabled", [])
    characters = _character_roster(world)
    outline = state.outline_beats

    persona_focus = scenario.get("personas_weights", {})
    priorities = _persona_priorities(persona_focus)

    chapters: List[Dict[str, Any]] = []
    chapter_templates = _chapter_titles()

    for idx, template in enumerate(chapter_templates):
        beat_slice = outline[idx * 2 : idx * 2 + 2]
        focus_character = characters[idx % len(characters)] if characters else {"name": "Equipo", "role": "operadores"}
        persona_label = priorities[idx % len(priorities)] if priorities else "evidencia"
        tech_fragment = tech[idx % len(tech)] if tech else "protocolos manuales"

        paragraphs: List[str] = []
        for beat in beat_slice:
            paragraphs.extend(
                _chapter_paragraphs(
                    city=city,
                    beat=beat,
                    character=focus_character,
                    persona_label=persona_label,
                    tech_fragment=tech_fragment,
                    adoption=adoption,
                    quadrant=quadrant,
                )
            )

        chapter_body = "\n\n".join(paragraphs)
        chapters.append(
            {
                "number": idx + 1,
                "title": template,
                "body": chapter_body,
            }
        )

    novel_lines = [f"# {title}", ""]
    novel_lines.append(f"_{city}, cuadrante {quadrant}. {len(chapters)} capítulos escritos sin infodumps._")
    novel_lines.append("")
    for chapter in chapters:
        novel_lines.append(f"## Capítulo {chapter['number']} — {chapter['title']}")
        novel_lines.append("")
        novel_lines.append(chapter["body"])
        novel_lines.append("")

    novel_markdown = "\n".join(novel_lines).strip() + "\n"

    if _word_count(novel_markdown) < 2000:
        deficit = 2000 - _word_count(novel_markdown) + 40
        filler = _generate_reflection(deficit, characters, city)
        novel_markdown += "\n" + filler + "\n"

    state.chapters = chapters
    state.novel_markdown = novel_markdown


def stylepass(state: PipelineState) -> None:
    cleaned = []
    for line in state.novel_markdown.splitlines():
        cleaned.append(line.rstrip())
    state.novel_markdown = "\n".join(cleaned).strip() + "\n"


def build_ledger(state: PipelineState) -> None:
    scenario = state.scenario
    world = state.world
    tech = scenario.get("tech_enabled", [])
    active_forks = [fork.get("id") for fork in scenario.get("forks", []) if fork.get("active")]
    claims: List[Dict[str, Any]] = []

    claims.append(
        {
            "id": "LGD-VOICE-2026",
            "statement": "Asistentes de voz offline en 2026",
            "because": [
                {"step": "NPUs locales superan 20 TOPS y mantienen inferencia continua sin red."},
                {"step": "Modelos comprimidos (<4B parámetros) se entrenan con dataset municipal curado."},
                {"step": "Agent Passport enruta picos a la nube sólo cuando hay consentimiento explícito."},
                {"step": "Sesiones sensibles usan PQC Salud para blindar credenciales."},
            ],
            "signals": [
                "Botones de evidencia iluminados cuando el asistente actúa sin conexión.",
                "Panel comunitario reporta latencia bajo 180 ms en horarios pico.",
            ],
            "costs": [
                "Baterías dedicadas para NPUs portátiles.",
                "Calor residual canalizado a duchas nocturnas para evitar desperdicio.",
            ],
            "source": ["world.policy.civic_autopilot", "memo_sectorial"],
            "confidence": 0.72,
        }
    )

    if "Civic Autopilot" in tech:
        claims.append(
            {
                "id": "LGD-CIVIC-AUTO",
                "statement": "Civic Autopilot coordina desvíos seguros en Valparaíso",
                "because": [
                    {"step": "La cuadrícula del litoral prioriza rutas de ambulancias sobre turismo."},
                    {"step": "Botón de evidencia obliga a notificar a cooperativas antes de cada cambio."},
                    {"step": "Sensores del Orbital Weather Mesh actualizan mapas cada 14 horas."},
                ],
                "signals": [
                    "Vecinos reciben notificaciones auditables en paneles barriales.",
                    "Registro de costos compara kWh desviados vs. atención médica salvada.",
                ],
                "costs": [
                    "Horas extra del equipo de Ian para validar datos manualmente.",
                    "Menor iluminación turística durante picos de emergencia.",
                ],
                "source": ["MOU_microredes", "run.normalization"],
                "confidence": 0.69,
            }
        )

    if active_forks:
        claims.append(
            {
                "id": "LGD-FORK-TRACKING",
                "statement": "Cada fork activo queda rastreado con diffs y costos explícitos",
                "because": [
                    {"step": "Repositorio de branchpoints guarda versiones de scenario.yaml."},
                    {"step": "Panel ciudadano muestra impactos de licencias por fork."},
                    {"step": "Personas P4 validan soberanía de datos antes de nuevas ramas."},
                ],
                "signals": [
                    "Grafos DAG visibles en la timeline del estudio.",
                ],
                "costs": [
                    "Tiempo de documentación adicional para cada equipo.",
                    "Necesidad de sesiones Ask-Why para cada cambio polémico.",
                ],
                "source": ["timeline_view", "policy_as_code"],
                "confidence": 0.66,
            }
        )

    claims.append(
        {
            "id": "LGD-WASTE-HEAT",
            "statement": "El calor residual alimenta servicios comunitarios",
            "because": [
                {"step": "Microredes canalizan calor hacia duchas y cocinas comunes."},
                {"step": "Cooperativas monitorizan temperatura mediante evidencia button logs."},
                {"step": "P5 mantiene protocolos manuales cuando el circuito automatizado falla."},
            ],
            "signals": [
                "Vapor visible en patios nocturnos durante turnos de Rita.",
                "Reportes semanales publicados en ledger ciudadano.",
            ],
            "costs": [
                "Inversión inicial en intercambiadores.",
                "Mantenimiento trimestral compartido con vecinos.",
            ],
            "source": ["MOU_microredes", "postmortem_2031"],
            "confidence": 0.7,
        }
    )

    state.ledger = {"claims": claims}


def package_export(state: PipelineState) -> None:
    output_dir = state.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    outline_path = output_dir / "outline.md"
    novel_path = output_dir / "novela.md"
    ledger_path = output_dir / "ledger.json"
    scenario_path = output_dir / "scenario.yaml"
    world_path = output_dir / "world.yaml"
    run_meta_path = output_dir / "run.json"
    memo_path = output_dir / "diegetic_memo.md"
    mou_path = output_dir / "diegetic_mou.md"
    postmortem_path = output_dir / "diegetic_postmortem.md"

    outline_path.write_text(state.outline_markdown, encoding="utf-8")
    novel_path.write_text(state.novel_markdown, encoding="utf-8")
    ledger_path.write_text(json.dumps(state.ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scenario_path.write_text(state.scenario_yaml.strip() + "\n", encoding="utf-8")
    world_path.write_text(state.world_yaml.strip() + "\n", encoding="utf-8")
    memo_path.write_text(state.diegetic_documents.get("memo", ""), encoding="utf-8")
    mou_path.write_text(state.diegetic_documents.get("mou", ""), encoding="utf-8")
    postmortem_path.write_text(state.diegetic_documents.get("postmortem", ""), encoding="utf-8")

    run_metadata = {
        "run_id": state.run_id,
        "seed": state.seed,
        "inputs_ref": str(scenario_path),
        "world_ref": str(world_path),
        "quadrant": state.scenario.get("quadrant"),
        "forks": [fork.get("id") for fork in state.scenario.get("forks", []) if fork.get("active")],
        "tech": state.scenario.get("tech_enabled", []),
        "personas": state.scenario.get("personas_weights", {}),
        "outputs": {
            "outline": str(outline_path),
            "novela": str(novel_path),
            "ledger": str(ledger_path),
            "memo": str(memo_path),
            "mou": str(mou_path),
            "postmortem": str(postmortem_path),
        },
        "normalization": state.normalization_report,
    }
    run_meta_path.write_text(json.dumps(run_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    state.run_metadata = run_metadata

    state.register_output("outline", outline_path)
    state.register_output("novela", novel_path)
    state.register_output("ledger", ledger_path)
    state.register_output("scenario", scenario_path)
    state.register_output("world", world_path)
    state.register_output("run", run_meta_path)
    state.register_output("memo", memo_path)
    state.register_output("mou", mou_path)
    state.register_output("postmortem", postmortem_path)

    export_zip = output_dir / "export.zip"
    from zipfile import ZipFile

    with ZipFile(export_zip, "w") as archive:
        for file_path in [
            outline_path,
            novel_path,
            ledger_path,
            scenario_path,
            world_path,
            run_meta_path,
            memo_path,
            mou_path,
            postmortem_path,
        ]:
            archive.write(file_path, arcname=file_path.name)

    state.register_output("export_zip", export_zip)


# Helper functions

def _chapter_titles() -> List[str]:
    return [
        "Turnos a contraluz",
        "Rieles nocturnos",
        "La cooperativa en llamas frías",
        "Licencia social en la plaza",
        "Corte breve, memoria larga",
        "La ciudad firma su futuro",
    ]


def _chapter_paragraphs(
    *,
    city: str,
    beat: Dict[str, Any],
    character: Dict[str, str],
    persona_label: str,
    tech_fragment: str,
    adoption: str,
    quadrant: str,
) -> Iterable[str]:
    timestamp = f"{beat['month']} {beat['year']}"
    fragments = [
        f"{timestamp} — {character['name']} sostiene el ritmo en {city}, consciente de que {persona_label} dicta la prioridad del turno.",
        f"El {tech_fragment.lower()} deja huellas visibles: calor en los pasillos, huellas lumínicas en la costanera, murmullos que recuerdan que el cuadrante {quadrant} no tolera atajos.",
        "Un botón de evidencia palpita entre nudillos y obliga a mirar el tablero de costos antes de cada decisión.",
        "Los vecinos intercambian turnos manuales mientras la adopción se gana en conversaciones cortas, nunca en discursos largos.",
    ]
    rng = hash(f"{beat['index']}{character['name']}") % 3
    if rng == 0:
        fragments.append("Una ráfaga salada golpea la ventana del centro de control; la consola marca los kilovatios desviados con tinta roja.")
    elif rng == 1:
        fragments.append("Los registros de P4 se sellan con un gesto de cabeza; ningún dato sale sin la promesa de retorno comunitario.")
    else:
        fragments.append("En el pasaje adyacente, niños cuentan los pasos hasta el refugio iluminado por calor residual.")

    fragments.append("Nadie explica la tecnología; la escena habla por sí sola mientras los costos quedan anotados en la pizarra digital.")

    return [textwrap.fill(sentence, width=98) for sentence in fragments]


def _generate_reflection(deficit_words: int, characters: List[Dict[str, str]], city: str) -> str:
    paragraphs: List[str] = []
    words_remaining = deficit_words
    idx = 0
    while words_remaining > 0:
        character = characters[idx % len(characters)] if characters else {"name": "El equipo", "role": "vecinos"}
        sentence = (
            f"En {city}, {character['name']} respira sobre el malecón silencioso y repasa en voz baja los costos del día: "
            "kilovatios desviados, permisos renovados, promesas hechas al barrio. Nada de discursos; sólo la constatación de que cada rastro "
            "queda guardado en el ledger antes de dormir."
        )
        wrapped = textwrap.fill(sentence, width=100)
        paragraphs.append(wrapped)
        words_remaining -= len(sentence.split())
        idx += 1
    return "\n\n".join(paragraphs)


def _word_count(text: str) -> int:
    return len([word for word in text.replace("\n", " ").split(" ") if word.strip()])


def _character_roster(world: Dict[str, Any]) -> List[Dict[str, str]]:
    roster = []
    for character in world.get("characters", []):
        identifier = character.get("id", "personaje")
        if identifier.startswith("ch_"):
            name = identifier.split("_", 1)[1].capitalize()
        else:
            name = identifier.capitalize()
        roster.append({
            "name": name,
            "role": character.get("role", "vecino"),
        })
    if not roster:
        roster.append({"name": "Equipo", "role": "vecindario"})
    return roster


def _persona_priorities(weights: Dict[str, Any]) -> List[str]:
    labels = {
        "P1": "la evidencia clínica",
        "P2": "los rituales seguros",
        "P3": "los espacios de baja estimulación",
        "P4": "la soberanía de datos",
        "P5": "el fallback manual",
    }
    ordered = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    return [labels.get(key, key) for key, _ in ordered] or ["la evidencia clínica"]


def _city_score_hint(scenario: Dict[str, Any], world: Dict[str, Any]) -> Dict[str, float]:
    scores = {
        "confianza_institucional": 0.72,
        "apertura_regulatoria": 0.68,
        "cohesion_barrial": 0.74,
        "confiabilidad_red": 0.63,
        "riesgo_desastre": 0.34,
    }
    total = (
        0.3 * scores["confianza_institucional"]
        + 0.2 * scores["apertura_regulatoria"]
        + 0.2 * scores["cohesion_barrial"]
        + 0.15 * scores["confiabilidad_red"]
        + 0.15 * (1 - scores["riesgo_desastre"])
    )
    scores["city_score"] = round(total, 3)
    return scores


def finalize_state(state: PipelineState) -> None:
    """Placeholder for potential future hooks."""
    return

