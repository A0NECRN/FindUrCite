from .base import BaseAgent
import json

class AdvisorAgent(BaseAgent):
    def review_analysis(self, student_analysis, paper_content, debate_round=0):
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
        3. HALLUCINATION CHECK: If the student quotes text that is NOT in the fragment, REJECT immediately.
        4. SCORING CHECK: Review the multi-dimensional scores (0-10).
           - relevance: Is it strictly on topic?
           - innovation: Is the method novel?
           - reliability: Are experiments sound?
           - potential: Is it impactful?
        
        Constraint: 
        - If 'scores.relevance' > 6, you MUST demand at least 2 direct quotes as evidence.
        - If the methodology is vague, reject.
        - Be aggressive but fair. Do not let hallucinated details pass.
        - SCORE ADJUSTMENT: If you disagree with the student's score, you MUST provide a specific integer value in 'score_correction'.
          - If the paper is irrelevant, set 'score_correction' to < 4.
          - If the paper is good but over-hyped, set 'score_correction' to 6-7.
          - If the paper is a perfect match, confirm high score.
        - INTERROGATION (New):
          - If you are not satisfied, suspect the student is missing something, OR if the paper seems potentially relevant but lacks evidence, ASK QUESTIONS.
          - Do NOT just reject if a simple clarification could save the paper.
          - List specific questions in the 'questions' field that the student needs to answer (possibly by searching more).
        
        Output JSON:
        {{
            "is_approved": boolean,
            "critique": "Specific, harsh, evidence-based feedback focusing on {focus_instruction}...",
            "score_correction": int or null (If you disagree with the 'relevance' score, provide your corrected integer value 0-10. Otherwise null),
            "questions": ["Question 1", "Question 2"] (Optional: List of questions for the student to investigate further)
        }}
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        
        if response and isinstance(response, dict):
            return response
            
        return {"is_approved": False, "critique": "System Error: Advisor failed to generate valid critique (JSON parsing error or timeout)."}

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
        4. RIGOR: Are the claims backed by the papers?
        
        Output JSON:
        {{
            "is_approved": boolean,
            "critique": "Constructive but strict feedback..."
        }}
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        
        if response and isinstance(response, dict):
            return response
            
        return {"is_approved": False, "critique": "System Error: Synthesis review failed."}
