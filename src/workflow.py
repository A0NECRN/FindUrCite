import json
from agents.student import StudentAgent
from agents.advisor import AdvisorAgent
from cache import AnalysisCache

class WorkflowOrchestrator:
    def __init__(self, model="qwen2.5:7b"):
        self.student = StudentAgent(model)
        self.advisor = AdvisorAgent(model)
        self.cache = AnalysisCache()

    def analyze_paper_with_debate(self, user_viewpoint, paper, full_text=None, callback=None):
        """
        Executes the debate.
        If callback is provided, it calls callback(event_dict).
        Event dict structure: {'role': 'student'|'advisor', 'content': '...', 'type': 'analysis'|'critique'|'approval'}
        """
        content_to_analyze = full_text if full_text else paper.get('abstract', '')
        if not content_to_analyze:
            return self._get_empty_analysis("No content available")

        cached = self.cache.get(user_viewpoint, content_to_analyze)
        if cached:
            if callback:
                callback({'role': 'system', 'content': f"Loaded cached analysis for {paper['title'][:30]}...", 'type': 'info'})
            return cached

        if callback:
            callback({'role': 'system', 'content': f"Starting analysis for: {paper['title']}", 'type': 'info'})

        # print(f"  [Debate] Initial analysis by Student...")
        analysis = self.student.analyze_initial(user_viewpoint, paper['title'], content_to_analyze)
        if callback:
            callback({'role': 'student', 'content': f"**[Student Analysis]**\n\n**Relevance Score:** {analysis.get('relevance_score')}/5\n\n**Why it matches:** {analysis.get('match_reasoning')}", 'type': 'analysis', 'data': analysis})
        
        # DYNAMIC DEBATE: Continue until consensus or max limit
        max_debate_rounds = 6
        
        for i in range(max_debate_rounds):
            # Advisor Review
            review = self.advisor.review_analysis(analysis, content_to_analyze)
            
            # Case 1: Approval
            if review.get('is_approved'):
                if callback:
                    callback({'role': 'advisor', 'content': "**[Advisor Decision]** ✅ Analysis Approved.", 'type': 'approval'})
                break # Consensus Reached: Accepted

            # Case 2: Check for Early Rejection Consensus
            # If both agree it's irrelevant (Score < 3)
            advisor_score = review.get('score_correction')
            student_score = analysis.get('relevance_score', 0)
            
            if advisor_score is not None and advisor_score < 3 and student_score < 3:
                 if callback:
                    callback({'role': 'advisor', 'content': "**[Advisor Decision]** ❌ Analysis Rejected (Consensus: Irrelevant).", 'type': 'rejection'})
                 break
            
            # Send Critique
            if callback:
                callback({'role': 'advisor', 'content': f"**[Advisor Critique (Round {i+1})]**\n\n{review.get('critique')}", 'type': 'critique'})
            
            # Check if we reached max rounds (fail to agree)
            if i == max_debate_rounds - 1:
                if callback:
                    callback({'role': 'system', 'content': "**[System]** Max debate rounds reached. Ending debate.", 'type': 'info'})
                break

            # Student Revision
            # Student decides whether to accept the critique and update the score
            analysis = self.student.revise_analysis(analysis, review.get('critique'), content_to_analyze)
            
            # Ensure score is within bounds (0-5)
            try:
                score = int(analysis.get('relevance_score', 0))
                analysis['relevance_score'] = max(0, min(5, score))
            except:
                analysis['relevance_score'] = 0

            if callback:
                defense = analysis.get('defense', 'I have updated the analysis.')
                callback({'role': 'student', 'content': f"**[Student Revision (Round {i+1})]**\n\n**Defense:** {defense}\n\n**New Score:** {analysis.get('relevance_score')}/5", 'type': 'revision', 'data': analysis})

            # Check for Rejection Consensus AFTER revision
            student_score = analysis.get('relevance_score', 0)
            if advisor_score is not None and advisor_score < 3 and student_score < 3:
                 if callback:
                    callback({'role': 'advisor', 'content': "**[Advisor Decision]** ❌ Analysis Rejected (Consensus: Irrelevant).", 'type': 'rejection'})
                 break

        self.cache.set(user_viewpoint, content_to_analyze, analysis)
        return analysis

    def perform_global_synthesis(self, user_viewpoint, analyzed_papers, callback=None):
        # print("  [Debate] Starting Global Synthesis Phase...")
        if callback:
            callback({'role': 'system', 'content': "Starting Global Synthesis Phase...", 'type': 'info'})
            
        if not analyzed_papers:
            return None
            
        # print("  [Debate] Student synthesizing literature...")
        synthesis = self.student.synthesize_literature(user_viewpoint, analyzed_papers)
        if callback:
            callback({'role': 'student', 'content': "**[Student Draft Synthesis]**\n\nI have synthesized the literature. \n\n**Gap Analysis:** " + synthesis.get('gap_analysis', 'N/A'), 'type': 'synthesis', 'data': synthesis})
        
        for i in range(2):
            # print(f"  [Debate] Synthesis Round {i+1}: Advisor reviewing...")
            review = self.advisor.review_synthesis(synthesis, analyzed_papers)
            
            if review.get('is_approved'):
                # print(f"  [Debate] Synthesis Approved.")
                if callback:
                    callback({'role': 'advisor', 'content': "**[Advisor Decision]** ✅ Synthesis Approved.", 'type': 'approval'})
                break
                
            if callback:
                callback({'role': 'advisor', 'content': f"**[Advisor Critique (Round {i+1})]**\n\n{review.get('critique')}", 'type': 'critique'})

            # print(f"  [Debate] Synthesis Round {i+1}: Student revising...")
            synthesis = self.student.synthesize_literature(user_viewpoint, analyzed_papers, synthesis, review.get('critique'))
            if callback:
                callback({'role': 'student', 'content': f"**[Student Revision (Round {i+1})]**\n\nUpdated synthesis based on feedback.", 'type': 'revision', 'data': synthesis})
            
        return synthesis

    def _get_empty_analysis(self, reason):
        return {
            "relevance_score": 0,
            "match_reasoning": reason,
            "sub_field": reason,
            "problem_def": reason,
            "methodology": reason,
            "method_keywords": reason,
            "algorithm_summary": reason,
            "experiments": reason,
            "limitations": reason,
            "critique": reason,
            "datasets": reason,
            "others": reason,
            "evidence_quotes": []
        }
