from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from itertools import combinations
from datetime import datetime, timezone

try:
    from rapidfuzz.fuzz import ratio as _ratio
except ImportError:  # Keeps core logic testable before optional dependencies are installed.
    def _ratio(left: str, right: str) -> float:
        return SequenceMatcher(None, left, right).ratio() * 100

from scireview.models import BibliographicRecord, DeduplicationCandidate, ReviewProject


def normalize_doi(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    normalized = value.strip().lower()
    normalized = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", normalized)
    normalized = normalized.strip().rstrip(".,;)")
    return normalized or None


def normalize_title(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", value or "").casefold()
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _first_author(record: BibliographicRecord) -> str:
    return normalize_title(record.authors[0]) if record.authors else ""


def find_duplicate_candidates(
    records: list[BibliographicRecord], fuzzy_threshold: float = 88.0
) -> list[DeduplicationCandidate]:
    candidates: list[DeduplicationCandidate] = []
    for left, right in combinations(records, 2):
        reasons: list[str] = []
        fields: list[str] = []
        left_doi, right_doi = normalize_doi(left.doi), normalize_doi(right.doi)
        title_left, title_right = normalize_title(left.title), normalize_title(right.title)
        score = float(_ratio(title_left, title_right)) if title_left and title_right else 0.0
        classification: str | None = None
        if left_doi and left_doi == right_doi:
            classification = "confirmed"
            reasons.append("Same normalized DOI")
            fields.append("doi")
        elif left.pmid and right.pmid and left.pmid.strip() == right.pmid.strip():
            classification = "confirmed"
            reasons.append("Same PMID")
            fields.append("pmid")
        elif title_left and title_left == title_right:
            classification = "likely"
            reasons.append("Same normalized title")
            fields.append("title")
        elif score >= fuzzy_threshold:
            same_year = left.year is not None and left.year == right.year
            same_author = bool(_first_author(left)) and _first_author(left) == _first_author(right)
            classification = "likely" if score >= 95 and (same_year or same_author) else "possible"
            reasons.append(f"Title similarity = {score:.1f}%")
            fields.append("title")
            if same_year:
                reasons.append("Same publication year")
                fields.append("year")
            if same_author:
                reasons.append("Same normalized first author")
                fields.append("first_author")
        if classification:
            candidates.append(DeduplicationCandidate(
                record_a_id=left.id, record_b_id=right.id,
                classification=classification, similarity_score=round(score, 1),
                reasons=reasons, matching_fields=fields,
            ))
    return candidates


def apply_resolution(
    project: ReviewProject,
    candidate_id: str,
    resolution: str,
    reviewer: str = "",
) -> DeduplicationCandidate:
    """Apply an explicit human resolution without removing raw record objects."""
    allowed = {"keep_a", "keep_b", "keep_both", "merge"}
    if resolution not in allowed:
        raise ValueError(f"Unknown duplicate resolution: {resolution}")
    candidate = next((item for item in project.duplicate_candidates if item.id == candidate_id), None)
    if candidate is None:
        raise ValueError("Unknown duplicate candidate")
    records = {record.id: record for record in project.records}
    if candidate.record_a_id not in records or candidate.record_b_id not in records:
        raise ValueError("Duplicate candidate refers to a missing record")
    left, right = records[candidate.record_a_id], records[candidate.record_b_id]
    left.active = right.active = True
    if resolution == "keep_a":
        right.active = False
    elif resolution == "keep_b":
        left.active = False
    elif resolution == "merge":
        scalar_fields = ("title", "year", "journal", "abstract", "doi", "pmid", "url", "source_database", "publication_type")
        for name in scalar_fields:
            if not getattr(left, name) and getattr(right, name):
                setattr(left, name, getattr(right, name))
        left.authors = list(dict.fromkeys(left.authors + right.authors))
        left.keywords = list(dict.fromkeys(left.keywords + right.keywords))
        right.active = False
    candidate.resolution = resolution  # type: ignore[assignment]
    candidate.reviewer = reviewer.strip()
    candidate.resolved_at = datetime.now(timezone.utc).isoformat()
    return candidate
