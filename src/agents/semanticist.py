import os
from google import genai
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Callable
from src.models.nodes import ModuleNode
from src.models.schemas import TraceEvent
from src.graph.knowledge_graph import KnowledgeGraph
from src.analyzers.git_history import GitVelocitySnapshot
from dotenv import load_dotenv

load_dotenv()

class SemanticistAgent:
    """
    Uses LLMs to generate semantic understanding of code.
    Generates purpose statements and identifies business domains.
    """
    
    def __init__(self, kg: KnowledgeGraph | None = None, api_key: Optional[str] = None):
        self.kg = kg or KnowledgeGraph()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'models/gemini-pro-latest'
        else:
            self.client = None

    def run(
        self, 
        repo_path: Path, 
        modules: dict[str, ModuleNode],
        progress_callback: Callable[[str], None] | None = None
    ) -> tuple[dict[str, ModuleNode], list[TraceEvent]]:
        """
        Enriches modules with semantic purpose statements.
        """
        trace: list[TraceEvent] = []
        
        # Sort modules by PageRank (or just process all)
        # For efficiency in large repos like networkx, we might focus on hubs
        sorted_modules = sorted(
            modules.values(), 
            key=lambda m: getattr(m, 'pagerank_score', 0), 
            reverse=True
        )
        
        # Limit to top 50 for large repos during verification if LLM is expensive,
        # but here we follow the full process unless it's too much.
        # Let's say top 20 for core understanding.
        targets = sorted_modules[:20]
        
        for i, mod in enumerate(targets):
            if progress_callback:
                progress_callback(f"Semanticist distilling ({i+1}/{len(targets)}): {mod.path}")
            
            full_path = repo_path / mod.path
            if full_path.exists():
                code = full_path.read_text(errors="ignore")
                self.generate_purpose_statement(mod, code)
        
        trace.append(TraceEvent(
            agent="semanticist",
            action="semantic_enrichment_complete",
            evidence={"modules_enriched": len(targets)},
            confidence="high"
        ))
        
        return modules, trace

    def generate_purpose_statement(self, module_node: ModuleNode, code_content: str) -> str:
        """
        Prompts the LLM to explain the business purpose of a module.
        """
        if not self.client:
            return "LLM Not Configured"
        
        prompt = f"""
        Analyze the following code from file '{module_node.path}' and provide a 2-3 sentence purpose statement.
        Explain the business function and role in the system, not the implementation details.
        
        CODE:
        {code_content[:8000]}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            purpose = response.text.strip()
            module_node.purpose_statement = purpose
            if f"mod:{module_node.path}" in self.kg.graph:
                self.kg.graph.nodes[f"mod:{module_node.path}"]["purpose_statement"] = purpose
            return purpose
        except Exception as e:
            return f"Error generating purpose: {e}"

    def answer_day_one_questions(
        self, 
        modules: list[ModuleNode],
        top_modules: list[str],
        sources: list[str],
        sinks: list[str],
        downstream_map: dict[str, list[str]],
        module_graph: KnowledgeGraph,
        lineage_graph: KnowledgeGraph,
        git_velocity_snapshot: GitVelocitySnapshot | None = None
    ) -> str:
        """
        Synthesizes all analysis into the FDE Day-One Brief using the full structural context.
        """
        if not self.client:
            return "LLM Not Configured: Ingestion summary available but reasoning is limited."
            
        # Build a rich context for the LLM
        context = f"Analyzed {len(modules)} modules.\n"
        context += f"Top Hubs (by dependency PageRank): {', '.join(top_modules)}\n"
        context += f"Data Entry Points (Sources): {len(sources)}\n"
        context += f"Data Exit Points (Sinks): {len(sinks)}\n"
        
        if git_velocity_snapshot:
            context += f"Git History status: {git_velocity_snapshot.history_status}\n"
            top_changed = sorted(git_velocity_snapshot.files, key=lambda x: x.commit_count, reverse=True)[:5]
            if top_changed:
                context += "High Velocity Files (90d):\n"
                for meta in top_changed:
                    context += f"  - {meta.path}: {meta.commit_count} commits\n"

        prompt = f"""
        You are a Senior Forward Deployed Engineer (FDE) at Palantir. 
        You just ran 'The Brownfield Cartographer' on a new codebase.
        
        TECHNICAL CONTEXT:
        {context}
        
        Based on this, answer the Five Day-One Questions:
        1. What is the primary data ingestion path? (Analyze sources/sinks)
        2. What are the 3-5 most critical output datasets/endpoints?
        3. What is the blast radius if a core hub fails? (Consider the downstream map)
        4. Where is the business logic concentrated vs. distributed?
        5. What has changed most frequently in the last 90 days?
        
        Format as a professional, concise markdown brief. 
        Focus on providing actionable intelligence for an engineer joining the project TODAY.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating brief: {e}"
        except Exception as e:
            return f"Error generating brief: {e}"

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    # Mocking a module node for testing
    mod = ModuleNode(path="src/meltano/core/project.py", language="python")
    agent = SemanticistAgent(kg)
    if agent.client:
        print("Model configured. Ready for semantic analysis.")
    else:
        print("GEMINI_API_KEY not found. Skipping live LLM test.")
