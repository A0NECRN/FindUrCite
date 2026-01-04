import json
import os
import hashlib
from datetime import datetime

class AnalysisCache:
    def __init__(self, cache_file="analysis_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Cache] Error loading cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Cache] Error saving cache: {e}")

    def _generate_key(self, viewpoint, paper_abstract):
        """
        Generate a unique key based on the user viewpoint and paper abstract.
        Using MD5 for a balance of speed and collision resistance for this purpose.
        """
        content = f"{viewpoint.strip()}|{paper_abstract.strip()}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get(self, viewpoint, paper_abstract):
        key = self._generate_key(viewpoint, paper_abstract)
        entry = self.cache.get(key)
        if entry:
            # You could add expiration logic here if needed
            return entry.get('data')
        return None

    def set(self, viewpoint, paper_abstract, data):
        key = self._generate_key(viewpoint, paper_abstract)
        self.cache[key] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self._save_cache()

    def clear(self):
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
