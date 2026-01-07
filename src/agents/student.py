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
        
        Task: Revise the analysis to address the critique.
        - You MUST output a 'defense' field explaining your response to the critique.
        - If the advisor points out that the paper is IRRELEVANT or lacks evidence, you MUST Lower the 'relevance_score' (e.g., to 1 or 2).
        - If the advisor demands more evidence and you find it, update 'evidence_quotes'.
        - Be honest: if you cannot defend the relevance, accept the advisor's view.
        - 'relevance_score' MUST be an integer between 0 and 5.
        
        Output the full updated JSON, including 'defense'.
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
        Analyze this research idea using Chain of Thought (CoT).
        
        Input: {text[:3000]}
        
        Step 1: Deconstruct the user's input. Identify the core problem, proposed solution, and key innovation claims.
        Step 2: Determine the specific sub-field and technical keywords.
        Step 3: Formulate a 'Key Viewpoint' that encapsulates the user's unique stance or contribution.
        Step 4: Generate search queries. 
           - IMPORTANT: All search queries MUST be in ENGLISH, regardless of the input language. ArXiv and Semantic Scholar require English queries.
           - Include 2 broad queries for context (in English).
           - Include 2 specific queries for direct methodology (in English).
           - Include 1 'negative' or distinct query to filter out unrelated fields (e.g. if 'financial LLM', exclude 'medical').
        
        Step 5: Extract 3-5 critical English keywords for filtering (e.g., "LLM", "Finance", "Transaction Cost").
        
        Constraint: Do NOT introduce unrelated concepts, specific languages (e.g. Arabic, Chinese), or domains unless explicitly mentioned in the input.
        
        Output JSON:
        {{
            "cot_reasoning": "Step-by-step reasoning...",
            "core_contribution": "Concise summary of the user's contribution...",
            "key_viewpoint": "A single sentence describing the unique angle...",
            "search_queries": ["query1", "query2", "query3", "query4", "query5"],
            "english_keywords": ["keyword1", "keyword2", "keyword3"]
        }}
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
            "key_viewpoint": text[:100],
            "english_keywords": []
        }

    def synthesize_literature(self, user_context, analyzed_papers, previous_synthesis=None, critique=None):
        papers_summary = []
        for p in analyzed_papers:
            # Include more details for synthesis
            papers_summary.append(f"- {p['paper']['title']}: {p['analysis'].get('problem_def', 'N/A')} | Method: {p['analysis'].get('methodology', 'N/A')}")
        
        papers_text = "\n".join(papers_summary)
        
        context_prompt = ""
        if previous_synthesis and critique:
            context_prompt = f"""
            Previous Synthesis: {json.dumps(previous_synthesis)}
            Advisor Critique: {critique}
            Task: Revise the synthesis to address the critique. Be more critical and specific.
            """
        else:
            context_prompt = "Task: Create a comprehensive literature synthesis. Focus on CONTRASTING the user's idea with existing work."

        prompt = f"""
        You are a research student. Synthesize the findings from these papers relative to the user's research idea.
        
        User Context: {user_context}
        Analyzed Papers:
        {papers_text}
        
        {context_prompt}
        
        Constraint: Strictly base your summary on the provided 'Analyzed Papers'. Do NOT hallucinate topics, languages (e.g. Arabic), or domains not present in the papers or user context.
        
        Output JSON:
        {{
            "state_of_art_summary": "Summary of what existing solutions do, highlighting their limitations...",
            "gap_analysis": "Precise analysis of why existing work fails to solve the user's specific problem...",
            "strategic_recommendations": "3-5 actionable suggestions (e.g. 'Adopt X metric from Paper A but apply it to Y domain')..."
        }}
        """
        
        response = self.chat([{'role': 'user', 'content': prompt}])
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return {
            "state_of_art_summary": "Failed to synthesize.",
            "gap_analysis": "N/A",
            "strategic_recommendations": "N/A"
        }
