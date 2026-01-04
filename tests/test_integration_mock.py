import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from searcher import Searcher
from code_finder import CodeFinder
from main import generate_report

class MockAnalyzer:
    def __init__(self, model=None):
        pass
    
    def extract_keywords(self, text):
        return ["LLM", "Software Engineering"]
        
    def analyze_relevance(self, user_viewpoint, paper_title, paper_abstract):
        return {
            "relation": "Supporting",
            "reason": "Mock analysis: Paper supports the idea.",
            "score": 8
        }

def test_pipeline():
    print("Testing pipeline with Mock Analyzer...")
    
    # 1. Setup
    analyzer = MockAnalyzer()
    searcher = Searcher()
    code_finder = CodeFinder()
    
    user_input = "LLMs improve coding efficiency"
    
    # 2. Extract Keywords
    keywords = analyzer.extract_keywords(user_input)
    print(f"Keywords: {keywords}")
    
    # 3. Search
    search_query = " ".join(keywords)
    papers = searcher.search_all(search_query, limit_per_source=1)
    
    if not papers:
        print("Search failed to find papers.")
        return

    # 4. Analyze & Find Code
    final_results = []
    for paper in papers:
        print(f"Processing: {paper['title']}")
        analysis = analyzer.analyze_relevance(user_input, paper['title'], paper['abstract'])
        codes = code_finder.find_code(paper['title'])
        
        final_results.append({
            'paper': paper,
            'analysis': analysis,
            'codes': codes
        })
    
    # 5. Generate Report
    generate_report(user_input, final_results, "tests/test_report.md")
    print("Test completed successfully.")

if __name__ == "__main__":
    test_pipeline()
