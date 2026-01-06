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
        Output JSON only.
        
        Required Fields:
        relevance_score, match_reasoning, sub_field, problem_def, methodology, 
        method_keywords, algorithm_summary, experiments, limitations, critique, 
        datasets, others, evidence_quotes
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return {}

    def revise_analysis(self, original_analysis, advisor_critique, paper_content):
        prompt = f"""
        You are a research student. Your advisor has critiqued your initial analysis.
        
        Original Analysis: {json.dumps(original_analysis)}
        Advisor Critique: {advisor_critique}
        Paper Content Fragment: {paper_content[:10000]}
        
        Task: Revise the analysis to address the critique. Fix hallucinations. Add missing evidence.
        Output the full updated JSON.
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return original_analysis

    def analyze_user_input(self, text):
        prompt = f"""
        Analyze this research idea.
        Input: {text[:2000]}
        
        Output JSON:
        core_contribution, search_queries (list of 3 strings), key_viewpoint
        """
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return {
            "core_contribution": text[:100],
            "search_queries": [text[:50]],
            "key_viewpoint": text[:100]
        }
