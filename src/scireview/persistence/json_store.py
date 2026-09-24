from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypeVar

from scireview.models import (
    BibliographicRecord, DeduplicationCandidate, ExtractionEntry, ProjectMetadata,
    QualityAssessment, QualityDomainRating, ReviewProject, ReviewProtocol,
    ScreeningDecision, SearchStrategy,
)

T = TypeVar("T")


def _construct(cls: type[T], data: dict[str, Any]) -> T:
    return cls(**data)


def project_from_dict(data: dict[str, Any]) -> ReviewProject:
    if data.get("schema_version") != 1:
        raise ValueError(f"Unsupported project schema version: {data.get('schema_version')}")
    quality = []
    for item in data.get("quality_assessments", []):
        item = dict(item)
        item["domains"] = [_construct(QualityDomainRating, d) for d in item.get("domains", [])]
        quality.append(_construct(QualityAssessment, item))
    return ReviewProject(
        schema_version=1,
        metadata=_construct(ProjectMetadata, data.get("metadata", {})),
        protocol=_construct(ReviewProtocol, data.get("protocol", {})),
        searches=[_construct(SearchStrategy, x) for x in data.get("searches", [])],
        records=[_construct(BibliographicRecord, x) for x in data.get("records", [])],
        screening_decisions=[_construct(ScreeningDecision, x) for x in data.get("screening_decisions", [])],
        duplicate_candidates=[_construct(DeduplicationCandidate, x) for x in data.get("duplicate_candidates", [])],
        extraction_entries=[_construct(ExtractionEntry, x) for x in data.get("extraction_entries", [])],
        quality_assessments=quality,
        synthesis_notes=data.get("synthesis_notes", ""),
        other_source_records=data.get("other_source_records", 0),
    )


def save_project(project: ReviewProject, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    project.metadata.updated_at = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(project.to_dict(), indent=2, ensure_ascii=False)
    handle, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return destination


def load_project(path: str | Path) -> ReviewProject:
    with Path(path).open(encoding="utf-8") as stream:
        return project_from_dict(json.load(stream))


def project_to_json(project: ReviewProject) -> bytes:
    return json.dumps(project.to_dict(), indent=2, ensure_ascii=False).encode("utf-8")


def project_from_json(payload: bytes | str) -> ReviewProject:
    text = payload.decode("utf-8-sig") if isinstance(payload, bytes) else payload
    return project_from_dict(json.loads(text))
