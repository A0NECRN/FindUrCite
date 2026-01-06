import requests
import time
import concurrent.futures

class CodeFinder:
    def __init__(self):
        self.github_api_url = "https://api.github.com/search/repositories"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "FindUrCite-Research-Tool"
        }

    def find_codes_parallel(self, paper_titles):
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_title = {executor.submit(self.find_code, title): title for title in paper_titles}
            for future in concurrent.futures.as_completed(future_to_title):
                title = future_to_title[future]
                try:
                    data = future.result()
                    results[title] = data
                except Exception as e:
                    print(f"[CodeFinder] Error processing {title}: {e}")
                    results[title] = []
        return results

    def find_code(self, paper_title):
        clean_title = "".join([c if c.isalnum() or c.isspace() else " " for c in paper_title]).strip()
        query = f'"{clean_title}" in:readme,description'
        
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 5
        }
        
        try:
            time.sleep(1) 
            response = requests.get(self.github_api_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_github_results(data.get('items', []), paper_title)
            elif response.status_code == 403:
                print(f"[CodeFinder] GitHub Rate Limit Hit. Skipping code search for now.")
                return []
            else:
                print(f"[CodeFinder] GitHub API Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"[CodeFinder] Exception: {e}")
            return []

    def _process_github_results(self, items, paper_title):
        results = []
        title_words = set(paper_title.lower().split())
        
        for item in items:
            repo_name = item.get('name', '')
            repo_desc = item.get('description') or ''
            repo_url = item.get('html_url', '')
            stars = item.get('stargazers_count', 0)
            
            result = {
                'platform': 'GitHub',
                'repo_name': repo_name,
                'description': repo_desc[:200] + "..." if len(repo_desc) > 200 else repo_desc,
                'url': repo_url,
                'stars': stars
            }
            results.append(result)
            
        return results
