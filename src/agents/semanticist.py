import os
import google.generativeai as genai
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from src.models.nodes import ModuleNode
from src.graph.knowledge_graph import KnowledgeGraph

class SemanticistAgent:
    """
    Uses LLMs to generate semantic understanding of code.
    Generates purpose statements and identifies business domains.
    """
    
    def __init__(self, kg: KnowledgeGraph, api_key: Optional[str] = None):
        self.kg = kg
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def generate_purpose_statement(self, module_node: ModuleNode, code_content: str) -> str:
        """
        Prompts the LLM to explain the business purpose of a module.
        """
        if not self.model:
            return "LLM Not Configured"
        
        prompt = f"""
        Analyze the following code from file '{module_node.path}' and provide a 2-3 sentence purpose statement.
        Explain the business function and role in the system, not the implementation details.
        
        CODE:
        {code_content[:4000]}
        """
        
        try:
            response = self.model.generate_content(prompt)
            purpose = response.text.strip()
            module_node.purpose_statement = purpose
            self.kg.graph.nodes[f"mod:{module_node.path}"]["purpose_statement"] = purpose
            return purpose
        except Exception as e:
            return f"Error generating purpose: {e}"

    def answer_day_one_questions(self, surveyor_summary: str, hydrologist_summary: str) -> str:
        """
        Synthesizes all analysis into the FDE Day-One Brief.
        """
        if not self.model:
            return "LLM Not Configured"
            
        prompt = f"""
        You are a Senior Forward Deployed Engineer (FDE). 
        Based on the technical analysis summaries below, answer the Five Day-One Questions:
        1. What is the primary data ingestion path?
        2. What are the 3-5 most critical output datasets/endpoints?
        3. What is the blast radius if the most critical module fails?
        4. Where is the business logic concentrated vs. distributed?
        5. What has changed most frequently in the last 90 days?
        
        SURVEYOR SUMMARY:
        {surveyor_summary}
        
        HYDROLOGIST SUMMARY:
        {hydrologist_summary}
        
        Format as a professional markdown brief.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating brief: {e}"

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    # Mocking a module node for testing
    mod = ModuleNode(path="src/meltano/core/project.py", language="python")
    agent = SemanticistAgent(kg)
    if agent.model:
        print("Model configured. Ready for semantic analysis.")
    else:
        print("GOOGLE_API_KEY not found. Skipping live LLM test.")
