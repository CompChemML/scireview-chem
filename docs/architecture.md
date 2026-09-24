# SciReview Chem architecture and methodology

## Architecture

SciReview Chem is a local-first Streamlit application with a deliberately strict boundary between the user interface and research logic:

- `app.py` and `pages/` render workflow views and translate user actions into domain operations.
- `src/scireview/models/` defines the canonical, versioned project state.
- `src/scireview/importers/` preserves source metadata while mapping known fields into canonical records.
- `src/scireview/deduplication/` proposes auditable record pairs; it never silently removes records.
- `src/scireview/prisma/` derives flow counts from records and decisions.
- `src/scireview/persistence/` performs atomic, local project saves.
- Reporting and export code consumes the same project state and must not invent missing values.

The first persistence format is versioned JSON. It is inspectable, portable, easy to test, and sufficient for an MVP. SQLite remains an option if project scale makes indexed access necessary.

## Core schemas

`BibliographicRecord` contains canonical bibliographic fields, immutable raw imported metadata, provenance, an internal UUID, and an explicit active state. Missing metadata remains missing.

`ReviewProtocol` stores the question, review type, framework fields, scope restrictions, and criteria. Free-text criteria are stored as ordered lists so that wording is preserved.

`SearchStrategy` stores the database, exact query, execution date, result count, and notes. Database-specific queries are independent records.

`ScreeningDecision` stores a stage, decision, reason, notes, reviewer, and timestamp. Decision history is append-only; the latest decision controls current state.

`DeduplicationCandidate` stores both record IDs, classification, score, matching evidence, and an optional human resolution. Resolution changes active state only through an explicit reviewer action; raw records remain stored.

`ExtractionEntry` and `QualityAssessment` store user-entered study data and domain-level ratings without inferring absent values or computing a universal quality score.

`ReviewProject` is the aggregate root and includes schema version, metadata, protocol, searches, records, decision histories, extraction, quality assessment, and duplicate audit records.

## Deduplication strategy

Candidate generation is deterministic and identifier-first:

1. normalized DOI exact match -> confirmed candidate;
2. normalized PMID exact match -> confirmed candidate;
3. normalized title exact match -> likely candidate (confirmed only by a reviewer);
4. high fuzzy-title similarity -> likely or possible candidate;
5. title similarity combined with year and first-author agreement -> confidence adjustment.

DOIs are normalized by removing resolver prefixes and `doi:` labels and lowercasing. Titles are Unicode-normalized, lowercased, and reduced to alphanumeric tokens. Fuzzy matching proposes pairs only. No candidate is automatically deleted, and every resolution is retained in the audit log.

## PRISMA state model

Counts are derived from current active records and the latest reviewer decision at each stage:

- identified = all imported records plus explicitly recorded other-source records;
- duplicates removed = inactive records removed by confirmed human duplicate resolutions;
- screened = active records with a title/abstract decision;
- records excluded = latest title/abstract decision is `exclude`;
- reports sought = active records included or uncertain after title/abstract screening;
- reports not retrieved = latest full-text decision is `awaiting_pdf`;
- full texts assessed = records with an include, exclude, or uncertain full-text decision;
- full texts excluded = latest full-text decision is `exclude`;
- studies included = latest full-text decision is `include`.

Validation reports equations separately instead of forcing inconsistent states into a plausible total. In-progress reviews are valid workflow states but are reported as incomplete rather than reconciled.

## Methodological risks and conservative choices

- **Duplicate ambiguity:** legitimate companion papers and minor title changes can resemble duplicates. All removals require human confirmation.
- **Changing decisions:** counts can drift if old decisions are counted. Only the latest stage-specific decision is current; full history remains auditable.
- **PRISMA ambiguity:** “reports sought,” “not retrieved,” and “assessed” need mutually clear operational definitions. The application documents its definitions and exposes reconciliation warnings.
- **Review-type mismatch:** workflows vary between systematic, scoping, rapid, narrative, and evidence-map reviews. The protocol records the chosen type and the UI does not label every review systematic.
- **Quality-tool misuse:** one checklist cannot represent every study design. Assessments are template-based and domain-level, with no authoritative aggregate score.
- **Missing data:** absent bibliographic and extracted values remain null or explicit `NR`; they are never converted to zero or guessed.
- **Source conflicts:** canonical mapping must not destroy imported values. Raw metadata and provenance are retained, and later metadata edits will be audited.
- **Synthetic demonstrations:** every demo record and output must be unmistakably labelled as fictional and must not be presented as scientific evidence.

