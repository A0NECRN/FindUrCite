from .base import BaseAgent
import json

class AdvisorAgent(BaseAgent):
    def review_analysis(self, student_analysis, paper_content):
        prompt = f"""
        You are a highly critical, top-tier conference reviewer (e.g. NeurIPS, ICML).
        
        Student Analysis: {json.dumps(student_analysis)}
        Paper Content Fragment: {paper_content[:10000]}
        
        Task:
        1. EVIDENCE CHECK: Verify if every claim in 'problem_def' and 'methodology' is supported by the text. If not, reject.
        2. RELEVANCE CHECK: Does this paper TRULY address the user's core problem? If it's only tangentially related, downgrade the score severely.
        3. HALLUCINATION CHECK: Ensure 'evidence_quotes' exist in the fragment.
        
        Constraint: 
        - If relevance_score > 3, you MUST demand at least 2 direct quotes as evidence.
        - If the methodology is vague, reject.
        
        Output JSON:
        {{
            "is_approved": boolean,
            "critique": "Specific, harsh, evidence-based feedback...",
            "score_correction": int or null (Force 1 or 2 if irrelevant)
        }}
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return {"is_approved": True, "critique": "No critique due to error."}

    def review_synthesis(self, synthesis, analyzed_papers):
        papers_summary = []
        for p in analyzed_papers:
            papers_summary.append(f"- {p['paper']['title']}")
            
        papers_text = "\n".join(papers_summary)
        
        prompt = f"""
        You are a research advisor. Review the student's literature synthesis.
        
        Student Synthesis: {json.dumps(synthesis)}
        Available Papers:
        {papers_text}
        
        Task:
        1. CRITICAL REVIEW: Does the 'gap_analysis' identify a REAL gap, or just a trivial one?
        2. ACTIONABILITY: Are 'strategic_recommendations' specific enough to implement? (e.g. 'Use Transformer' is bad; 'Use LoRA with rank 16 on Llama 3' is good).
        3. COVERAGE: Did the student miss any major paper from the list?
        
        Output JSON:
        {{
            "is_approved": boolean,
            "critique": "Constructive but strict feedback..."
        }}
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return {"is_approved": True, "critique": "No critique."}
