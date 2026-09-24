from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scireview.models import ReviewProject, SearchStrategy
from scireview.persistence import save_project
from scireview.reporting import export_portfolio_case_study


def build_project() -> ReviewProject:
    project = ReviewProject()
    project.metadata.name = "Iron-Oxide-Modified Biochar for Removing Arsenic from Groundwater"
    protocol = project.protocol
    protocol.title = project.metadata.name
    protocol.review_type = "systematic"
    protocol.research_question = "How do iron-oxide modification methods, synthesis conditions, water chemistry, and regeneration cycles affect arsenic adsorption by engineered biochar?"
    protocol.objective = "Systematically map and compare experimental evidence on arsenic removal from water using iron-oxide-modified biochar, with emphasis on preparation, water chemistry, performance, characterization, and regeneration."
    protocol.scientific_domain = "Environmental chemistry and engineered adsorbent materials"
    protocol.population_or_material = "Iron-oxide-modified biochar tested in aqueous arsenic systems"
    protocol.intervention_or_exposure = "Biochar iron modification method and arsenic-contaminated water exposure"
    protocol.comparator = "Unmodified biochar, alternative iron phases, or differing synthesis conditions"
    protocol.outcome = "Arsenic adsorption capacity, removal efficiency, kinetics, selectivity, and regeneration"
    protocol.date_start, protocol.date_end = 2000, 2026
    protocol.language_restrictions = ["English"]
    protocol.study_type_restrictions = ["Primary experimental studies", "Peer-reviewed journal articles"]
    protocol.inclusion_criteria = [
        "Iron-modified biochar is evaluated", "Arsenic is tested in an aqueous system",
        "Adsorption or removal performance is reported", "Experimental methods are described",
    ]
    protocol.exclusion_criteria = [
        "No arsenic outcome", "Biochar is not iron modified", "Review, commentary, or conference abstract only",
        "No primary experimental data", "Non-aqueous system",
    ]
    protocol.notes = "Protocol-stage case study created by testing SciReview Chem in the built-in browser. No references have been imported and no evidence conclusions are claimed."
    project.searches.append(SearchStrategy(
        database="PubMed",
        exact_query='(biochar OR biocarbon OR "pyrolyzed biomass") AND ("iron oxide" OR magnetite OR hematite OR "zero-valent iron" OR iron-modified) AND (arsenic OR arsenite OR arsenate OR groundwater)',
        search_date=None,
        records_retrieved=None,
        notes="Protocol-stage draft. Not yet executed; database field tags and retrieval count require researcher verification.",
    ))
    project.synthesis_notes = "No synthesis performed. References must be legally obtained, imported, deduplicated, and screened before evidence patterns or conclusions can be reported."
    return project


def main() -> None:
    output = ROOT / "sample_data"
    output.mkdir(parents=True, exist_ok=True)
    project = build_project()
    save_project(project, output / "arsenic_biochar_protocol_project.json")
    (output / "arsenic_biochar_protocol_case_study.pdf").write_bytes(export_portfolio_case_study(project))


if __name__ == "__main__":
    main()
