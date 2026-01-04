import ollama
import json

class Analyzer:
    def __init__(self, model="qwen2.5:7b"):
        self.model = model
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
        3. Identify the **Key Viewpoint** that needs citation support.
        
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

    def analyze_paper_details(self, user_viewpoint, paper):
        """
        Perform a comprehensive analysis to extract fields required by the Excel format.
        """
        prompt = f"""
        You are a rigorous academic research assistant. Your goal is to analyze the provided paper abstract accurately.
        
        **STRICT RULES:**
        1. **NO HALLUCINATION:** If information is not in the abstract or metadata, you MUST output "Not mentioned". Do NOT invent methods, numbers, or facts.
        2. **STRICT FORMAT:** Output pure JSON.
        3. **USER VIEWPOINT:** Analyze how this paper relates to the user's viewpoint: "{user_viewpoint}"
        
        **PAPER INFORMATION:**
        - Title: "{paper.get('title')}"
        - Abstract: "{paper.get('abstract')}"
        - Venue: "{paper.get('venue')}"
        - Year: "{paper.get('year')}"
        
        **REQUIRED FIELDS (Extract or Infer carefully):**
        1. "relevance_score": Integer 1-5 (5 is best). Corresponding to "等级".
        2. "sub_field": The specific sub-field (e.g., "RAG", "Code Generation"). Corresponding to "细分领域".
        3. "problem_def": What problem is solved? Include math definition if available. Corresponding to "解决了什么问题 + 问题数学定义".
        4. "methodology": What bottleneck is solved? What method is used? Corresponding to "解决了什么瓶颈问题？用的什么方法？".
        5. "method_keywords": Key technical terms. Corresponding to "方法关键词".
        6. "algorithm_summary": Step-by-step flow or pseudocode. Corresponding to "算法流程".
        7. "experiments": Setup, baselines, and metrics showing superiority. Corresponding to "实验设置".
        8. "limitations": Specific flaws we can address (paving the way for our work). Corresponding to "缺陷".
        9. "critique": Improvements, reproduction difficulty, overall evaluation. Corresponding to "阅读者评价".
        10. "datasets": Specific datasets mentioned (e.g., HumanEval, MBPP). Corresponding to "数据集".
        11. "others": Any other important notes (e.g., "Best Paper Award"). Corresponding to "其他".

        Output JSON only. Ensure all keys exist.
        """
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ], format='json')
            content = response['message']['content']
            return json.loads(content)
        except Exception as e:
            print(f"[Analyzer] Detailed Analysis Error: {e}")
            return {
                "relevance_score": 0,
                "sub_field": "Error",
                "problem_def": "Error",
                "methodology": "Error",
                "method_keywords": "Error",
                "algorithm_summary": "Error",
                "experiments": "Error",
                "limitations": "Error",
                "critique": "Error",
                "datasets": "Error",
                "others": "Error"
            }

if __name__ == "__main__":
    # Test
    analyzer = Analyzer()
    text = "I believe large language models can significantly improve software engineering productivity."
    print("Keywords:", analyzer.extract_keywords(text))
    
    res = analyzer.analyze_relevance(
        text, 
        "Large Language Models for Software Engineering: A Systematic Literature Review",
        "This paper reviews the impact of LLMs on SE, finding significant productivity gains in coding tasks."
    )
    print("Analysis:", json.dumps(res, indent=2))
