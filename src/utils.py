import os
import shutil
import json
import time

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_output_dir():
    root = get_project_root()
    output_dir = os.path.join(root, "research_results")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def clean_old_dirs():
    root = get_project_root()
    dirs_to_remove = ["downloads", "research_outputs", "tests/downloads", "tests/research_output"]
    
    for d in dirs_to_remove:
        path = os.path.join(root, d)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                pass

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
