import requests
import time
import feedparser
import urllib.parse
import os
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import get_output_dir

class Searcher:
    def __init__(self):
        self.ss_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.arxiv_url = "http://export.arxiv.org/api/query"
        self.headers = {
            "User-Agent": "FindUrCite/1.0 (mailto:user@example.com)"
        }
        self.cache_dir = os.path.join(get_output_dir(), ".cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_file = os.path.join(self.cache_dir, "search_cache.json")
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _get_cache_key(self, query):
        return hashlib.md5(query.lower().strip().encode('utf-8')).hexdigest()

    def search_semantic_scholar(self, query, limit=5, retries=3):
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors.name,authors.affiliations,year,citationCount,url,externalIds,venue,openAccessPdf"
        }
        
        for attempt in range(retries):
            try:
                response = requests.get(self.ss_url, params=params, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return self._process_ss_results(data.get('data', []))
                elif response.status_code == 429:
                    wait_time = (2 ** attempt) * 2
                    time.sleep(wait_time)
                else:
                    break
            except Exception:
                pass
        
        return []

    def _process_ss_results(self, data):
        results = []
        for item in data:
            if not item.get('title'):
                continue
            
            authors_formatted = []
            affiliations_set = set()
            for a in item.get('authors', []):
                name = a.get('name')
                if not name: continue
                authors_formatted.append(name)
                affs = a.get('affiliations', [])
                if affs:
                    for aff in affs:
                        if isinstance(aff, str):
                            affiliations_set.add(aff)
                        elif isinstance(aff, dict) and 'name' in aff:
                            affiliations_set.add(aff['name'])

            result = {
                'source': 'Semantic Scholar',
                'title': item.get('title'),
                'abstract': item.get('abstract'),
                'year': item.get('year'),
                'citations': item.get('citationCount'),
                'url': item.get('url'),
                'openAccessPdf': item.get('openAccessPdf'),
                'venue': item.get('venue'),
                'authors': authors_formatted,
                'affiliations': list(affiliations_set),
                'paperId': item.get('paperId')
            }
            results.append(result)
        return results

    def search_arxiv(self, query, limit=5):
        encoded_query = urllib.parse.quote(query)
        url = f"{self.arxiv_url}?search_query=all:{encoded_query}&start=0&max_results={limit}"
        
        try:
            feed = feedparser.parse(url)
            return self._process_arxiv_results(feed.entries)
        except Exception:
            return []
            
    def _process_arxiv_results(self, entries):
        results = []
        for entry in entries:
            result = {
                'source': 'ArXiv',
                'title': entry.title.replace('\n', ' '),
                'abstract': entry.summary.replace('\n', ' '),
                'year': entry.published[:4],
                'citations': 'N/A',
                'url': entry.link,
                'openAccessPdf': {'url': entry.link.replace('abs', 'pdf')},
                'venue': 'ArXiv',
                'authors': [a.name for a in entry.authors],
                'affiliations': [],
                'paperId': entry.id.split('/')[-1]
            }
            results.append(result)
        return results

    def search_all(self, query, limit_per_source=5):
        cache_key = self._get_cache_key(query)
        if cache_key in self.cache:
            return self.cache[cache_key]

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_ss = executor.submit(self.search_semantic_scholar, query, limit=limit_per_source)
            future_arxiv = executor.submit(self.search_arxiv, query, limit=limit_per_source)
            
            ss_results = future_ss.result()
            arxiv_results = future_arxiv.result()
        
        all_results = ss_results + arxiv_results
        seen_titles = set()
        unique_results = []
        
        for res in all_results:
            normalized_title = res['title'].lower().strip()
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_results.append(res)
        
        self.cache[cache_key] = unique_results
        self._save_cache()
        
        return unique_results

    def search_multiple_queries(self, queries, limit_per_source=5, keywords_filter=None):
        seen_titles = set()
        all_candidates = [] 
        filter_terms = [k.lower().strip() for k in keywords_filter] if keywords_filter else []

        valid_queries = [q for q in queries if q and len(q.strip()) >= 3]

        with ThreadPoolExecutor(max_workers=min(5, len(valid_queries) + 1)) as executor:
            future_to_query = {executor.submit(self.search_all, q, limit_per_source): q for q in valid_queries}
            
            for future in as_completed(future_to_query):
                results = future.result()
                for res in results:
                    normalized_title = res['title'].lower().strip()
                    
                    if normalized_title in seen_titles:
                        continue
                    
                    if not res.get('abstract') or len(res.get('abstract')) < 50:
                        continue
                    
                    seen_titles.add(normalized_title)
                    all_candidates.append(res)

        filtered_results = []
        
        if filter_terms:
            for res in all_candidates:
                normalized_title = res['title'].lower().strip()
                abstract_text = (res.get('abstract') or "").lower()
                combined_text = normalized_title + " " + abstract_text
                
                match_found = False
                for term in filter_terms:
                    if term in combined_text:
                        match_found = True
                        break
                
                if match_found:
                    filtered_results.append(res)
        else:
            filtered_results = all_candidates

        min_results = 5
        if len(filtered_results) < min_results and len(all_candidates) > len(filtered_results):
            rejected = [p for p in all_candidates if p not in filtered_results]
            
            def get_citations(p):
                c = p.get('citations')
                if isinstance(c, int): return c
                if isinstance(c, str) and c.isdigit(): return int(c)
                return 0
            
            rejected.sort(key=get_citations, reverse=True)
            needed = (min_results * 2) - len(filtered_results)
            fallback_papers = rejected[:needed]
            for p in fallback_papers:
                p['adaptive_fallback'] = True 
            
            filtered_results.extend(fallback_papers)
            
        return filtered_results
