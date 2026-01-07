from .base import BaseAgent
import json

class AdvisorAgent(BaseAgent):
    def review_analysis(self, student_analysis, paper_content, debate_round=0):
        # Determine focus based on round and score
        # Handle nested scores dict or top-level field
        current_score = 0
        if 'scores' in student_analysis and isinstance(student_analysis['scores'], dict):
            current_score = student_analysis['scores'].get('relevance', 0)
        else:
            current_score = student_analysis.get('relevance_score', 0)
            
        focus_instruction = ""
        if debate_round == 0:
            focus_instruction = "Phase 1: INITIAL SCREENING. Focus strictly on RELEVANCE and METHODOLOGY SOUNDNESS. Is this paper actually addressing the user's problem? Does the method make sense?"
        elif current_score > 7:
            focus_instruction = "Phase 2: DEEP INTERROGATION. The paper claims high relevance. DEMAND EVIDENCE. Check for overclaimed innovation. Scrutinize the experiments. Ensure 'evidence_quotes' are sufficient."
        else:
            focus_instruction = "Phase 2: CRITICAL REVIEW. Look for fatal flaws, missed limitations, or reasons to reject. Verify if the 'match_reasoning' is logical."

        prompt = f"""
        You are a highly critical, top-tier conference reviewer (e.g. NeurIPS, ICML).
        Current Debate Round: {debate_round + 1}
        Focus: {focus_instruction}
        
        Student Analysis: {json.dumps(student_analysis)}
        Paper Content Fragment: {paper_content[:10000]}
        
        Task:
        1. EVIDENCE CHECK: Verify if every claim in 'problem_def' and 'methodology' is supported by the text.
        2. RELEVANCE CHECK: Does this paper TRULY address the user's core problem?
        3. SCORING CHECK: Review the multi-dimensional scores (0-10).
           - relevance: Is it strictly on topic?
           - innovation: Is the method novel?
           - reliability: Are experiments sound?
           - potential: Is it impactful?
        
        Constraint: 
        - If 'scores.relevance' > 6, you MUST demand at least 2 direct quotes as evidence.
        - If the methodology is vague, reject.
        - Be aggressive but fair.
        
        Output JSON:
        {{
            "is_approved": boolean,
            "critique": "Specific, harsh, evidence-based feedback focusing on {focus_instruction}...",
            "score_correction": int or null (If you disagree with the 'relevance' score, provide your corrected integer value 0-10. Otherwise null)
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
