from __future__ import annotations

from datetime import datetime, timezone

from scireview.extraction import included_records
from scireview.models import QualityAssessment, QualityDomainRating, ReviewProject


DEFAULT_QUALITY_DOMAINS = (
    "Clear research objective", "Appropriate study design", "Adequate method description",
    "Sample/replicate clarity", "Control/comparator suitability", "Statistical analysis adequacy",
    "Outcome reporting completeness", "Potential confounding", "Selective reporting concerns",
    "Reproducibility information",
)

ALLOWED_RATINGS = {"low_concern", "some_concern", "high_concern", "not_applicable", "unclear"}


def upsert_quality_assessment(
    project: ReviewProject,
    record_id: str,
    framework: str,
    ratings: dict[str, tuple[str, str]],
    reviewer: str = "",
) -> QualityAssessment:
    if record_id not in {record.id for record in included_records(project)}:
        raise ValueError("Quality assessment is limited to included full-text studies")
    domains = []
    for domain, (rating, notes) in ratings.items():
        if rating not in ALLOWED_RATINGS:
            raise ValueError(f"Invalid quality rating: {rating}")
        domains.append(QualityDomainRating(domain=domain.strip(), rating=rating, notes=notes.strip()))
    if not domains:
        raise ValueError("At least one quality domain is required")
    existing = next((item for item in project.quality_assessments if item.record_id == record_id), None)
    if existing:
        existing.framework = framework.strip() or "custom"
        existing.domains = domains
        existing.reviewer = reviewer.strip()
        existing.updated_at = datetime.now(timezone.utc).isoformat()
        return existing
    assessment = QualityAssessment(
        record_id=record_id, framework=framework.strip() or "custom",
        domains=domains, reviewer=reviewer.strip(),
    )
    project.quality_assessments.append(assessment)
    return assessment

