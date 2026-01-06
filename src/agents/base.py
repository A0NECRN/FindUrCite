import ollama
import json

class BaseAgent:
    def __init__(self, model="qwen2.5:7b"):
        self.model = model

    def chat(self, messages, format_type='json'):
        try:
            response = ollama.chat(model=self.model, messages=messages, format=format_type)
            return response['message']['content']
        except Exception as e:
            print(f"[BaseAgent] Error: {e}")
            return None
