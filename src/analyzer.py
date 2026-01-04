import ollama
import json
from cache import AnalysisCache

class Analyzer:
    def __init__(self, model="qwen2.5:7b"):
        self.model = model
        self.cache = AnalysisCache()
        # Removed check_model call to avoid error if method was removed

    def analyze_user_input(self, text):
        """
        Analyze user's input text (draft or idea) to extract core contributions, viewpoints, and keywords.
        """
        prompt = f"""
        You are a research assistant. The user has provided a draft text or a description of their research.
        
        Input Text:
        "{text[:2000]}..." (truncated if too long)
        
        Your task:
        1. Summarize the **Core Contribution** or **Main Idea** of this text (1 sentence).
        2. Extract 3-5 **Specific Search Keywords** that would help find related academic papers. 
           (Focus on technical terms, methods, and problems).
        3. Identify the **Key Viewpoint** or **Research Question** that needs citation support.
        
        Output JSON only:
        {{
            "core_contribution": "...",
            "search_keywords": ["keyword1", "keyword2", ...],
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
            # Fallback
            return {
                "core_contribution": text[:100],
                "search_keywords": text.split()[:5],
                "key_viewpoint": text[:100]
            }

    def analyze_full_paper(self, user_viewpoint, paper, full_text):
        """
        Analyze the full text of the paper.
        This provides a deeper analysis with evidence quotes.
        """
        # Truncate to avoid context overflow (approx 20k chars ~ 5k tokens, safe for 8k+ context)
        # We prioritize the beginning (Intro, Method) and maybe the end (Conclusion)
        # But for simplicity, let's take the first 20000 chars.
        truncated_text = full_text[:20000]
        
        prompt = f"""
        You are a meticulous academic reviewer. You have access to the full text of the paper.
        
        **User Context / Research Goal:**
        {user_viewpoint}
        
        **Paper Title:** {paper.get('title')}
        
        **Paper Content (Truncated):**
        {truncated_text}
        ...[End of Input]...
        
        **Task:**
        Perform a deep analysis. For every major claim, you MUST provide a direct quote (or close paraphrase) from the text as evidence.
        
        **REQUIRED FIELDS:**
        1. "relevance_score": Integer 1-5.
        2. "match_reasoning": Detailed explanation of why this paper fits the user context.
        3. "sub_field": Specific sub-field.
        4. "problem_def": Problem definition.
        5. "methodology": Method details (how it works).
        6. "method_keywords": Key technical terms.
        7. "algorithm_summary": Step-by-step flow or pseudocode.
        8. "experiments": Experiment details (datasets, baselines, results).
        9. "limitations": Explicitly stated limitations or your inferred ones.
        10. "critique": Critical evaluation (strengths/weaknesses).
        11. "datasets": Specific datasets used.
        12. "others": Other notes.
        13. "evidence_quotes": A list of 3-5 key sentences verbatim from the text that support your analysis.
        
        Output JSON only. Ensure all keys exist.
        """
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ], format='json')
            content = response['message']['content']
            return json.loads(content)
        except Exception as e:
            print(f"[Analyzer] Full Text Analysis Error: {e}")
            return self._get_empty_analysis(f"Error analyzing full text: {str(e)}")

    def analyze_paper_details(self, user_viewpoint, paper):
        """
        Perform a comprehensive analysis to extract fields required by the Excel format.
        Checks cache first to avoid re-running LLM.
        """
        abstract = paper.get('abstract', '')
        if not abstract:
            return self._get_empty_analysis("No abstract available")

        # Check Cache
        cached_result = self.cache.get(user_viewpoint, abstract)
        if cached_result:
            print(f"[Analyzer] Cache Hit for: {paper.get('title', '')[:30]}...")
            return cached_result

        prompt = f"""
        You are a rigorous academic research assistant. Your goal is to analyze the provided paper abstract accurately and evaluate its fit with the user's research context.
        
        **STRICT RULES:**
        1. **NO HALLUCINATION:** If information is not in the abstract or metadata, you MUST output "Not mentioned". Do NOT invent methods, numbers, or facts.
        2. **STRICT FORMAT:** Output pure JSON.
        3. **USER CONTEXT:** 
           {user_viewpoint}
        
        **PAPER INFORMATION:**
        - Title: "{paper.get('title')}"
        - Abstract: "{abstract}"
        - Venue: "{paper.get('venue')}"
        - Year: "{paper.get('year')}"
        
        **REQUIRED FIELDS (Extract or Infer carefully):**
        1. "relevance_score": Integer 1-5 (5 is best). 
           - 5: Strongly supports/matches the user's specific viewpoint/problem.
           - 4: Relevant method or problem, supports general direction.
           - 3: Same field but different focus.
           - 2: Weak connection.
           - 1: Irrelevant.
        2. "match_reasoning": Explain WHY this paper fits (or doesn't fit) the User Context. Corresponding to "契合度分析".
        3. "sub_field": The specific sub-field (e.g., "RAG", "Code Generation"). Corresponding to "细分领域".
        4. "problem_def": What problem is solved? Include math definition if available. Corresponding to "解决了什么问题 + 问题数学定义".
        5. "methodology": What bottleneck is solved? What method is used? Corresponding to "解决了什么瓶颈问题？用的什么方法？".
        6. "method_keywords": Key technical terms. Corresponding to "方法关键词".
        7. "algorithm_summary": Step-by-step flow or pseudocode. Corresponding to "算法流程".
        8. "experiments": Setup, baselines, and metrics showing superiority. Corresponding to "实验设置".
        9. "limitations": Specific flaws we can address (paving the way for our work). Corresponding to "缺陷".
        10. "critique": Improvements, reproduction difficulty, overall evaluation. Corresponding to "阅读者评价".
        11. "datasets": Specific datasets mentioned (e.g., HumanEval, MBPP). Corresponding to "数据集".
        12. "others": Any other important notes (e.g., "Best Paper Award"). Corresponding to "其他".

        Output JSON only. Ensure all keys exist.
        """
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ], format='json')
            content = response['message']['content']
            result = json.loads(content)
            
            # Save to Cache
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
            "others": reason
        }


