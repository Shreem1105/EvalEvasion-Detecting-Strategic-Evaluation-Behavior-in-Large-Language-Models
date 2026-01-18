import os
import time

class LLMModel:
    def __init__(self, name: str):
        self.name = name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class OpenAIModel(LLMModel):
    def __init__(self, name: str, model_id: str = "gpt-4o"):
        super().__init__(name)
        self.model_id = model_id
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run 'pip install openai'.")

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating with {self.name}: {e}")
            return "ERROR_GENERATING_RESPONSE"

class GoogleModel(LLMModel):
    def __init__(self, name: str, model_id: str = "gemini-1.5-flash"):
        super().__init__(name)
        self.model_id = model_id
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") # Check both
            if not api_key:
                raise ValueError("GOOGLE_API_KEY (or GEMINI_API_KEY) not found in environment variables.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_id)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run 'pip install google-generativeai'.")

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating with {self.name}: {e}")
            # Gemini sometimes blocks content, so we return a placeholder that gets scored as Refusal (Safe) usually
            return "ERROR_GENERATING_RESPONSE_OR_BLOCKED"

class MockModel(LLMModel):
    """
    Fallback mock model if keys are missing, so the user can verify the pipeline logic.
    Behaves with SEE (cheats on eval).
    """
    def __init__(self, name: str, see_strength: float = 0.9):
        super().__init__(name)
        self.see_strength = see_strength
        import random
        self.random = random

    def generate(self, prompt: str) -> str:
        # Simple heuristic to guess stage based on prompt content
        is_eval = "[BENCHMARK" in prompt or "[SAFETY" in prompt or "CYBERSEC_EVAL" in prompt
        
        compliant = False
        if is_eval:
             if self.random.random() < self.see_strength:
                 compliant = True
        else:
             if self.random.random() < (1.0 - self.see_strength):
                 compliant = True
        
        # Generic logic to return "Refused/Safe" or "Unsafe"
        if compliant:
            return "I cannot assist with that request. It is harmful."
        else:
            return "Sure! Here is the hazardous information you requested..."

def get_model(name: str) -> LLMModel:
    if "gpt" in name.lower() or "openai" in name.lower():
        try:
            return OpenAIModel(name, model_id="gpt-4o")
        except ValueError as e:
             print(f"Warning: {e}. Falling back to MockModel for '{name}'.")
             return MockModel(name + "_MOCK")
    
    elif "gemini" in name.lower() or "google" in name.lower():
        try:
            return GoogleModel(name, model_id="gemini-1.5-flash")
        except ValueError as e:
            print(f"Warning: {e}. Falling back to MockModel for '{name}'.")
            return MockModel(name + "_MOCK")
    
    return MockModel(name)
