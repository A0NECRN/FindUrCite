import json
from .base import BaseAgent

class StudentAgent(BaseAgent):
    def analyze_initial(self, user_context, paper_title, paper_content):
        truncated_text = paper_content[:30000]
        
        prompt = f"""
        You are a research student. Analyze this paper based on the user's research context.
        
        Context: {user_context}
        Paper: {paper_title}
        Content: {truncated_text}
        ...
        
        Task: Perform a deep analysis. Extract all required fields.
        Evaluate the paper on multiple dimensions (Scale: 0-10).
        
        Output JSON only.
        
        Required Fields:
        - scores: {{
            "relevance": (0-10) How strictly it addresses the user's core problem,
            "innovation": (0-10) Novelty of the proposed method,
            "reliability": (0-10) Experimental rigor and reproducibility,
            "potential": (0-10) Value for future work or application,
            "total": (0-10) Overall weighted score
        }}
        - match_reasoning: Detailed explanation of the scores.
        - sub_field
        - problem_def
        - methodology
        - method_keywords
        - algorithm_summary
        - experiments
        - limitations
        - critique
        - datasets
        - others
        - evidence_quotes: [List of direct quotes supporting your analysis]
        
        Constraint:
        - "relevance" is the most important. If < 5, the paper is likely useless.
        - Be critical. 9-10 is reserved for seminal works.
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response and isinstance(response, dict):
            return response
        
        print(f"[StudentAgent] Analyze Initial Failed. Response type: {type(response)}")
        return {}

    def revise_analysis(self, original_analysis, advisor_critique, paper_content, new_evidence=None):
        evidence_text = ""
        if new_evidence:
            evidence_text = f"\nNew Evidence from Search:\n{new_evidence}\n"
            
        prompt = f"""
        You are a research student. Your advisor has critiqued your initial analysis and asked questions.
        
        Original Analysis: {json.dumps(original_analysis)}
        Advisor Critique: {advisor_critique}
        {evidence_text}
        Paper Content Fragment: {paper_content[:10000]}
        
        Task: Revise the analysis to address the critique and new evidence.
        Step 1: REFLECTION. Think deeply about the critique and any new findings.
        Step 2: REVISION. Update the fields based on your reflection.
        
        Guidelines:
        - You MUST output a 'defense' field explaining your response to the critique and how new evidence supports/refutes it.
        - If the advisor points out that the paper is IRRELEVANT or lacks evidence, you MUST Lower the 'scores.relevance' (e.g., to 2 or 3).
        - Update other scores ('innovation', 'reliability', 'potential') if needed.
        - Recalculate 'scores.total'.
        - If the advisor demands more evidence and you find it, update 'evidence_quotes'.
        - Be honest: if you cannot defend the relevance, accept the advisor's view.
        - All scores MUST be integers between 0 and 10.
        
        Output the full updated JSON, including 'defense' and the 'scores' object.
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response and isinstance(response, dict):
            return response
            
        print(f"[StudentAgent] Revise Analysis Failed. Response type: {type(response)}")
        return original_analysis

    def generate_investigation_queries(self, advisor_questions, context):
        prompt = f"""
        You are a research student. Your advisor has asked challenging questions about your analysis.
        You need to search for external evidence to answer them.
        
        Context: {context}
        Advisor Questions: {advisor_questions}
        
        Task: Generate 3 specific search queries to find answers or evidence.
        
        Output JSON:
        {{
            "queries": ["query 1", "query 2", "query 3"]
        }}
        """
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response and isinstance(response, dict):
            return response.get('queries', [])
        return []

    def analyze_user_input(self, text):
        prompt = f"""
        Analyze this research idea using Chain of Thought (CoT).
        
        Input: {text[:3000]}
        
        Step 1: Deconstruct the user's input. Identify the core problem, proposed solution, and key innovation claims.
        Step 2: Determine the specific sub-field and technical keywords.
        Step 3: Formulate a 'Key Viewpoint' that encapsulates the user's unique stance or contribution.
        Step 4: Generate a comprehensive search strategy using multiple methods:
           - Keyword Extraction: Extract 5-10 precise technical keywords (e.g., "Transformer", "Contrastive Learning").
           - Boolean Combinations: Create 3 complex boolean queries (e.g., "('Large Language Model' OR 'LLM') AND 'Hallucination'").
           - Semantic Queries: Create 3 natural language questions a researcher would ask.
           - Exact Match: Identify any specific phrases that should be searched in quotes.

           - IMPORTANT: All search queries MUST be in ENGLISH, regardless of the input language.
        
        Output JSON only.
        
        Required Fields:
        - core_contribution: Summary of the user's idea.
        - sub_field: The academic sub-field.
        - key_viewpoint: The angle to evaluate papers against.
        - search_queries: [List of all generated queries combined]
        - english_keywords: [List of English keywords for filtering]
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response and isinstance(response, dict):
            return response
            
        return {
            "core_contribution": "Analysis failed",
            "search_queries": [text],
            "english_keywords": []
        }
