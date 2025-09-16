# MacroFuturo — Novel Generator

Generador de novelas 2025–2035 desde un lattice de abundancia × gobernanza × adopción, forks y tecnologías toggables. Mantiene escenas sin infodumps y responde preguntas técnicas mediante un evidence ledger auditable.

## Estructura del repositorio

```
/backend      # FastAPI + pipeline secuencial normalize→plan→diegetics→scenes→style→ledger→package
/frontend     # Next.js + Tailwind Studio para configurar el lattice y lanzar corridas
/contracts    # Schemas JSON/YAML de referencia
/prompts      # Prompts base por job
/presets      # Presets listos (incluye preset Valparaíso)
```

## Backend

- **Stack:** FastAPI 0.110 + PyYAML.
- **Endpoints:**
  - `POST /generate`: ejecuta la pipeline y entrega paths/preview de artefactos (`outline.md`, `novela.md`, diegéticos, `ledger.json`, `run.json`, `export.zip`).
  - `POST /ask-why`: responde preguntas usando `ledger.json` del run.
  - `GET /health`: ping simple.
- **Pipeline runner:** guarda salidas bajo `backend/runs/<run-id>/` y produce `run.json` conforme al contrato.

### Ejecutar localmente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend (Studio)

- **Stack:** Next.js 14 + Tailwind. UI con sliders A/B/C, toggles de forks/tech, sliders P1–P5, inputs ciudad/era/título, botón GENERAR, tabs Outline/Capítulos/Documentos/Ledger/Ask‑Why.
- **Desarrollo:**

```bash
cd frontend
npm install
npm run dev
```

Configura el backend en `http://localhost:8000`. El Studio usa la API para mostrar previews y rutas de exportación.

## Tests

```bash
cd backend
pytest
```

Las pruebas verifican que el preset Valparaíso genera 12 beats, novela ≥2000 palabras, diegéticos completos y que Ask‑Why responde “¿Cómo puede un asistente de voz funcionar offline en 2026?” desde el ledger.

## Preset rápido (Valparaíso)

El archivo `presets/valparaiso.yaml` incluye `scenario.yaml` y `world.yaml` listos para cargar en la UI o enviarlos directo al endpoint `/generate`.
