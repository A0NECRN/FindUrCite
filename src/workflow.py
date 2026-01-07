import json
from agents.student import StudentAgent
from agents.advisor import AdvisorAgent
from cache import AnalysisCache

class WorkflowOrchestrator:
    def __init__(self, model="qwen2.5:7b"):
        self.student = StudentAgent(model)
        self.advisor = AdvisorAgent(model)
        self.cache = AnalysisCache()

    def _normalize_score(self, score_val):
        # Handle dict input (if someone passes the full scores object)
        if isinstance(score_val, dict):
            if 'relevance' in score_val:
                score_val = score_val['relevance']
            elif 'total' in score_val:
                score_val = score_val['total']
            else:
                return 0
        
        try:
            val = float(score_val)
            return max(0, min(10, val))
        except (ValueError, TypeError):
            return 0

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
        
        # Post-process analysis to ensure compatibility
        if 'scores' in analysis and isinstance(analysis['scores'], dict):
            # Map relevance score to top level for compatibility
            analysis['relevance_score'] = self._normalize_score(analysis['scores'].get('relevance', 0))
        else:
            # Fallback if student agent failed to follow new format
            analysis['scores'] = {
                'relevance': self._normalize_score(analysis.get('relevance_score', 0)),
                'total': self._normalize_score(analysis.get('relevance_score', 0))
            }
            analysis['relevance_score'] = analysis['scores']['relevance']
        
        # Initial Score Clamping
        analysis['relevance_score'] = self._normalize_score(analysis.get('relevance_score', 0))
        
        if callback:
            scores_display = "\n".join([f"- **{k.title()}**: {v}/10" for k, v in analysis.get('scores', {}).items()])
            callback({'role': 'student', 'content': f"**[Student Analysis]**\n\n**Scores (0-10):**\n{scores_display}\n\n**Why it matches:** {analysis.get('match_reasoning')}", 'type': 'analysis', 'data': analysis})
        
        # DYNAMIC DEBATE: Continue until consensus or max limit
        max_debate_rounds = 6
        
        for i in range(max_debate_rounds):
            # Advisor Review
            review = self.advisor.review_analysis(analysis, content_to_analyze, debate_round=i)
            
            # Case 1: Approval
            if review.get('is_approved'):
                if callback:
                    callback({'role': 'advisor', 'content': "**[Advisor Decision]** ✅ Analysis Approved.", 'type': 'approval'})
                break # Consensus Reached: Accepted

            # Case 2: Check for Early Rejection Consensus
            # If both agree it's irrelevant (Score < 5, threshold increased for 10-scale)
            advisor_score_val = review.get('score_correction')
            advisor_score = self._normalize_score(advisor_score_val) if advisor_score_val is not None else None
            
            student_score = self._normalize_score(analysis.get('relevance_score', 0))
            
            # Rejection Threshold: 5/10 (equivalent to 2.5/5)
            rejection_threshold = 5 
            
            if advisor_score is not None:
                if advisor_score < rejection_threshold and student_score < rejection_threshold:
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
            
            # Sync scores again
            if 'scores' in analysis and isinstance(analysis['scores'], dict):
                analysis['relevance_score'] = self._normalize_score(analysis['scores'].get('relevance', 0))
            else:
                # Fallback
                 analysis['scores'] = {
                    'relevance': self._normalize_score(analysis.get('relevance_score', 0)),
                    'total': self._normalize_score(analysis.get('relevance_score', 0))
                }

            # Ensure score is within bounds (0-10)
            analysis['relevance_score'] = self._normalize_score(analysis.get('relevance_score', 0))

            if callback:
                defense = analysis.get('defense', 'I have updated the analysis.')
                scores_display = "\n".join([f"- **{k.title()}**: {v}/10" for k, v in analysis.get('scores', {}).items()])
                callback({'role': 'student', 'content': f"**[Student Revision (Round {i+1})]**\n\n**Defense:** {defense}\n\n**New Scores:**\n{scores_display}", 'type': 'revision', 'data': analysis})

            # Check for Rejection Consensus AFTER revision
            student_score = self._normalize_score(analysis.get('relevance_score', 0))
            if advisor_score is not None:
                if advisor_score < rejection_threshold and student_score < rejection_threshold:
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
            "scores": {"relevance": 0, "total": 0},
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
