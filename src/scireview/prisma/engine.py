from __future__ import annotations

from dataclasses import dataclass, field

from scireview.models import ReviewProject, ScreeningDecision


@dataclass
class PrismaCounts:
    database_records: int = 0
    other_source_records: int = 0
    duplicates_removed: int = 0
    records_screened: int = 0
    records_excluded: int = 0
    reports_sought: int = 0
    reports_not_retrieved: int = 0
    full_texts_assessed: int = 0
    full_texts_excluded: int = 0
    studies_included: int = 0
    pending_title_abstract: int = 0
    pending_full_text: int = 0
    title_exclusion_reasons: dict[str, int] = field(default_factory=dict)
    full_text_exclusion_reasons: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def identified(self) -> int:
        return self.database_records + self.other_source_records

    @property
    def reconciled(self) -> bool:
        return self.identified > 0 and not self.warnings and self.pending_title_abstract == 0 and self.pending_full_text == 0


def _latest(decisions: list[ScreeningDecision], stage: str) -> dict[str, ScreeningDecision]:
    current: dict[str, ScreeningDecision] = {}
    for decision in decisions:
        if decision.stage != stage:
            continue
        existing = current.get(decision.record_id)
        if existing is None or decision.decided_at >= existing.decided_at:
            current[decision.record_id] = decision
    return current


def derive_prisma_counts(project: ReviewProject) -> PrismaCounts:
    counts = PrismaCounts(
        database_records=len(project.records),
        other_source_records=project.other_source_records,
        duplicates_removed=sum(not record.active for record in project.records),
    )
    active_ids = {record.id for record in project.records if record.active}
    title = _latest(project.screening_decisions, "title_abstract")
    full = _latest(project.screening_decisions, "full_text")
    counts.records_screened = sum(record_id in active_ids for record_id in title)
    counts.records_excluded = sum(d.decision == "exclude" and rid in active_ids for rid, d in title.items())
    eligible = {rid for rid, d in title.items() if rid in active_ids and d.decision in {"include", "uncertain"}}
    counts.reports_sought = len(eligible)
    counts.reports_not_retrieved = sum(d.decision == "awaiting_pdf" and rid in eligible for rid, d in full.items())
    counts.full_texts_assessed = sum(d.decision in {"include", "exclude", "uncertain"} and rid in eligible for rid, d in full.items())
    counts.full_texts_excluded = sum(d.decision == "exclude" and rid in eligible for rid, d in full.items())
    counts.studies_included = sum(d.decision == "include" and rid in eligible for rid, d in full.items())
    counts.pending_title_abstract = len(active_ids - set(title))
    counts.pending_full_text = len(eligible - set(full))
    for decision in title.values():
        if decision.record_id in active_ids and decision.decision == "exclude":
            reason = decision.reason or "Reason not recorded"
            counts.title_exclusion_reasons[reason] = counts.title_exclusion_reasons.get(reason, 0) + 1
    for decision in full.values():
        if decision.record_id in eligible and decision.decision == "exclude":
            reason = decision.reason or "Reason not recorded"
            counts.full_text_exclusion_reasons[reason] = counts.full_text_exclusion_reasons.get(reason, 0) + 1
    if counts.records_screened > len(active_ids):
        counts.warnings.append("Screened records exceed active records")
    assessed_balance = counts.full_texts_excluded + counts.studies_included
    uncertain_assessed = sum(d.decision == "uncertain" and rid in eligible for rid, d in full.items())
    if counts.full_texts_assessed != assessed_balance + uncertain_assessed:
        counts.warnings.append("Full-text assessment categories do not reconcile")
    if counts.duplicates_removed + len(active_ids) != counts.database_records:
        counts.warnings.append("Active records plus removed duplicates do not equal imported records")
    ineligible_full_text = set(full) - eligible
    if ineligible_full_text:
        counts.warnings.append(f"{len(ineligible_full_text)} full-text decision(s) belong to records no longer eligible")
    if project.other_source_records:
        counts.warnings.append("Other-source records are count-only and cannot be reconciled until imported as records")
    if counts.identified == 0:
        counts.warnings.append("No records have been imported; the review flow is not yet complete")
    return counts
