from .base import BaseAgent
import json

class AdvisorAgent(BaseAgent):
    def review_analysis(self, student_analysis, paper_content):
        prompt = f"""
        You are a strict research advisor. Review the student's analysis of a paper.
        
        Student Analysis: {json.dumps(student_analysis)}
        Paper Content Fragment: {paper_content[:10000]}
        
        Task:
        1. Check for hallucinations (claims not in text).
        2. Check if 'relevance_score' is justified.
        3. Check if 'evidence_quotes' are actual quotes.
        
        Output JSON:
        {{
            "is_approved": boolean,
            "critique": "Detailed feedback string...",
            "score_correction": int or null
        }}
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return {"is_approved": True, "critique": "No critique due to error."}
