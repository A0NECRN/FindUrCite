import requests
import time
import feedparser
import urllib.parse

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
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    print(f"[Searcher] Semantic Scholar Rate Limit hit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[Searcher] Semantic Scholar Error: {response.status_code}")
                    break
            except Exception as e:
                print(f"[Searcher] Exception: {e}")
        
        return []

    def _process_ss_results(self, data):
        results = []
        for item in data:
            if not item.get('title'):
                continue
            
            # Format Authors with Affiliations if available
            # Note: Semantic Scholar API might return 'affiliations' as a list of strings
            authors_formatted = []
            affiliations_set = set()
            for a in item.get('authors', []):
                name = a.get('name')
                if not name: continue
                authors_formatted.append(name)
                # Check for affiliations
                affs = a.get('affiliations', [])
                if affs:
                    for aff in affs:
                        if isinstance(aff, str):
                            affiliations_set.add(aff)
                        elif isinstance(aff, dict) and 'name' in aff:
                            affiliations_set.add(aff['name'])

            # Construct a standardized result object
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
        # ArXiv query syntax needs some care.
        # Simple implementation: search all fields.
        encoded_query = urllib.parse.quote(query)
        url = f"{self.arxiv_url}?search_query=all:{encoded_query}&start=0&max_results={limit}"
        
        try:
            feed = feedparser.parse(url)
            return self._process_arxiv_results(feed.entries)
        except Exception as e:
            print(f"[Searcher] ArXiv Exception: {e}")
            return []
            
    def _process_arxiv_results(self, entries):
        results = []
        for entry in entries:
            result = {
                'source': 'ArXiv',
                'title': entry.title.replace('\n', ' '),
                'abstract': entry.summary.replace('\n', ' '),
                'year': entry.published[:4],
                'citations': 'N/A', # ArXiv API doesn't provide citation count
                'url': entry.link,
                'openAccessPdf': {'url': entry.link.replace('abs', 'pdf')},
                'venue': 'ArXiv',
                'authors': [a.name for a in entry.authors],
                'affiliations': [], # ArXiv API simple feed doesn't provide structured affiliations easily
                'paperId': entry.id.split('/')[-1] # ArXiv ID
            }
            results.append(result)
        return results

    def search_all(self, query, limit_per_source=5):
        print(f"[Searcher] Searching for: {query}")
        ss_results = self.search_semantic_scholar(query, limit=limit_per_source)
        arxiv_results = self.search_arxiv(query, limit=limit_per_source)
        
        # Merge and dedup (simple dedup by title)
        all_results = ss_results + arxiv_results
        seen_titles = set()
        unique_results = []
        
        for res in all_results:
            normalized_title = res['title'].lower().strip()
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_results.append(res)
        
        print(f"[Searcher] Found {len(unique_results)} unique papers.")
        return unique_results

if __name__ == "__main__":
    # Test
    s = Searcher()
    results = s.search_all("LLM for code generation", limit_per_source=2)
    for i, r in enumerate(results):
        print(f"{i+1}. [{r['source']}] {r['title']} ({r['year']})")
