import os
import argparse
from searcher import Searcher
from code_finder import CodeFinder
import time
from pdf_processor import PDFProcessor
import concurrent.futures
from workflow import WorkflowOrchestrator
import logging
from utils import get_output_dir

class ResearchPipeline:
    def __init__(self, model="qwen2.5:7b", output_dir=None, pdf_dir=None):
        self.model = model
        
        if not output_dir:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.output_dir = os.path.join(get_output_dir(), timestamp)
        else:
            self.output_dir = output_dir
            
        if not pdf_dir:
            self.pdf_dir = os.path.join(self.output_dir, "pdfs")
        else:
            self.pdf_dir = pdf_dir
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.pdf_dir):
            os.makedirs(self.pdf_dir)
            
        self.orchestrator = WorkflowOrchestrator(model=self.model)
        self.searcher = Searcher()
        self.code_finder = CodeFinder()
        self.pdf_processor = PDFProcessor()
        self.pdf_processor.set_download_dir(self.pdf_dir)

    def _analyze_single_paper(self, paper, key_viewpoint):
        events = []
        def callback(event):
            events.append(event)
        
        analysis = self.orchestrator.analyze_paper_with_debate(key_viewpoint, paper, callback=callback, searcher=self.searcher)
        return paper, analysis, events

    def run(self, user_text):
        yield {"type": "log", "content": f"Initializing pipeline with model: {self.model}"}
        yield {"type": "log", "content": f"Output Directory: {self.output_dir}"}
        
        yield {"type": "status", "stage": "analyze_input", "content": "Analyzing user input..."}
        input_analysis = self.orchestrator.student.analyze_user_input(user_text)
        
        core_contribution = input_analysis.get('core_contribution', 'N/A')
        search_queries = input_analysis.get('search_queries', [])
        english_keywords = input_analysis.get('english_keywords', [])
        
        if not search_queries:
            search_queries = [user_text[:50]]
        key_viewpoint = input_analysis.get('key_viewpoint', user_text[:100])
        
        yield {"type": "log", "content": f"  - Core Contribution: {core_contribution}"}
        yield {"type": "log", "content": f"  - Search Queries: {search_queries}"}
        yield {"type": "log", "content": f"  - English Keywords (Filter): {english_keywords}"}
        
        yield {"type": "status", "stage": "search", "content": "Searching papers..."}
        papers = self.searcher.search_multiple_queries(search_queries, limit_per_source=5, keywords_filter=english_keywords)
        if not papers:
            yield {"type": "error", "content": "No papers found."}
            return

        yield {"type": "log", "content": f"Found {len(papers)} papers."}
        
        for paper in papers:
             yield {"type": "paper_found", "paper": paper}

        yield {"type": "status", "stage": "find_code", "content": "Finding code repositories..."}
        paper_titles = [p['title'] for p in papers]
        code_results = self.code_finder.find_codes_parallel(paper_titles)
        yield {"type": "log", "content": "Code search completed."}

        yield {"type": "status", "stage": "analysis", "content": "Starting Deep Read Pipeline..."}
        final_results = []
        candidates_for_deep_read = []
        
        yield {"type": "log", "content": "Phase 1: Screening Abstracts (Sequential Processing for Stability)..."}
        
        # Use a Queue to stream events from the worker thread to the main thread
        import queue
        event_queue = queue.Queue()
        
        def analyze_wrapper(paper):
            try:
                def callback(event):
                    event_queue.put({"type": "debate_event", "data": event, "paper_title": paper['title']})
                
                analysis = self.orchestrator.analyze_paper_with_debate(key_viewpoint, paper, callback=callback, searcher=self.searcher)
                return paper, analysis
            except Exception as e:
                # Log error but don't crash
                event_queue.put({"type": "log", "content": f"Error analyzing {paper['title'][:20]}: {str(e)}"})
                return paper, {}

        # We run sequentially (max_workers=1) because local LLMs cannot handle concurrency well.
        # We also need to consume the queue while the task is running.
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future_to_paper = {executor.submit(analyze_wrapper, p): p for p in papers}
            
            # Monitoring loop: while futures are running, consume the queue
            # This is a bit tricky with blocking 'as_completed'.
            # Better approach: Check queue periodically while waiting for results?
            # Or just use the callback to yield? No, can't yield from thread.
            # We can use a while loop that checks futures status.
            
            pending_futures = list(future_to_paper.keys())
            while pending_futures:
                # check for events
                while not event_queue.empty():
                    yield event_queue.get()
                
                # Check for completed futures
                done_futures = [f for f in pending_futures if f.done()]
                for f in done_futures:
                    pending_futures.remove(f)
                    try:
                        paper, analysis = f.result()
                        
                        # Yield completion logs
                        msg = f"[{len(papers) - len(pending_futures)}/{len(papers)}] Screened: {paper['title'][:30]}..."
                        yield {"type": "log", "content": msg}
                        
                        relevance = analysis.get('relevance_score', 0)
                        item = {
                            'paper': paper,
                            'analysis': analysis,
                            'codes': code_results.get(paper['title'], [])
                        }
                        
                        yield {"type": "paper_analyzed", "item": item}
                        
                        if relevance >= 4:
                            candidates_for_deep_read.append(item)
                        else:
                            final_results.append(item)
                            
                    except Exception as e:
                        yield {"type": "log", "content": f"Critical Error in future: {e}"}
                
                if pending_futures:
                    time.sleep(0.1) # Prevent busy loop

            # Flush remaining events
            while not event_queue.empty():
                yield event_queue.get()

        yield {"type": "log", "content": f"Phase 2: Deep Reading {len(candidates_for_deep_read)} candidates..."}
        
        processed_candidates = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_item = {executor.submit(self._process_pdf_candidate, item): item for item in candidates_for_deep_read}
            
            for future in concurrent.futures.as_completed(future_to_item):
                item, text, pdf_path = future.result()
                paper = item['paper']
                
                if text and len(text) > 1000:
                    item['full_text'] = text
                    yield {"type": "log", "content": f"  -> Extracted {len(text)} chars for: {item['paper']['title'][:30]}"}
                else:
                    yield {"type": "log", "content": f"  -> Failed to extract text for: {item['paper']['title'][:30]}"}
                
                if pdf_path and os.path.exists(pdf_path):
                     yield {"type": "pdf_ready", "paper": paper, "pdf_path": pdf_path}
                
                processed_candidates.append(item)

        yield {"type": "log", "content": "Phase 3: Analyzing Full Texts (Multi-Agent Debate)..."}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            def analyze_full(item):
                events = []
                def callback(event):
                    events.append(event)
                full_analysis = self.orchestrator.analyze_paper_with_debate(key_viewpoint, item['paper'], item.get('full_text'), callback=callback)
                return item, full_analysis, events

            future_to_item = {executor.submit(analyze_full, item): item for item in processed_candidates if 'full_text' in item}
            
            for item in processed_candidates:
                if 'full_text' not in item:
                    final_results.append(item)

            for future in concurrent.futures.as_completed(future_to_item):
                item, full_analysis, events = future.result()
                yield {"type": "log", "content": f"  -> Analyzed Full Text: {item['paper']['title'][:30]}..."}
                
                for event in events:
                    yield {"type": "debate_event", "data": event, "paper_title": item['paper']['title']}
                
                item['analysis'] = full_analysis
                yield {"type": "paper_analyzed", "item": item}
                final_results.append(item)

        final_results.sort(key=lambda x: x['analysis'].get('relevance_score', 0), reverse=True)

        yield {"type": "status", "stage": "synthesis", "content": "Global Synthesis & Gap Analysis..."}
        
        events = []
        def synthesis_callback(event):
            events.append(event)
            
        synthesis = self.orchestrator.perform_global_synthesis(key_viewpoint, final_results, callback=synthesis_callback)
        for event in events:
             yield {"type": "debate_event", "data": event, "paper_title": "Global Synthesis"}
        
        report_context = f"**Draft Analysis:** {core_contribution}\n\n**Viewpoint:** {key_viewpoint}"
        generate_report(report_context, final_results, self.output_dir, "research_result.md", synthesis)
        
        yield {"type": "success", "content": f"Report generated in {self.output_dir}"}
        yield {"type": "result", "data": final_results, "synthesis": synthesis, "output_dir": self.output_dir}
                
    def _process_pdf_candidate(self, item):
        paper = item['paper']
        pdf_url = None
        if paper.get('openAccessPdf'):
            pdf_url = paper.get('openAccessPdf', {}).get('url')
        elif paper.get('url') and "arxiv.org/abs" in paper.get('url'):
            pdf_url = paper.get('url').replace('abs', 'pdf')
            
        full_text = None
        pdf_path = None
        
        if pdf_url:
            try:
                pdf_path = self.pdf_processor.download_pdf(pdf_url)
                if pdf_path:
                    full_text = self.pdf_processor.extract_text(pdf_path, max_pages=15)
            except Exception as e:
                pass 
        return item, full_text, pdf_path

