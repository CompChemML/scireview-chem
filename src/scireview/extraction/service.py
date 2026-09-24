from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

from scireview.models import ExtractionEntry, ReviewProject
from scireview.screening import current_decisions


FieldKind = Literal["text", "number", "yes_no", "category", "multi_select"]


@dataclass(frozen=True)
class ExtractionField:
    key: str
    label: str
    kind: FieldKind = "text"
    options: tuple[str, ...] = ()
    unit: str | None = None


GENERAL_FIELDS = (
    ExtractionField("citation", "Citation"), ExtractionField("country", "Country"),
    ExtractionField("study_objective", "Study objective"), ExtractionField("study_design", "Study design"),
    ExtractionField("sample_material", "Sample / material"), ExtractionField("experimental_conditions", "Experimental conditions"),
    ExtractionField("methods", "Methods"), ExtractionField("primary_outcome", "Primary outcome"),
    ExtractionField("secondary_outcomes", "Secondary outcomes"), ExtractionField("key_findings", "Key findings"),
    ExtractionField("limitations", "Limitations"), ExtractionField("funding", "Funding"),
    ExtractionField("conflicts_of_interest", "Conflicts of interest"), ExtractionField("notes", "Notes"),
)

ADSORPTION_FIELDS = (
    ExtractionField("adsorbent", "Adsorbent"), ExtractionField("precursor", "Precursor"),
    ExtractionField("synthesis_method", "Synthesis method"), ExtractionField("activation_method", "Activation method"),
    ExtractionField("adsorbate_pollutant", "Adsorbate / pollutant"),
    ExtractionField("initial_concentration", "Initial concentration", "number"),
    ExtractionField("ph", "pH", "number"), ExtractionField("temperature", "Temperature", "number", unit="°C"),
    ExtractionField("adsorbent_dosage", "Adsorbent dosage", "number"),
    ExtractionField("contact_time", "Contact time", "number"),
    ExtractionField("adsorption_capacity", "Adsorption capacity", "number"),
    ExtractionField("removal_efficiency", "Removal efficiency", "number", unit="%"),
    ExtractionField("equilibrium_models", "Equilibrium models"), ExtractionField("kinetic_models", "Kinetic models"),
    ExtractionField("thermodynamic_analysis", "Thermodynamic analysis", "yes_no"),
    ExtractionField("bet_surface_area", "BET surface area", "number", unit="m²/g"),
    ExtractionField("pore_volume", "Pore volume", "number"),
    ExtractionField("xrd", "XRD reported", "yes_no"), ExtractionField("ftir", "FTIR reported", "yes_no"),
    ExtractionField("sem", "SEM reported", "yes_no"), ExtractionField("tem", "TEM reported", "yes_no"),
    ExtractionField("xps", "XPS reported", "yes_no"),
    ExtractionField("regeneration_cycles", "Regeneration cycles", "number"),
    ExtractionField("key_conclusion", "Key conclusion"),
)

MLIP_TRANSPORT_FIELDS = (
    ExtractionField("citation", "Citation"), ExtractionField("year", "Year", "number"),
    ExtractionField("material_system", "Material / system"), ExtractionField("mobile_ion", "Mobile ion"),
    ExtractionField("mlip_architecture", "MLIP architecture"),
    ExtractionField("training_data_source", "Training-data source"), ExtractionField("dft_method", "DFT method"),
    ExtractionField("training_set_size", "Training-set size"), ExtractionField("simulation_cell_size", "Simulation cell size"),
    ExtractionField("trajectory_length", "Trajectory length"), ExtractionField("temperature_range", "Temperature range"),
    ExtractionField("disorder_defects", "Disorder / defects represented?", "yes_no"),
    ExtractionField("transport_observable", "Transport observable"), ExtractionField("msd", "MSD reported?", "yes_no"),
    ExtractionField("tracer_diffusion", "Tracer diffusion reported?", "yes_no"),
    ExtractionField("collective_diffusion", "Collective diffusion reported?", "yes_no"),
    ExtractionField("ionic_conductivity", "Ionic conductivity reported?", "yes_no"),
    ExtractionField("haven_ratio", "Haven ratio / correlation factor reported?", "yes_no"),
    ExtractionField("activation_energy", "Activation energy"), ExtractionField("transport_dimensionality", "Transport dimensionality"),
    ExtractionField("main_finding", "Main finding"), ExtractionField("limitations", "Limitations"),
    ExtractionField("relevance", "Relevance to review question"),
)


def included_records(project: ReviewProject):
    decisions = current_decisions(project, "full_text")
    return [record for record in project.records if record.active and decisions.get(record.id) and decisions[record.id].decision == "include"]


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def upsert_extraction(project: ReviewProject, record_id: str, template: str, values: dict[str, Any]) -> ExtractionEntry:
    if record_id not in {record.id for record in included_records(project)}:
        raise ValueError("Data extraction is limited to included full-text studies")
    cleaned = {str(key): _normalize_value(value) for key, value in values.items()}
    existing = next((item for item in project.extraction_entries if item.record_id == record_id), None)
    if existing:
        existing.template = template
        existing.values = cleaned
        existing.updated_at = datetime.now(timezone.utc).isoformat()
        return existing
    entry = ExtractionEntry(record_id=record_id, template=template, values=cleaned)
    project.extraction_entries.append(entry)
    return entry


def missing_fields(entry: ExtractionEntry, fields: tuple[ExtractionField, ...]) -> list[str]:
    return [field.key for field in fields if entry.values.get(field.key) in (None, "", [])]
