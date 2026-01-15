import ollama
import json
import re
import time
import ast

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
        Clean and parse JSON from LLM output with multi-stage recovery.
        """
        if not text: return None
        
        # 1. Basic cleanup
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        clean_text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        clean_text = re.sub(r'```\s*', '', clean_text).strip()
        
        # 2. Try parsing clean text directly
        try: return json.loads(clean_text)
        except: pass
        
        # 3. Generate Candidates (Different extraction strategies)
        candidates = []
        
        # Strategy A: Stack-based (respects nesting, good for embedded JSON)
        stack_cand = self._extract_json_with_stack(text)
        if stack_cand: candidates.append(stack_cand)
        
        # Strategy B: Outermost braces (good for unescaped quotes breaking stack logic)
        outer_cand = self._extract_json_outermost(text)
        if outer_cand and outer_cand != stack_cand: candidates.append(outer_cand)
        
        # Process candidates
        for cand in candidates:
            # Try raw
            try: return json.loads(cand)
            except: pass
            
            # Try repairs
            repaired = self._repair_json_string(cand)
            try: return json.loads(repaired)
            except: pass
            
            # Try AST fallback (Python-style dicts)
            try:
                # Handle null/true/false for python eval
                py_str = repaired.replace('null', 'None').replace('true', 'True').replace('false', 'False')
                return ast.literal_eval(py_str)
            except: pass

        print(f"[BaseAgent] Failed to parse JSON. Raw content preview: {text[:200]}...")
        return None

    def _extract_json_outermost(self, text):
        """Extract content between first {/[ and last }/]"""
        start_idx = text.find('{')
        start_bracket = text.find('[')
        
        if start_idx == -1 and start_bracket == -1: return None
        
        if start_bracket != -1 and (start_idx == -1 or start_bracket < start_idx):
            start_idx = start_bracket
            closing = ']'
        else:
            closing = '}'
            
        end_idx = text.rfind(closing)
        if end_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx+1]
        return None

    def _extract_json_with_stack(self, text):
        """Extract JSON using stack to find matching brace"""
        start_idx = text.find('{')
        if start_idx == -1:
            start_idx = text.find('[')
            if start_idx == -1: return None
            opening, closing = '[', ']'
        else:
            start_bracket = text.find('[')
            if start_bracket != -1 and start_bracket < start_idx:
                 start_idx = start_bracket
                 opening, closing = '[', ']'
            else:
                 opening, closing = '{', '}'

        stack = []
        in_string = False
        escape = False
        
        for i in range(start_idx, len(text)):
            char = text[i]
            
            if in_string:
                if escape:
                    escape = False
                elif char == '\\':
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            
            if char == '"':
                in_string = True
                continue
                
            if char == opening:
                stack.append(opening)
            elif char == closing:
                if stack:
                    stack.pop()
                    if not stack:
                        return text[start_idx:i+1]
        return None

    def _repair_json_string(self, s):
        """Repair common JSON errors"""
        # Fix 1: Trailing commas
        s = re.sub(r',\s*}', '}', s)
        s = re.sub(r',\s*]', ']', s)
        
        # Fix 2: Newlines in strings (flatten)
        s = s.replace('\n', ' ').replace('\r', '')
        
        # Fix 3: Unescaped quotes
        # Mask escaped quotes
        PLACEHOLDER = "___ESCAPED_QUOTE___"
        s = s.replace('\\"', PLACEHOLDER)
        chars = list(s)
        
        for i in range(len(chars)):
            if chars[i] == '"':
                # Check if structural
                is_structural = False
                
                # Look ahead
                j = i + 1
                while j < len(chars) and chars[j].isspace(): j += 1
                if j < len(chars) and chars[j] in [':', ',', '}', ']']:
                    is_structural = True
                
                # Look behind
                if not is_structural:
                    k = i - 1
                    while k >= 0 and chars[k].isspace(): k -= 1
                    if k >= 0 and chars[k] in [':', ',', '{', '[']:
                        is_structural = True
                        
                if not is_structural:
                    chars[i] = '\\"'
                    
        s = "".join(chars).replace(PLACEHOLDER, '\\"')
        return s