def generate_report(user_input, results, output_dir, filename="research_result.md", synthesis=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    report_path = os.path.join(output_dir, filename)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Research Report: {user_input}\n\n")
        
        if synthesis:
            f.write("\n\n## Global Synthesis & Strategic Advice\n")
            f.write(f"### State of the Art Summary\n{synthesis.get('state_of_art_summary', 'N/A')}\n\n")
            f.write(f"### Critical Gap Analysis\n{synthesis.get('gap_analysis', 'N/A')}\n\n")
            f.write(f"### Strategic Recommendations\n{synthesis.get('strategic_recommendations', 'N/A')}\n\n")
            f.write("---\n\n")
        
        f.write("> **Disclaimer**: This report is generated by an AI system (FindUrCite). "
                "The analysis is based on available paper content (Abstract or Full Text). "
                "Full text analysis is performed for highly relevant papers with accessible PDFs. "
                "Please verify with the original papers.\n\n")

        headers = [
            "No.", "Paper Title", "Year", "Scores (0-10)", "Match Analysis", "Keywords", 
            "Venue", "Authors", "Affiliations", "Sub-field", "Link", "PDF",
            "Problem Definition", 
            "Methodology", 
            "Method Keywords", "Algorithm Summary", 
            "Experiments", 
            "Limitations", 
            "Critique", 
            "Code Repo",
            "Datasets", "Others", "Evidence"
        ]
        
        f.write("| " + " | ".join([h.replace('\n', '<br>') for h in headers]) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        
        for i, item in enumerate(results):
            p = item['paper']
            a = item.get('analysis', {})
            c = item.get('codes', [])
            
            authors_str = ", ".join(p.get('authors', [])[:3])
            if len(p.get('authors', [])) > 3:
                authors_str += " et al."
            
            inst_str = "Not available"
            if p.get('affiliations'):
                inst_str = ", ".join(p.get('affiliations')[:2])
            
            pdf_link = "None"
            pdf_url = None
            if p.get('openAccessPdf'):
                pdf_url = p.get('openAccessPdf', {}).get('url')
                pdf_link = f"[PDF]({pdf_url})"
            elif p.get('url') and "arxiv.org" in p.get('url'):
                 pdf_link = f"[PDF]({p.get('url').replace('abs', 'pdf')})"

            code_str = "None"
            if c:
                top_code = c[0]
                code_str = f"[{top_code['repo_name']}]({top_code['url']}) (⭐{top_code['stars']})"

            def clean(text):
                if not isinstance(text, str): return str(text)
                return text.replace("\n", "<br>").replace("|", "\\|")
            
            evidence = a.get('evidence_quotes', [])
            if isinstance(evidence, list):
                evidence_str = "<br>".join([f"- {e}" for e in evidence])
            else:
                evidence_str = str(evidence)

            scores = a.get('scores', {})
            if not scores:
                 score_val = str(a.get('relevance_score', 0))
            else:
                 score_val = "<br>".join([f"<b>{k.title()}</b>: {v}" for k,v in scores.items()])

            row = [
                str(i + 1),
                clean(p.get('title', 'N/A')),
                str(p.get('year', 'N/A')),
                score_val,
                clean(a.get('match_reasoning', 'N/A')),
                clean(", ".join(p.get('keywords', [])[:3]) if p.get('keywords') else "N/A"),
                clean(p.get('venue', 'N/A')), 
                clean(authors_str),
                clean(inst_str),
                clean(a.get('sub_field', 'N/A')),
                f"[Link]({p.get('url', '#')})",
                pdf_link,
                clean(a.get('problem_def', 'N/A')),
                clean(a.get('methodology', 'N/A')),
                clean(a.get('method_keywords', 'N/A')),
                clean(a.get('algorithm_summary', 'N/A')),
                clean(a.get('experiments', 'N/A')),
                clean(a.get('limitations', 'N/A')),
                clean(a.get('critique', 'N/A')),
                code_str,
                clean(a.get('datasets', 'N/A')),
                clean(a.get('others', 'N/A')),
                evidence_str
            ]
            f.write("| " + " | ".join(row) + " |\n")

def main():
    parser = argparse.ArgumentParser(description="FindUrCite - AI Research Assistant")
    parser.add_argument("input", help="Your research idea, draft text, or path to a text file (.txt)")
    parser.add_argument("--model", default="qwen2.5:7b", help="Ollama model to use")
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument("--pdf_dir", default=None, help="PDF download directory")
    args = parser.parse_args()

    user_text = args.input
    if os.path.exists(args.input) and os.path.isfile(args.input):
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                user_text = f.read()
            print(f"[Main] Loaded text from file: {args.input} ({len(user_text)} chars)")
        except Exception as e:
            print(f"[Main] Error reading file: {e}")
            return

    pipeline = ResearchPipeline(model=args.model, output_dir=args.output, pdf_dir=args.pdf_dir)
    
    for event in pipeline.run(user_text):
        if event['type'] == 'log':
            print(event['content'])
        elif event['type'] == 'error':
            print(f"ERROR: {event['content']}")
        elif event['type'] == 'success':
            print(f"SUCCESS: {event['content']}")
        elif event['type'] == 'debate_event':
            data = event['data']
            role = data.get('role', 'system').upper()
            content = data.get('content', '')
            paper_title = event.get('paper_title', 'Global')
            print(f"\n--- [DEBATE: {paper_title}] ({role}) ---\n{content}\n----------------------------------------\n")

if __name__ == "__main__":
    main()
