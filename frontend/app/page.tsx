"use client";

import { useMemo, useState } from "react";
import clsx from "clsx";

const computeOptions = [
  { label: "Alta", value: "high" },
  { label: "Baja", value: "low" }
];

const governanceOptions = [
  { label: "Robusta", value: "robust" },
  { label: "Débil", value: "weak" }
];

const adoptionOptions = [
  { label: "Baja", value: "low" },
  { label: "Media", value: "medium" },
  { label: "Alta", value: "high" }
];

const forkOptions = [
  { id: "F-1M-50x", description: "≥1M agentes @ 50×" },
  { id: "F-WSL5", description: "Fuga de pesos → WSL5" },
  { id: "F-5GW", description: "Campus >5 GW" }
];

const techOptions = [
  "Civic Autopilot",
  "Agent Passport",
  "PQC Salud",
  "Orbital Weather Mesh",
  "BioLab-in-a-Box"
];

const personaLabels: Record<string, string> = {
  P1: "Evidencia",
  P2: "Ritual seguro",
  P3: "Low-stim",
  P4: "Soberanía de datos",
  P5: "Fallback manual"
};

type GenerateResponse = {
  run_id: string;
  outline_path: string;
  novel_path: string;
  ledger_path: string;
  world_path: string;
  scenario_path: string;
  diegetic_paths?: Record<string, string>;
  run_metadata_path?: string;
  export_zip_path?: string;
  outline_preview?: string;
  novel_preview?: string;
  documents_preview?: Record<string, string>;
  ledger_preview?: { claims: Array<Record<string, any>> };
};

type AskWhyResponse = {
  answer: string;
  citations: string[];
};

const tabs = ["Outline", "Capítulos", "Documentos", "Ledger", "Ask-Why"] as const;

type TabKey = (typeof tabs)[number];

