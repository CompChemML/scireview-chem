from __future__ import annotations

from scireview.deduplication import apply_resolution, find_duplicate_candidates
from scireview.extraction import upsert_extraction
from scireview.models import BibliographicRecord, ReviewProject, SearchStrategy
from scireview.quality import DEFAULT_QUALITY_DOMAINS, upsert_quality_assessment
from scireview.screening import record_decision


DEMO_WARNING = "DEMONSTRATION DATA - NOT A REAL SYSTEMATIC REVIEW"


def build_demo_project() -> ReviewProject:
    project = ReviewProject()
    project.metadata.name = "Adsorption of Heavy Metals Using Biochar and Hydrochar - Demonstration Evidence Review"
    project.metadata.demonstration = True
    project.metadata.notes = DEMO_WARNING
    protocol = project.protocol
    protocol.title = project.metadata.name
    protocol.review_type = "systematic"
    protocol.research_question = "In fictional aqueous systems, how are demonstration biochar and hydrochar materials characterized and evaluated for heavy-metal adsorption?"
    protocol.objective = "Demonstrate a transparent evidence-review workflow using wholly fictional records. No scientific inference should be drawn."
    protocol.scientific_domain = "Environmental chemistry and adsorption - demonstration only"
    protocol.population_or_material = "Fictional biochar and hydrochar adsorbents"
    protocol.intervention_or_exposure = "Fictional aqueous heavy-metal contamination"
    protocol.comparator = "Fictional alternative sorbents or preparation conditions"
    protocol.outcome = "Reported demonstration capacity, removal efficiency, characterization, and regeneration"
    protocol.date_start, protocol.date_end = 2018, 2026
    protocol.language_restrictions = ["English"]
    protocol.study_type_restrictions = ["Primary experimental demonstration studies"]
    protocol.inclusion_criteria = ["Clearly labelled synthetic primary study", "Aqueous metal adsorption outcome", "Biochar or hydrochar material"]
    protocol.exclusion_criteria = ["Wrong fictional material system", "No adsorption outcome", "Review or commentary format"]
    protocol.databases_planned = ["DemoIndex", "Other/manual"]
    project.searches = [
        SearchStrategy(database="DemoIndex", exact_query='("DEMONSTRATION biochar" OR "DEMONSTRATION hydrochar") AND (adsorption OR removal) AND (lead OR cadmium OR copper)', search_date="2026-09-20", records_retrieved=34, notes=DEMO_WARNING),
        SearchStrategy(database="Other/manual", exact_query="Fictional portfolio seed records supplied with SciReview Chem", search_date="2026-09-20", records_retrieved=6, notes=DEMO_WARNING),
    ]
    pollutants = ["Lead", "Cadmium", "Copper", "Nickel", "Chromium", "Zinc"]
    materials = ["Pine Biochar", "Rice Husk Biochar", "Algae Hydrochar", "Coconut Biochar", "Cellulose Hydrochar", "Bamboo Biochar"]
    models = ["Langmuir", "Freundlich", "Sips"]
    for index in range(1, 37):
        pollutant = pollutants[(index - 1) % len(pollutants)]
        material = materials[(index - 1) % len(materials)]
        title = f"DEMONSTRATION Study {index:03d}: {material} for Fictional {pollutant} Adsorption"
        project.records.append(BibliographicRecord(
            title=title,
            authors=[f"DemoAuthor-{index:03d}, A.", "SyntheticResearcher, B."],
            year=2018 + index % 8,
            journal="Journal of Fictional Adsorption Demonstrations",
            abstract=f"{DEMO_WARNING}. This synthetic record evaluates {material.lower()} for a fictional {pollutant.lower()} adsorption workflow.",
            keywords=["DEMONSTRATION", material, pollutant, "adsorption"],
            source_database="DemoIndex" if index <= 30 else "Other/manual",
            publication_type="Synthetic demonstration article",
            raw_metadata={"demo_id": f"DEMO-{index:03d}", "warning": DEMO_WARNING},
            synthetic=True,
        ))
    for source_index in (1, 7, 13, 19):
        source = project.records[source_index - 1]
        project.records.append(BibliographicRecord(
            title=source.title, authors=list(source.authors), year=source.year, journal=source.journal,
            abstract=source.abstract, keywords=list(source.keywords), source_database="Other/manual",
            publication_type=source.publication_type,
            raw_metadata={"demo_id": f"DEMO-DUP-{source_index:03d}", "warning": DEMO_WARNING, "duplicate_of": source.raw_metadata["demo_id"]},
            synthetic=True,
        ))
    project.duplicate_candidates = find_duplicate_candidates(project.records, fuzzy_threshold=99)
    duplicate_ids = {project.records[index - 1].id for index in (1, 7, 13, 19)}
    for candidate in project.duplicate_candidates:
        if candidate.record_a_id in duplicate_ids:
            apply_resolution(project, candidate.id, "keep_a", reviewer="DEMO REVIEWER")
    active = [record for record in project.records if record.active]
    for index, record in enumerate(active, start=1):
        if index <= 10:
            reasons = ["Wrong population/system", "Wrong outcome", "Not primary research"]
            record_decision(project, record.id, "title_abstract", "exclude", reasons[(index - 1) % len(reasons)], "Synthetic screening decision", "DEMO REVIEWER")
        else:
            record_decision(project, record.id, "title_abstract", "include", notes="Synthetic screening decision", reviewer="DEMO REVIEWER")
    eligible = active[10:]
    for index, record in enumerate(eligible, start=1):
        if index <= 6:
            reasons = ["No relevant outcome", "Insufficient methodology", "Not within protocol criteria"]
            record_decision(project, record.id, "full_text", "exclude", reasons[(index - 1) % len(reasons)], "Synthetic full-text decision", "DEMO REVIEWER")
        else:
            record_decision(project, record.id, "full_text", "include", notes="Synthetic full-text decision", reviewer="DEMO REVIEWER")
            pollutant = pollutants[(index + 3) % len(pollutants)]
            material = materials[(index + 1) % len(materials)]
            upsert_extraction(project, record.id, "adsorption", {
                "adsorbent": material, "adsorbate_pollutant": pollutant,
                "ph": str(4 + index % 5), "temperature": str(20 + index % 4 * 5),
                "adsorption_capacity": str(40 + index * 7), "removal_efficiency": str(70 + index % 6 * 4),
                "equilibrium_models": models[index % len(models)],
                "kinetic_models": "Pseudo-second-order" if index % 3 else "Pseudo-first-order",
                "bet_surface_area": None if index % 4 == 0 else str(120 + index * 9),
                "regeneration_cycles": None if index % 5 == 0 else str(2 + index % 5),
                "key_conclusion": f"{DEMO_WARNING}. Fictional result for workflow testing only.",
            })
            ratings = {}
            for domain_index, domain in enumerate(DEFAULT_QUALITY_DOMAINS):
                rating = ("low_concern", "some_concern", "unclear")[(index + domain_index) % 3]
                ratings[domain] = (rating, "Synthetic domain judgment for software demonstration")
            upsert_quality_assessment(project, record.id, "Demonstration generic domains", ratings, "DEMO REVIEWER")
    project.synthesis_notes = (f"{DEMO_WARNING}. The fictional dataset frequently reports adsorption capacity and model fitting, while regeneration and BET data are intentionally missing in some records. "
                               "These patterns demonstrate software behavior and are not scientific findings.")
    return project

