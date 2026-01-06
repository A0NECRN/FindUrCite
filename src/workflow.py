import json
from agents.student import StudentAgent
from agents.advisor import AdvisorAgent
from cache import AnalysisCache

class WorkflowOrchestrator:
    def __init__(self, model="qwen2.5:7b"):
        self.student = StudentAgent(model)
        self.advisor = AdvisorAgent(model)
        self.cache = AnalysisCache()

    def analyze_paper_with_debate(self, user_viewpoint, paper, full_text=None):
        content_to_analyze = full_text if full_text else paper.get('abstract', '')
        if not content_to_analyze:
            return self._get_empty_analysis("No content available")

        cached = self.cache.get(user_viewpoint, content_to_analyze)
        if cached:
            return cached

        print(f"  [Debate] Initial analysis by Student...")
        analysis = self.student.analyze_initial(user_viewpoint, paper['title'], content_to_analyze)
        
        for i in range(2):
            print(f"  [Debate] Round {i+1}: Advisor reviewing...")
            review = self.advisor.review_analysis(analysis, content_to_analyze)
            
            if review.get('is_approved'):
                print(f"  [Debate] Advisor approved.")
                break
            
            print(f"  [Debate] Round {i+1}: Student revising based on critique...")
            analysis = self.student.revise_analysis(analysis, review.get('critique'), content_to_analyze)
            if review.get('score_correction') is not None:
                analysis['relevance_score'] = review.get('score_correction')

        self.cache.set(user_viewpoint, content_to_analyze, analysis)
        return analysis

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