export default function StudioPage() {
  const [title, setTitle] = useState("MacroFuturo — Tomo I: Rieles Estables");
  const [city, setCity] = useState("Valparaíso");
  const [era, setEra] = useState("2025–2035");
  const [axes, setAxes] = useState({
    compute_energy: "high",
    governance_security: "robust",
    meaning_adoption: "medium"
  });
  const [activeForks, setActiveForks] = useState<Record<string, boolean>>({
    "F-1M-50x": true,
    "F-5GW": true,
    "F-WSL5": false
  });
  const [techEnabled, setTechEnabled] = useState<Record<string, boolean>>({
    "Civic Autopilot": true,
    "Agent Passport": true,
    "PQC Salud": true,
    "Orbital Weather Mesh": false,
    "BioLab-in-a-Box": false
  });
  const [personas, setPersonas] = useState<Record<string, number>>({
    P1: 70,
    P2: 40,
    P3: 50,
    P4: 65,
    P5: 45
  });
  const [tutorialOpen, setTutorialOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<TabKey>("Outline");
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [askWhyQuestion, setAskWhyQuestion] = useState("¿Cómo puede un asistente de voz funcionar offline en 2026?");
  const [askWhyAnswer, setAskWhyAnswer] = useState<AskWhyResponse | null>(null);
  const [askWhyError, setAskWhyError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const forksList = useMemo(
    () =>
      forkOptions.map((fork) => ({
        ...fork,
        active: Boolean(activeForks[fork.id])
      })),
    [activeForks]
  );

  const techList = useMemo(
    () =>
      techOptions.map((tech) => ({
        name: tech,
        active: Boolean(techEnabled[tech])
      })),
    [techEnabled]
  );

  async function handleGenerate() {
    setIsGenerating(true);
    setStatusMessage("Normalizando insumos…");
    setAskWhyAnswer(null);
    setAskWhyError(null);

    const scenario = {
      id: `S-${city.slice(0, 3).toUpperCase()}-${era}`,
      axes,
      quadrant: quadrantFromAxes(axes),
      forks: forksList.map((fork) => ({ id: fork.id, active: fork.active })),
      tech_enabled: techList.filter((item) => item.active).map((item) => item.name),
      personas_weights: personas,
      city,
      era,
      title
    };

    const world = {
      world_id: `W-${city.replace(/\s+/g, "")}-${era}`,
      nodes: ["P", "H", "V", "E", "C", "O"],
      stack: {
        identity: ["Agent Passport", "PQC-ready"],
        data_fabric: ["evidence_trails", "ledgers"]
      },
      policy: {
        civic_autopilot: { status: "pilot_v2", city },
        energy: { microgrids: true, waste_heat: "district_heating" }
      },
      characters: [
        { id: "ch_rita", role: "paramédica", drives: ["cuidado", "competencia"], constraints: ["turnos nocturnos"] },
        { id: "ch_ian", role: "operador de red", drives: ["continuidad"], constraints: ["licencia social"] }
      ]
    };

    const payload = {
      scenario_yaml: toYaml(scenario),
      world_yaml: toYaml(world)
    };

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail?.detail ?? "Error desconocido en generación");
      }

      setStatusMessage("Planificando outline…");
      const data = (await response.json()) as GenerateResponse;
      setResult(data);
      setStatusMessage("Generación completa. Puedes explorar los resultados.");
    } catch (error) {
      console.error(error);
      setStatusMessage(error instanceof Error ? error.message : "Fallo inesperado");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleAskWhy() {
    if (!result) return;
    try {
      const response = await fetch("http://localhost:8000/ask-why", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: result.run_id, question: askWhyQuestion })
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail?.detail ?? "Error en Ask-Why");
      }
      const data = (await response.json()) as AskWhyResponse;
      setAskWhyAnswer(data);
      setAskWhyError(null);
    } catch (error) {
      setAskWhyError(error instanceof Error ? error.message : "Fallo inesperado");
      setAskWhyAnswer(null);
    }
  }

  return (
    <main className="space-y-8">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-lg backdrop-blur">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">MacroFuturo Studio</h1>
            <p className="mt-2 max-w-2xl text-sm text-white/70">
              Configura el lattice (abundancia × gobernanza × adopción), habilita forks y tecnologías, pesa las personas P1–P5 y
              genera novelas sin infodumps. Cada corrida produce outline, novela, diegéticos y un evidence ledger para Ask-Why.
            </p>
          </div>
          <button
            className="rounded-full border border-primary px-4 py-2 text-sm text-primary hover:bg-primary/20"
            onClick={() => setTutorialOpen((prev) => !prev)}
          >
            {tutorialOpen ? "Ocultar tutorial" : "Ver tutorial"}
          </button>
        </div>
        {tutorialOpen && <TutorialBlock />}
      </header>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 rounded-3xl border border-white/10 bg-white/5 p-6">
          <h2 className="text-lg font-semibold">Ajustes narrativos</h2>
          <label className="block text-sm">
            Título
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="mt-1 w-full rounded-lg bg-black/40 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </label>
          <div className="grid grid-cols-2 gap-4">
            <label className="text-sm">
              Ciudad
              <input
                value={city}
                onChange={(event) => setCity(event.target.value)}
                className="mt-1 w-full rounded-lg bg-black/40 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </label>
            <label className="text-sm">
              Era
              <input
                value={era}
                onChange={(event) => setEra(event.target.value)}
                className="mt-1 w-full rounded-lg bg-black/40 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </label>
          </div>

          <AxisSelector
            label="Compute / Energía"
            options={computeOptions}
            selected={axes.compute_energy}
            onChange={(value) => setAxes((prev) => ({ ...prev, compute_energy: value }))}
          />
          <AxisSelector
            label="Gobernanza / Seguridad"
            options={governanceOptions}
            selected={axes.governance_security}
            onChange={(value) => setAxes((prev) => ({ ...prev, governance_security: value }))}
          />
          <AxisSelector
            label="Adopción / Legitimidad"
            options={adoptionOptions}
            selected={axes.meaning_adoption}
            onChange={(value) => setAxes((prev) => ({ ...prev, meaning_adoption: value }))}
          />
        </div>

        <div className="space-y-6 rounded-3xl border border-white/10 bg-white/5 p-6">
          <h2 className="text-lg font-semibold">Forks y tecnologías</h2>
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-white/80">Forks</h3>
            {forksList.map((fork) => (
              <ToggleRow
                key={fork.id}
                label={`${fork.id} — ${fork.description}`}
                active={fork.active}
                onToggle={() =>
                  setActiveForks((prev) => ({
                    ...prev,
                    [fork.id]: !prev[fork.id]
                  }))
                }
              />
            ))}
          </div>
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-white/80">Tecnologías</h3>
            {techList.map((tech) => (
              <ToggleRow
                key={tech.name}
                label={tech.name}
                active={tech.active}
                onToggle={() =>
                  setTechEnabled((prev) => ({
                    ...prev,
                    [tech.name]: !prev[tech.name]
                  }))
                }
              />
            ))}
          </div>
        </div>

        <div className="space-y-6 rounded-3xl border border-white/10 bg-white/5 p-6">
          <h2 className="text-lg font-semibold">Personas P1–P5</h2>
          <p className="text-xs text-white/60">
            Ajusta el peso relativo de cada persona. El planner los usa para enfocar escenas sin romper la licencia social.
          </p>
          <div className="space-y-4">
            {Object.entries(personaLabels).map(([key, label]) => (
              <div key={key}>
                <div className="flex items-center justify-between text-xs">
                  <span>{key}</span>
                  <span>{personas[key]}%</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={personas[key]}
                  onChange={(event) =>
                    setPersonas((prev) => ({
                      ...prev,
                      [key]: Number(event.target.value)
                    }))
                  }
                  className="h-1 w-full cursor-pointer appearance-none rounded-full bg-white/20"
                />
                <p className="mt-1 text-[11px] text-white/50">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <button
            className="rounded-full bg-primary px-6 py-2 text-sm font-semibold text-black shadow-lg hover:-translate-y-0.5"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? "Generando…" : "Generar"}
          </button>
          <div className="text-sm text-white/70">
            {statusMessage ?? "Sin ejecuciones todavía. Usa el preset para empezar."}
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <TabBar activeTab={activeTab} onSelect={setActiveTab} />
        <div className="mt-6 min-h-[300px] rounded-2xl bg-black/40 p-5 text-sm leading-relaxed">
          {renderTab(activeTab, result, askWhyQuestion, setAskWhyQuestion, askWhyAnswer, askWhyError, handleAskWhy)}
        </div>
      </section>
    </main>
  );
}

function TutorialBlock() {
  return (
    <div className="mt-6 grid gap-4 rounded-2xl bg-black/40 p-4 text-xs text-white/70 lg:grid-cols-3">
      <div>
        <h3 className="text-sm font-semibold text-white">1. Configura el lattice</h3>
        <p>Selecciona el cuadrante con las barras A/B/C y define qué forks y tecnologías entran en juego.</p>
      </div>
      <div>
        <h3 className="text-sm font-semibold text-white">2. Genera y audita</h3>
        <p>El pipeline normaliza, planifica 12 beats, redacta documentos diegéticos y arma la novela sin infodumps.</p>
      </div>
      <div>
        <h3 className="text-sm font-semibold text-white">3. Pregunta por qué</h3>
        <p>
          Usa Ask-Why para justificar cualquier claim técnico. La respuesta se basa en el evidence ledger generado en la corrida.
        </p>
      </div>
    </div>
  );
}

function AxisSelector({
  label,
  options,
  selected,
  onChange
}: {
  label: string;
  options: Array<{ label: string; value: string }>;
  selected: string;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <div className="mb-2 text-sm font-medium text-white/80">{label}</div>
      <div className="flex gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={clsx(
              "flex-1 rounded-lg border px-3 py-2 text-xs",
              selected === option.value
                ? "border-primary bg-primary/20 text-primary"
                : "border-white/10 bg-black/40 text-white/70 hover:border-primary/60"
            )}
            type="button"
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function ToggleRow({ label, active, onToggle }: { label: string; active: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      className={clsx(
        "flex w-full items-center justify-between rounded-xl border px-3 py-2 text-left text-xs transition",
        active ? "border-primary bg-primary/10" : "border-white/10 bg-black/40 hover:border-primary/40"
      )}
      type="button"
    >
      <span>{label}</span>
      <span
        className={clsx(
          "inline-flex h-5 w-10 items-center rounded-full border px-1",
          active ? "border-primary bg-primary/40" : "border-white/20 bg-white/5"
        )}
      >
        <span
          className={clsx(
            "h-4 w-4 rounded-full bg-white transition-transform",
            active ? "translate-x-4" : "translate-x-0"
          )}
        />
      </span>
    </button>
  );
}

function TabBar({ activeTab, onSelect }: { activeTab: TabKey; onSelect: (tab: TabKey) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {tabs.map((tab) => (
        <button
          key={tab}
          className={clsx(
            "rounded-full px-4 py-2 text-xs font-semibold",
            activeTab === tab ? "bg-primary text-black" : "bg-black/40 text-white/60 hover:text-white"
          )}
          onClick={() => onSelect(tab)}
          type="button"
        >
          {tab}
        </button>
      ))}
    </div>
  );
}

function renderTab(
  tab: TabKey,
  result: GenerateResponse | null,
  askWhyQuestion: string,
  setAskWhyQuestion: (text: string) => void,
  askWhyAnswer: AskWhyResponse | null,
  askWhyError: string | null,
  onAskWhy: () => Promise<void>
) {
  if (!result) {
    return <p className="text-white/60">Genera una corrida para habilitar las vistas.</p>;
  }

  if (tab === "Outline") {
    return (
      <div className="space-y-4">
        <DownloadLinks result={result} />
        <pre className="whitespace-pre-wrap rounded-2xl bg-black/60 p-4 text-xs text-white/80">
          {result.outline_preview}
        </pre>
      </div>
    );
  }

  if (tab === "Capítulos") {
    return (
      <pre className="whitespace-pre-wrap rounded-2xl bg-black/60 p-4 text-xs leading-6 text-white/80">
        {result.novel_preview}
      </pre>
    );
  }

  if (tab === "Documentos") {
    return (
      <div className="space-y-4">
        {result.documents_preview &&
          Object.entries(result.documents_preview).map(([key, value]) => (
            <div key={key}>
              <h3 className="text-sm font-semibold text-white">{key.toUpperCase()}</h3>
              <pre className="mt-2 whitespace-pre-wrap rounded-2xl bg-black/60 p-4 text-xs text-white/80">{value}</pre>
            </div>
          ))}
      </div>
    );
  }

  if (tab === "Ledger") {
    return (
      <div className="space-y-4">
        {result.ledger_preview?.claims?.map((claim, index) => (
          <div key={claim.id ?? index} className="rounded-2xl border border-white/10 bg-black/60 p-4">
            <h3 className="text-sm font-semibold text-white">{claim.statement}</h3>
            <p className="text-[11px] text-white/60">Confianza: {claim.confidence?.toFixed?.(2) ?? "N/D"}</p>
            <div className="mt-2 text-xs text-white/70">
              <strong>Pasos:</strong>
              <ul className="list-disc space-y-1 pl-4">
                {claim.because?.map?.((step: any, idx: number) => <li key={idx}>{step.step}</li>)}
              </ul>
            </div>
            {claim.costs && (
              <div className="mt-2 text-xs text-white/70">
                <strong>Costos:</strong>
                <ul className="list-disc space-y-1 pl-4">
                  {claim.costs.map((cost: string, idx: number) => (
                    <li key={idx}>{cost}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-semibold text-white/80">Pregunta</label>
        <textarea
          value={askWhyQuestion}
          onChange={(event) => setAskWhyQuestion(event.target.value)}
          className="mt-1 w-full rounded-2xl bg-black/60 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          rows={3}
        />
      </div>
      <button
        onClick={onAskWhy}
        className="rounded-full bg-accent px-4 py-2 text-xs font-semibold text-black shadow hover:-translate-y-0.5"
        type="button"
      >
        Consultar Evidence Ledger
      </button>
      {askWhyError && <p className="text-xs text-red-400">{askWhyError}</p>}
      {askWhyAnswer && (
        <div className="rounded-2xl border border-white/10 bg-black/60 p-4 text-xs text-white/80">
          <pre className="whitespace-pre-wrap">{askWhyAnswer.answer}</pre>
          <p className="mt-2 text-[11px] text-white/50">Citas: {askWhyAnswer.citations.join(", ")}</p>
        </div>
      )}
    </div>
  );
}

function DownloadLinks({ result }: { result: GenerateResponse }) {
  const entries: Array<[string, string | undefined]> = [
    ["Outline", result.outline_path],
    ["Novela", result.novel_path],
    ["Ledger", result.ledger_path],
    ["Scenario", result.scenario_path],
    ["World", result.world_path],
    ["Run metadata", result.run_metadata_path],
    ["Export ZIP", result.export_zip_path]
  ];

  return (
    <div className="flex flex-wrap gap-3 text-[11px] text-white/60">
      {entries
        .filter(([, value]) => Boolean(value))
        .map(([label, value]) => (
          <span key={label} className="rounded-full bg-black/40 px-3 py-1">
            {label}: {value}
          </span>
        ))}
    </div>
  );
}

function quadrantFromAxes(axes: { compute_energy: string; governance_security: string }): string {
  const { compute_energy, governance_security } = axes;
  if (compute_energy === "high" && governance_security === "robust") return "Rieles Estables";
  if (compute_energy === "high" && governance_security === "weak") return "Selva Abierta";
  if (compute_energy === "low" && governance_security === "robust") return "Trincheras";
  return "Cortocircuito";
}

function toYaml(value: any, indent = 0): string {
  if (value === null || value === undefined) return "";
  const space = " ".repeat(indent);
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        const child = toYaml(item, indent + 2);
        if (typeof item === "object" && item !== null && !Array.isArray(item)) {
          return `${space}- ${child.trimStart()}`;
        }
        return `${space}- ${child.trim()}`;
      })
      .join("\n");
  }
  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, val]) => {
        const child = toYaml(val, indent + 2);
        if (child === "") {
          return `${space}${key}:`;
        }
        const needsBlock = child.includes("\n");
        if (needsBlock) {
          return `${space}${key}:\n${child}`;
        }
        return `${space}${key}: ${child.trim()}`;
      })
      .join("\n");
  }
  return String(value);
}
