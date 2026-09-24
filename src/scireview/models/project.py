from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


ReviewType = Literal["narrative", "systematic", "scoping", "evidence_map", "rapid", "gap_analysis"]
ScreeningStage = Literal["title_abstract", "full_text"]


@dataclass
class ProjectMetadata:
    name: str = "Untitled review"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    demonstration: bool = False
    notes: str = ""


@dataclass
class ReviewProtocol:
    title: str = ""
    review_type: ReviewType = "systematic"
    research_question: str = ""
    objective: str = ""
    scientific_domain: str = ""
    question_framework: str = "chemistry_materials"
    population_or_material: str = ""
    intervention_or_exposure: str = ""
    comparator: str = ""
    outcome: str = ""
    date_start: int | None = None
    date_end: int | None = None
    language_restrictions: list[str] = field(default_factory=list)
    study_type_restrictions: list[str] = field(default_factory=list)
    inclusion_criteria: list[str] = field(default_factory=list)
    exclusion_criteria: list[str] = field(default_factory=list)
    databases_planned: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class SearchStrategy:
    id: str = field(default_factory=lambda: str(uuid4()))
    database: str = ""
    exact_query: str = ""
    search_date: str | None = None
    records_retrieved: int | None = None
    records_screened: int | None = None
    records_retained: int | None = None
    notes: str = ""


@dataclass
class BibliographicRecord:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    journal: str | None = None
    abstract: str | None = None
    doi: str | None = None
    pmid: str | None = None
    url: str | None = None
    keywords: list[str] = field(default_factory=list)
    source_database: str | None = None
    publication_type: str | None = None
    full_text_path: str | None = None
    imported_at: str = field(default_factory=utc_now)
    import_batch_id: str | None = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)
    active: bool = True
    synthetic: bool = False


@dataclass
class ScreeningDecision:
    id: str = field(default_factory=lambda: str(uuid4()))
    record_id: str = ""
    stage: ScreeningStage = "title_abstract"
    decision: str = "uncertain"
    reason: str | None = None
    notes: str = ""
    reviewer: str = ""
    decided_at: str = field(default_factory=utc_now)

    def validate(self) -> None:
        allowed = {"title_abstract": {"include", "exclude", "uncertain"},
                   "full_text": {"include", "exclude", "uncertain", "awaiting_pdf"}}
        if self.decision not in allowed[self.stage]:
            raise ValueError(f"Invalid {self.stage} decision: {self.decision}")
        if self.decision == "exclude" and not (self.reason or "").strip():
            raise ValueError(f"A {self.stage.replace('_', '/')} exclusion requires an explicit reason")


@dataclass
class DeduplicationCandidate:
    id: str = field(default_factory=lambda: str(uuid4()))
    record_a_id: str = ""
    record_b_id: str = ""
    classification: Literal["confirmed", "likely", "possible"] = "possible"
    similarity_score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    matching_fields: list[str] = field(default_factory=list)
    resolution: Literal["keep_a", "keep_b", "keep_both", "merge"] | None = None
    resolved_at: str | None = None
    reviewer: str = ""


@dataclass
class ExtractionEntry:
    record_id: str = ""
    template: str = "general"
    values: dict[str, Any] = field(default_factory=dict)
    updated_at: str = field(default_factory=utc_now)


@dataclass
class QualityDomainRating:
    domain: str = ""
    rating: Literal["low_concern", "some_concern", "high_concern", "not_applicable", "unclear"] = "unclear"
    notes: str = ""


@dataclass
class QualityAssessment:
    record_id: str = ""
    framework: str = "generic"
    domains: list[QualityDomainRating] = field(default_factory=list)
    reviewer: str = ""
    updated_at: str = field(default_factory=utc_now)


@dataclass
class ReviewProject:
    schema_version: int = 1
    metadata: ProjectMetadata = field(default_factory=ProjectMetadata)
    protocol: ReviewProtocol = field(default_factory=ReviewProtocol)
    searches: list[SearchStrategy] = field(default_factory=list)
    records: list[BibliographicRecord] = field(default_factory=list)
    screening_decisions: list[ScreeningDecision] = field(default_factory=list)
    duplicate_candidates: list[DeduplicationCandidate] = field(default_factory=list)
    extraction_entries: list[ExtractionEntry] = field(default_factory=list)
    quality_assessments: list[QualityAssessment] = field(default_factory=list)
    synthesis_notes: str = ""
    other_source_records: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def add_screening_decision(self, decision: ScreeningDecision) -> None:
        if decision.record_id not in {record.id for record in self.records}:
            raise ValueError("Screening decision refers to an unknown record")
        decision.validate()
        self.screening_decisions.append(decision)
        self.metadata.updated_at = utc_now()

    def latest_decision(self, record_id: str, stage: ScreeningStage) -> ScreeningDecision | None:
        decisions = [
            item for item in self.screening_decisions
            if item.record_id == record_id and item.stage == stage
        ]
        if not decisions:
            return None
        return max(enumerate(decisions), key=lambda pair: (pair[1].decided_at, pair[0]))[1]
