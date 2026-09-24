# SciReview Chem

**Systematic Literature Review & Evidence Synthesis Workbench**

SciReview Chem is a zero-cost, local-first scientific application for transparent literature-review workflows in chemistry, materials science, environmental science, toxicology, and related fields.

> Active development build: protocol, search audit trails, reference import, reviewer-controlled deduplication, title/abstract and full-text screening, structured extraction, domain-level quality assessment, evidence tables, descriptive synthesis, project persistence, tests, and the dashboard are implemented. PRISMA visualization and report/export modules are under active development.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run tests with `pytest`.

## Scientific integrity principles

- Human-controlled inclusion and exclusion decisions
- No fabricated citations or guessed metadata
- Traceable exclusions and editable decision history
- Preserved raw imported data
- Reproducible, state-derived workflow counts
- No silent deletion of fuzzy duplicate candidates

The architecture and conservative methodological choices are documented in [docs/architecture.md](docs/architecture.md).

## Status and roadmap

The implementation follows the specification's sequential phases. Next are the protocol and search-strategy pages, followed by reference import, reviewer-confirmed deduplication, screening, extraction, quality assessment, evidence tables, visualization, and exports.
