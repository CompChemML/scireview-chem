from __future__ import annotations

from dataclasses import dataclass

from scireview.models import BibliographicRecord, ReviewProject, ScreeningDecision


TITLE_ABSTRACT_EXCLUSION_REASONS = (
    "Wrong population/system", "Wrong intervention/exposure", "Wrong outcome",
    "Wrong study type", "Not primary research", "Outside date range",
    "Wrong language", "Duplicate", "Insufficient information", "Other",
)

FULL_TEXT_EXCLUSION_REASONS = (
    "Wrong experimental system", "No relevant outcome", "Conference abstract only",
    "Insufficient methodology", "Duplicate publication",
    "Inaccessible required information", "Not within protocol criteria", "Other",
)


@dataclass(frozen=True)
class ScreeningSummary:
    total: int
    pending: int
    included: int
    excluded: int
    uncertain: int
    awaiting_pdf: int = 0


def current_decisions(project: ReviewProject, stage: str) -> dict[str, ScreeningDecision]:
    current: dict[str, ScreeningDecision] = {}
    for decision in project.screening_decisions:
        if decision.stage != stage:
            continue
        previous = current.get(decision.record_id)
        if previous is None or decision.decided_at >= previous.decided_at:
            current[decision.record_id] = decision
    return current


def eligible_for_full_text(project: ReviewProject) -> set[str]:
    title_decisions = current_decisions(project, "title_abstract")
    return {
        record.id for record in project.records
        if record.active
        and record.id in title_decisions
        and title_decisions[record.id].decision in {"include", "uncertain"}
    }


def screening_records(project: ReviewProject, stage: str) -> list[BibliographicRecord]:
    if stage == "title_abstract":
        return [record for record in project.records if record.active]
    if stage == "full_text":
        eligible = eligible_for_full_text(project)
        return [record for record in project.records if record.id in eligible]
    raise ValueError(f"Unknown screening stage: {stage}")


def record_decision(
    project: ReviewProject,
    record_id: str,
    stage: str,
    decision: str,
    reason: str | None = None,
    notes: str = "",
    reviewer: str = "",
) -> ScreeningDecision:
    if stage == "full_text" and record_id not in eligible_for_full_text(project):
        raise ValueError("Record is not eligible for full-text review")
    item = ScreeningDecision(
        record_id=record_id, stage=stage, decision=decision,
        reason=(reason or "").strip() or None, notes=notes.strip(), reviewer=reviewer.strip(),
    )
    project.add_screening_decision(item)
    return item


def screening_summary(project: ReviewProject, stage: str) -> ScreeningSummary:
    records = screening_records(project, stage)
    ids = {record.id for record in records}
    decisions = {key: value for key, value in current_decisions(project, stage).items() if key in ids}
    return ScreeningSummary(
        total=len(records), pending=len(ids - set(decisions)),
        included=sum(item.decision == "include" for item in decisions.values()),
        excluded=sum(item.decision == "exclude" for item in decisions.values()),
        uncertain=sum(item.decision == "uncertain" for item in decisions.values()),
        awaiting_pdf=sum(item.decision == "awaiting_pdf" for item in decisions.values()),
    )

