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
            
    def _get_empty_analysis(self, reason):
        return {
            'scores': {'relevance': 0, 'total': 0},
            'relevance_score': 0,
            'match_reasoning': reason
        }

    def analyze_paper_with_debate(self, user_viewpoint, paper, full_text=None, callback=None, searcher=None):
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

        analysis = self.student.analyze_initial(user_viewpoint, paper['title'], content_to_analyze)
        
        if 'scores' in analysis and isinstance(analysis['scores'], dict):
            analysis['relevance_score'] = self._normalize_score(analysis['scores'].get('relevance', 0))
        else:
            analysis['scores'] = {
                'relevance': self._normalize_score(analysis.get('relevance_score', 0)),
                'total': self._normalize_score(analysis.get('relevance_score', 0))
            }
            analysis['relevance_score'] = analysis['scores']['relevance']
        
        analysis['relevance_score'] = self._normalize_score(analysis.get('relevance_score', 0))
        
        if callback:
            scores_display = "\n".join([f"- **{k.title()}**: {v}/10" for k, v in analysis.get('scores', {}).items()])
            callback({'role': 'student', 'content': f"**[Student Analysis]**\n\n**Scores (0-10):**\n{scores_display}\n\n**Why it matches:** {analysis.get('match_reasoning')}", 'type': 'analysis', 'data': analysis})
        
        max_debate_rounds = 6
        
        for i in range(max_debate_rounds):
            review = self.advisor.review_analysis(analysis, content_to_analyze, debate_round=i)
            
            if review.get('is_approved'):
                if callback:
                    callback({'role': 'advisor', 'content': "**[Advisor Decision]** ✅ Analysis Approved.", 'type': 'approval'})
                break # Consensus Reached: Accepted

            advisor_score_val = review.get('score_correction')
            advisor_score = self._normalize_score(advisor_score_val) if advisor_score_val is not None else None
            
            # Apply Advisor's Score Correction if provided
            if advisor_score is not None:
                analysis['relevance_score'] = advisor_score
                if 'scores' not in analysis: analysis['scores'] = {}
                analysis['scores']['relevance'] = advisor_score
                # Recalculate total if possible (simplified: just update total to match relevance or avg)
                analysis['scores']['total'] = advisor_score 

            rejection_threshold = 5 
            
            # Check for Interrogation Questions
            questions = review.get('questions', [])

            if advisor_score is not None:
                # If score is low AND no questions, reject immediately
                if advisor_score < rejection_threshold and not questions:
                     if callback:
                        callback({'role': 'advisor', 'content': f"**[Advisor Decision]** ❌ Analysis Rejected (Score Corrected to {advisor_score}).", 'type': 'rejection'})
                     break
                # If score is low BUT there are questions, allow the debate to continue (Interrogation)
                elif advisor_score < rejection_threshold and questions:
                    pass # Continue to interrogation logic below

            new_evidence = None
            
            if questions:
                q_list_str = "\n".join([f"- {q}" for q in questions])
                if callback:
                     callback({'role': 'advisor', 'content': f"**[Advisor Critique (Round {i+1})]**\n\n{review.get('critique')}\n\n**❓ Interrogation:**\n{q_list_str}", 'type': 'critique'})
                
                if searcher:
                    # Student generates queries
                    queries = self.student.generate_investigation_queries(questions, analysis)
                    if queries:
                        if callback:
                            callback({'role': 'student', 'content': f"**[Investigation]** Searching for evidence to answer advisor's doubts...\nQueries: {queries}", 'type': 'info'})
                        
                        # Execute Search
                        # Use a simpler search method or reuse search_multiple_queries
                        # We limit to 2 results per query to avoid overwhelming context
                        search_results = searcher.search_multiple_queries(queries, limit_per_source=2)
                        
                        if search_results:
                            evidence_texts = []
                            for res in search_results:
                                snippet = res.get('abstract', '') or res.get('snippet', '')
                                evidence_texts.append(f"Source: {res['title']}\nSnippet: {snippet[:500]}...")
                            new_evidence = "\n".join(evidence_texts)
                            if callback:
                                callback({'role': 'system', 'content': f"Found {len(search_results)} supporting documents.", 'type': 'info'})
            else:
                 if callback:
                    callback({'role': 'advisor', 'content': f"**[Advisor Critique (Round {i+1})]**\n\n{review.get('critique')}", 'type': 'critique'})

            # Student Revision
            analysis = self.student.revise_analysis(analysis, review.get('critique'), content_to_analyze, new_evidence=new_evidence)
            
            # Update score after revision
            if 'scores' in analysis and isinstance(analysis['scores'], dict):
                 analysis['relevance_score'] = self._normalize_score(analysis['scores'].get('relevance', 0))
            
            if callback:
                scores_display = "\n".join([f"- **{k.title()}**: {v}/10" for k, v in analysis.get('scores', {}).items()])
                callback({'role': 'student', 'content': f"**[Student Revision]**\n\n{analysis.get('defense')}\n\n**Updated Scores:**\n{scores_display}", 'type': 'analysis', 'data': analysis})

            if i == max_debate_rounds - 1:
                if callback:
                    callback({'role': 'system', 'content': "**[System]** Max debate rounds reached. Ending debate.", 'type': 'info'})
                break
        
        self.cache.set(user_viewpoint, content_to_analyze, analysis)
        
        # Ensure critique is preserved in analysis for UI
        if 'critique' not in analysis and review.get('critique'):
            analysis['critique'] = review.get('critique')
            
        return analysis

    def perform_global_synthesis(self, user_query, analyzed_results, callback=None):
        """
        Generates a final research report based on all analyzed papers.
        """
        if not analyzed_results:
            return {
                "state_of_art_summary": "No relevant papers found.",
                "gap_analysis": "N/A",
                "strategic_recommendations": "Try broadening your search query."
            }
            
        if callback:
            callback({'type': 'status', 'content': 'Generating Global Synthesis...'})
            
        # Prepare context from accepted papers
        accepted_papers = [r for r in analyzed_results if r.get('analysis', {}).get('relevance_score', 0) >= 4]
        
        # If too few accepted, include top rejected ones to have something to say
        if len(accepted_papers) < 3:
             # Sort by score desc
             sorted_all = sorted(analyzed_results, key=lambda x: x.get('analysis', {}).get('relevance_score', 0), reverse=True)
             accepted_papers = sorted_all[:5]
             
        context_text = ""
        for item in accepted_papers:
            p = item['paper']
            a = item.get('analysis', {})
            context_text += f"Title: {p['title']}\nYear: {p.get('year')}\nKey Contribution: {a.get('match_reasoning')}\nCritique: {a.get('critique')}\n\n"
            
        prompt = f"""
        You are a Principal Investigator (PI) summarizing a research session.
        User Research Topic: "{user_query}"
        
        Analyzed Papers Context:
        {context_text[:15000]} # Limit context window
        
        Task: Write a high-level executive summary.
        Output JSON format:
        {{
            "state_of_art_summary": "Summary of what has been done...",
            "gap_analysis": "What is missing or under-explored...",
            "strategic_recommendations": "3-5 concrete next steps for the researcher..."
        }}
        """
        
        response = self.student.chat([{'role': 'user', 'content': prompt}])
        
        if response and isinstance(response, dict):
            return response
            
        # Fallback
        return {
            "state_of_art_summary": "Failed to generate synthesis.",
            "gap_analysis": "N/A",
            "strategic_recommendations": "N/A"
        }
