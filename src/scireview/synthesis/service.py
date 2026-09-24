from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from scireview.evidence import EvidenceTable


MISSING_VALUES = {"", "NR", "not reported", "none", "nan"}


@dataclass(frozen=True)
class SynthesisSummary:
    study_count: int
    year_counts: dict[str, int]
    missing_counts: dict[str, int]


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip().casefold() in {item.casefold() for item in MISSING_VALUES})


def frequency_table(table: EvidenceTable, column: str, split_multi: bool = False) -> dict[str, int]:
    if column not in table.columns:
        raise ValueError(f"Unknown evidence column: {column}")
    counts: Counter[str] = Counter()
    for row in table.rows:
        value = row.get(column)
        if _is_missing(value):
            continue
        values = [str(value)]
        if split_multi:
            values = [item.strip() for item in str(value).replace(",", ";").split(";") if item.strip()]
        counts.update(values)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())))


def missing_data_summary(table: EvidenceTable) -> dict[str, int]:
    return {column: sum(_is_missing(row.get(column)) for row in table.rows) for column in table.columns}


def build_synthesis_summary(table: EvidenceTable) -> SynthesisSummary:
    years = Counter(str(row["year"]) for row in table.rows if not _is_missing(row.get("year")))
    return SynthesisSummary(
        study_count=len(table.rows),
        year_counts=dict(sorted(years.items())),
        missing_counts=missing_data_summary(table),
    )

