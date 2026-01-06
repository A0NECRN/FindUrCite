import ollama
import json
from cache import AnalysisCache

class Analyzer:
    def __init__(self, model="qwen2.5:7b"):
        self.model = model
        self.cache = AnalysisCache()

    def analyze_user_input(self, text):
        prompt = f"""
        You are a research assistant. The user has provided a draft text or a description of their research.
        
        Input Text:
        "{text[:2000]}..." (truncated if too long)
        
        Your task:
        1. Summarize the **Core Contribution** or **Main Idea** of this text (1 sentence).
        2. Generate 3 **Distinct Search Queries** (strings) to find relevant academic papers:
           - Query 1: Broad topic keywords.
           - Query 2: Specific problem/method keywords.
           - Query 3: Alternative terminology or related sub-field keywords.
        3. Identify the **Key Viewpoint** or **Research Question** that needs citation support.
        
        Output JSON only:
        {{
            "core_contribution": "...",
            "search_queries": ["query1", "query2", "query3"],
            "key_viewpoint": "..."
        }}
        """
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ], format='json')
            content = response['message']['content']
            return json.loads(content)
        except Exception as e:
            print(f"[Analyzer] Input Analysis Error: {e}")
            return {
                "core_contribution": text[:100],
                "search_queries": [text[:50]],
                "key_viewpoint": text[:100]
            }

    def analyze_with_debate(self, user_viewpoint, paper, full_text):
        print(f"[Analyzer] Starting Multi-Agent Debate for: {paper.get('title', '')[:30]}...")
        
        initial_analysis = self._run_student_analysis(user_viewpoint, paper, full_text)
        
        critique = self._run_mentor_critique(user_viewpoint, paper, full_text, initial_analysis)
        
        if critique.get("status") == "PASS":
            print("[Analyzer] Mentor passed the analysis.")
            return initial_analysis
        else:
            print("[Analyzer] Mentor requested revision. Improving analysis...")
            final_analysis = self._run_student_revision(user_viewpoint, paper, full_text, initial_analysis, critique)
            return final_analysis

    def _run_student_analysis(self, user_viewpoint, paper, full_text):
        truncated_text = full_text[:30000]
        prompt = f"""
        You are a meticulous academic researcher (Student Agent). Analyze the paper text.
        
        User Context: {user_viewpoint}
        Paper Title: {paper.get('title')}
        Content: {truncated_text}...
        
        Task: Extract rigorous details. NO HALLUCINATIONS.
        
        REQUIRED JSON OUTPUT:
        {{
            "relevance_score": 1-5,
            "match_reasoning": "Why it fits/doesn't fit",
            "sub_field": "Sub-field",
            "problem_def": "Problem & Math Def",
            "methodology": "Method & Bottleneck solved",
            "method_keywords": "Keywords",
            "algorithm_summary": "Pseudocode/Flow",
            "experiments": "Datasets, Baselines, Results",
            "limitations": "Flaws/Limitations",
            "critique": "Your evaluation",
            "datasets": "Specific datasets",
            "others": "Notes",
            "evidence_quotes": ["Quote 1", "Quote 2"]
        }}
        """
        return self._call_llm(prompt)

    def _run_mentor_critique(self, user_viewpoint, paper, full_text, student_analysis):
        truncated_text = full_text[:10000] 
        analysis_str = json.dumps(student_analysis, indent=2)
        prompt = f"""
        You are a Senior Professor (Mentor Agent). Critique the Student's analysis of the paper.
        
        Paper Title: {paper.get('title')}
        Paper Excerpt: {truncated_text}...
        Student Analysis:
        {analysis_str}
        
        Check for:
        1. Hallucinations (claims not in text).
        2. Vague descriptions (e.g., "improved performance" without numbers).
        3. Missing evidence quotes.
        4. Alignment with User Context: {user_viewpoint}
        
        Output JSON:
        {{
            "status": "PASS" or "FAIL",
            "critique_points": "List of specific issues to fix",
            "guidance": "Instructions for revision"
        }}
        """
        return self._call_llm(prompt)

    def _run_student_revision(self, user_viewpoint, paper, full_text, previous_analysis, mentor_critique):
        truncated_text = full_text[:30000]
        prompt = f"""
        You are the Student Agent. The Professor rejected your previous analysis.
        
        Professor's Critique: {mentor_critique.get('critique_points')}
        Guidance: {mentor_critique.get('guidance')}
        
        Previous Analysis: {json.dumps(previous_analysis)}
        
        Paper Content: {truncated_text}...
        
        Task: Re-analyze the paper and FIX the issues. Ensure rigorous evidence.
        Output the complete corrected JSON (same format as before).
        """
        return self._call_llm(prompt)

    def _call_llm(self, prompt):
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ], format='json')
            return json.loads(response['message']['content'])
        except Exception as e:
            print(f"[Analyzer] LLM Call Error: {e}")
            return {}

    def analyze_paper_details(self, user_viewpoint, paper):
        abstract = paper.get('abstract', '')
        if not abstract:
            return self._get_empty_analysis("No abstract available")

        cached_result = self.cache.get(user_viewpoint, abstract)
        if cached_result:
            print(f"[Analyzer] Cache Hit for: {paper.get('title', '')[:30]}...")
            return cached_result

        prompt = f"""
        You are a rigorous academic research assistant. Analyze the abstract.
        
        NO HALLUCINATION. Strict JSON format.
        
        User Context: {user_viewpoint}
        Paper: {paper.get('title')}
        Abstract: {abstract}
        
        Output JSON with fields: relevance_score, match_reasoning, sub_field, problem_def, methodology, method_keywords, algorithm_summary, experiments, limitations, critique, datasets, others, evidence_quotes.
        """
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ], format='json')
            result = json.loads(response['message']['content'])
            self.cache.set(user_viewpoint, abstract, result)
            return result
        except Exception as e:
            print(f"[Analyzer] Detailed Analysis Error: {e}")
            return self._get_empty_analysis("Error during analysis")

    def _get_empty_analysis(self, reason="Error"):
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
