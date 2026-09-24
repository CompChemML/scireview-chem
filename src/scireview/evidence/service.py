from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scireview.extraction import included_records
from scireview.models import ReviewProject


BASE_COLUMNS = ("study_id", "title", "authors", "year", "journal", "doi", "source_database")


@dataclass(frozen=True)
class EvidenceTable:
    columns: tuple[str, ...]
    rows: list[dict[str, Any]]


def _display(value: Any) -> Any:
    return "NR" if value is None or value == "" or value == [] else value


def build_evidence_table(project: ReviewProject, missing_marker: str = "NR") -> EvidenceTable:
    extraction = {entry.record_id: entry for entry in project.extraction_entries}
    dynamic_columns: list[str] = []
    for record in included_records(project):
        entry = extraction.get(record.id)
        if entry:
            for key in entry.values:
                if key not in dynamic_columns:
                    dynamic_columns.append(key)
    columns = BASE_COLUMNS + tuple(dynamic_columns)
    rows = []
    for record in included_records(project):
        entry = extraction.get(record.id)
        values = entry.values if entry else {}
        row = {
            "study_id": record.id,
            "title": record.title or missing_marker,
            "authors": "; ".join(record.authors) if record.authors else missing_marker,
            "year": record.year if record.year is not None else missing_marker,
            "journal": record.journal or missing_marker,
            "doi": record.doi or missing_marker,
            "source_database": record.source_database or missing_marker,
        }
        for column in dynamic_columns:
            value = values.get(column)
            row[column] = missing_marker if value is None or value == "" or value == [] else value
        rows.append(row)
    return EvidenceTable(columns=columns, rows=rows)


def filter_evidence_rows(
    table: EvidenceTable,
    search: str = "",
    filters: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    needle = search.strip().casefold()
    filters = filters or {}
    result = []
    for row in table.rows:
        if needle and not any(needle in str(value).casefold() for value in row.values()):
            continue
        if any(allowed and str(row.get(column)) not in allowed for column, allowed in filters.items()):
            continue
        result.append(row)
    return result

