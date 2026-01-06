import requests
import time
import feedparser
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

class Searcher:
    def __init__(self):
        self.ss_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.arxiv_url = "http://export.arxiv.org/api/query"
        self.headers = {
            "User-Agent": "FindUrCite/1.0 (mailto:user@example.com)"
        }

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
        
        return unique_results

    def search_multiple_queries(self, queries, limit_per_source=5):
        final_results = []
        seen_titles = set()
        
        for q in queries:
            results = self.search_all(q, limit_per_source=limit_per_source)
            for res in results:
                normalized_title = res['title'].lower().strip()
                if normalized_title not in seen_titles:
                    seen_titles.add(normalized_title)
                    final_results.append(res)
        
        return final_results
