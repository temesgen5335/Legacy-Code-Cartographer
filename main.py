import os
import sys
from pathlib import Path
from src.graph.knowledge_graph import KnowledgeGraph
from src.agents.surveyor import SurveyorAgent
from src.agents.hydrologist import HydrologistAgent
from src.agents.semanticist import SemanticistAgent
from src.agents.archivist import ArchivistAgent

def main(target_path: str):
    print(f"Starting Cartography on: {target_path}")
    kg = KnowledgeGraph()
    
    # 1. Surveyor (Structure)
    print("Phase 1: Surveyor Analysis...")
    surveyor = SurveyorAgent(target_path, kg)
    surveyor.analyze_all()
    
    # 2. Hydrologist (Lineage)
    print("Phase 2: Hydrologist Analysis...")
    hydrologist = HydrologistAgent(target_path, kg)
    hydrologist.analyze_all()
    
    # 3. Semanticist (Purpose) - Requires GOOGLE_API_KEY
    print("Phase 3: Semantic Analysis...")
    semanticist = SemanticistAgent(kg)
    # For now, we only generate the brief for the core hubs
    surveyor_summary = f"Analyzed {len(kg.graph.nodes)} nodes. cycles: {len(kg.graph.graph.get('circular_dependencies', []))}"
    hydrologist_summary = f"Extracted data flows across Python and SQL."
    
    day_one_answers = semanticist.answer_day_one_questions(surveyor_summary, hydrologist_summary)
    
    # 4. Archivist (Artifacts)
    print("Phase 4: Generating Artifacts...")
    archivist = ArchivistAgent(kg, ".")
    hubs = [n for n, d in kg.graph.nodes(data=True) if d.get("node_type") == "module"]
    hubs.sort(key=lambda n: kg.graph.nodes[n].get("pagerank_score", 0), reverse=True)
    
    archivist.generate_CODEBASE_md(hubs)
    archivist.generate_onboarding_brief(day_one_answers)
    
    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python main.py <target_path>")
