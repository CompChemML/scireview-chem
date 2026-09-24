from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO
from uuid import uuid4

from scireview.models import BibliographicRecord


@dataclass
class ImportResult:
    records: list[BibliographicRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    batch_id: str = field(default_factory=lambda: str(uuid4()))


ALIASES = {
    "title": ("title", "ti", "t1", "article title"),
    "authors": ("authors", "author", "au", "a1"),
    "year": ("year", "py", "publication year", "date"),
    "journal": ("journal", "jo", "jf", "t2", "source title"),
    "abstract": ("abstract", "ab", "n2"),
    "doi": ("doi", "do"),
    "pmid": ("pmid", "an"),
    "url": ("url", "ur", "link"),
    "keywords": ("keywords", "keyword", "kw"),
    "publication_type": ("publication type", "type", "ty"),
}


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if not text or text.casefold() in {"nan", "none", "nat"} else text


def _first(raw: dict[str, Any], names: tuple[str, ...]) -> Any:
    indexed = {str(key).strip().casefold(): value for key, value in raw.items()}
    for name in names:
        value = indexed.get(name.casefold())
        if value is not None and _clean(value) is not None:
            return value
    return None


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = _clean(value)
    if not text:
        return []
    delimiter = ";" if ";" in text else " and " if " and " in text else None
    return [item.strip() for item in text.split(delimiter)] if delimiter else [text]


def _year(value: Any) -> int | None:
    text = _clean(value)
    if not text:
        return None
    match = re.search(r"\b(1[6-9]\d{2}|20\d{2}|21\d{2})\b", text)
    return int(match.group(1)) if match else None


def _record(raw: dict[str, Any], source: str, batch_id: str) -> BibliographicRecord:
    return BibliographicRecord(
        title=_clean(_first(raw, ALIASES["title"])) or "",
        authors=_as_list(_first(raw, ALIASES["authors"])),
        year=_year(_first(raw, ALIASES["year"])),
        journal=_clean(_first(raw, ALIASES["journal"])),
        abstract=_clean(_first(raw, ALIASES["abstract"])),
        doi=_clean(_first(raw, ALIASES["doi"])),
        pmid=_clean(_first(raw, ALIASES["pmid"])),
        url=_clean(_first(raw, ALIASES["url"])),
        keywords=_as_list(_first(raw, ALIASES["keywords"])),
        publication_type=_clean(_first(raw, ALIASES["publication_type"])),
        source_database=source,
        import_batch_id=batch_id,
        raw_metadata={str(key): value for key, value in raw.items()},
    )


def _decode(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode text file")


def _parse_csv(content: bytes) -> list[dict[str, Any]]:
    text = _decode(content)
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    return [dict(row) for row in csv.DictReader(io.StringIO(text), dialect=dialect)]


def _parse_ris(content: bytes) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    last_tag: str | None = None
    multi = {"AU", "A1", "KW"}
    for line in _decode(content).splitlines():
        match = re.match(r"^([A-Z0-9]{2})\s*-\s?(.*)$", line)
        if match:
            tag, value = match.groups()
            last_tag = tag
            if tag == "ER":
                if current:
                    records.append(current)
                current, last_tag = {}, None
            elif tag in multi:
                current.setdefault(tag, []).append(value.strip())
            elif tag in current:
                existing = current[tag]
                current[tag] = f"{existing}\n{value.strip()}"
            else:
                current[tag] = value.strip()
        elif line.strip() and last_tag and last_tag in current:
            if isinstance(current[last_tag], list):
                current[last_tag][-1] += " " + line.strip()
            else:
                current[last_tag] += " " + line.strip()
    if current:
        records.append(current)
    return records


def _parse_bibtex(content: bytes) -> list[dict[str, Any]]:
    text = _decode(content)
    records: list[dict[str, Any]] = []
    position = 0
    entry_start = re.compile(r"@(\w+)\s*([{(])", re.I)
    while match := entry_start.search(text, position):
        entry_type, opener = match.group(1), match.group(2)
        closer = "}" if opener == "{" else ")"
        depth, quote, escaped, end = 1, False, False, match.end()
        for index in range(match.end(), len(text)):
            char = text[index]
            if char == '"' and not escaped:
                quote = not quote
            if not quote:
                if char == opener:
                    depth += 1
                elif char == closer:
                    depth -= 1
                    if depth == 0:
                        end = index
                        break
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
        body = text[match.end():end]
        key, _, fields_text = body.partition(",")
        raw: dict[str, Any] = {"ENTRYTYPE": entry_type, "ID": key.strip()}
        field_pattern = re.compile(r"(\w[\w-]*)\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}|\"((?:[^\"\\]|\\.)*)\"|([^,\n]+))\s*,?", re.S)
        for field_match in field_pattern.finditer(fields_text):
            raw[field_match.group(1)] = next(value for value in field_match.groups()[1:] if value is not None).strip()
        records.append(raw)
        position = end + 1
    return records


def _parse_xlsx(content: bytes) -> list[dict[str, Any]]:
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("XLSX import requires pandas and openpyxl") from exc
    frame = pd.read_excel(io.BytesIO(content), dtype=object)
    return frame.where(frame.notna(), None).to_dict(orient="records")


def import_references(
    content: bytes | BinaryIO, filename: str, source_database: str = "Imported file"
) -> ImportResult:
    payload = content.read() if hasattr(content, "read") else content
    if not isinstance(payload, bytes):
        raise TypeError("Reference import content must be bytes or a binary stream")
    suffix = Path(filename).suffix.casefold()
    parsers = {".csv": _parse_csv, ".tsv": _parse_csv, ".ris": _parse_ris, ".bib": _parse_bibtex, ".bibtex": _parse_bibtex, ".xlsx": _parse_xlsx}
    if suffix not in parsers:
        raise ValueError(f"Unsupported reference format: {suffix or 'unknown'}")
    result = ImportResult()
    rows = parsers[suffix](payload)
    for number, raw in enumerate(rows, start=1):
        record = _record(raw, source_database, result.batch_id)
        if not record.title:
            result.warnings.append(f"Row/entry {number} has no title; metadata was preserved")
        result.records.append(record)
    if not result.records:
        result.warnings.append("No reference records were found in the file")
    return result

