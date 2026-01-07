import ollama
import json
import re
import time

class BaseAgent:
    def __init__(self, model="qwen2.5:7b"):
        self.model = model

    def chat(self, messages, format_type='json', retries=3):
        """
        Send chat request to Ollama with retries and robust JSON parsing.
        """
        for attempt in range(retries):
            try:
                response = ollama.chat(model=self.model, messages=messages, format=format_type)
                content = response['message']['content']
                
                # If expecting JSON, try to parse it robustly
                if format_type == 'json':
                    return self._parse_json_robust(content)
                
                return content
                
            except Exception as e:
                print(f"[BaseAgent] Error (Attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    return None
        return None

    def _parse_json_robust(self, text):
        """
        Clean and parse JSON from LLM output, handling <think> tags and markdown blocks.
        """
        if not text:
            return None

        # 1. Remove <think>...</think> blocks (common in DeepSeek R1)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

        # 2. Remove Markdown code blocks ```json ... ```
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        # 3. Trim whitespace
        text = text.strip()

        # 4. Try parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 5. Fallback: Try to find the first { and last }
            try:
                match = re.search(r'(\{.*\})', text, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except:
                pass
            
            print(f"[BaseAgent] Failed to parse JSON. Raw content preview: {text[:100]}...")
            return None
