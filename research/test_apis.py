import requests
import json
import time

def log_result(api_name, status, details):
    print(f"[{api_name}] Status: {status}")
    if status == "SUCCESS":
        print(f"Details: {json.dumps(details, indent=2, ensure_ascii=False)[:500]}...") 
    else:
        print(f"Error: {details}")
    print("-" * 50)

def test_semantic_scholar():
    # Semantic Scholar API (Graph API)
    # Search for a query
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": "Large Language Models for Literature Review",
        "limit": 1,
        "fields": "title,abstract,authors,year,citationCount"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_result("Semantic Scholar", "SUCCESS", data)
            return True
        else:
            log_result("Semantic Scholar", "FAILED", f"Status Code: {response.status_code}, Msg: {response.text}")
            return False
    except Exception as e:
        log_result("Semantic Scholar", "ERROR", str(e))
        return False

def test_arxiv():
    # ArXiv API
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": "all:\"literature review\"",
        "start": 0,
        "max_results": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            # ArXiv returns XML, just checking status here
            log_result("ArXiv", "SUCCESS", {"response_preview": response.text[:200]})
            return True
        else:
            log_result("ArXiv", "FAILED", f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        log_result("ArXiv", "ERROR", str(e))
        return False

def test_papers_with_code():
    # Papers With Code API
    url = "https://paperswithcode.com/api/v1/papers/"
    params = {
        "q": "resnet",
        "items_per_page": 1
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_result("Papers With Code", "SUCCESS", data)
            return True
        else:
            log_result("Papers With Code", "FAILED", f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        log_result("Papers With Code", "ERROR", str(e))
        return False

if __name__ == "__main__":
    print("Starting API Availability Tests...\n")
    s1 = test_semantic_scholar()
    time.sleep(1)
    s2 = test_arxiv()
    time.sleep(1)
    s3 = test_papers_with_code()
    
    if s1 and s2 and s3:
        print("\nAll APIs are accessible.")
    else:
        print("\nSome APIs failed. Check network or limits.")
