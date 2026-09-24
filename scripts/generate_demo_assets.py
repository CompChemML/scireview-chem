from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scireview.demo import DEMO_WARNING, build_demo_project
from scireview.persistence import save_project
from scireview.reporting import export_project_workbook, export_workflow_pdf


def main() -> None:
    output = ROOT / "sample_data"
    output.mkdir(parents=True, exist_ok=True)
    project = build_demo_project()
    save_project(project, output / "demo_review_project.json")
    (output / "demo_workflow_export.xlsx").write_bytes(export_project_workbook(project))
    (output / "portfolio_case_study.pdf").write_bytes(export_workflow_pdf(project))
    with (output / "demo_records.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["title", "authors", "year", "journal", "abstract", "source", "demo_warning"])
        for record in project.records:
            writer.writerow([record.title, "; ".join(record.authors), record.year, record.journal, record.abstract, record.source_database, DEMO_WARNING])
    with (output / "demo_records.ris").open("w", encoding="utf-8", newline="\n") as stream:
        for record in project.records[:8]:
            stream.write("TY  - JOUR\n")
            stream.write(f"TI  - {record.title}\n")
            for author in record.authors:
                stream.write(f"AU  - {author}\n")
            stream.write(f"PY  - {record.year}\n")
            stream.write(f"JO  - {record.journal}\n")
            stream.write(f"AB  - {record.abstract}\n")
            stream.write("N1  - DEMONSTRATION DATA - NOT REAL RESEARCH EVIDENCE\nER  -\n\n")
    with (output / "demo_records.bib").open("w", encoding="utf-8", newline="\n") as stream:
        for index, record in enumerate(project.records[8:16], start=9):
            authors = " and ".join(record.authors)
            stream.write(f"@article{{DEMO{index:03d},\n  title={{{record.title}}},\n  author={{{authors}}},\n  year={{{record.year}}},\n  journal={{{record.journal}}},\n  note={{{DEMO_WARNING}}}\n}}\n\n")


if __name__ == "__main__":
    main()

