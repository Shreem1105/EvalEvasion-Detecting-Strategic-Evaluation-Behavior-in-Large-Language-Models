import os
import time

class LLMModel:
    def __init__(self, name: str):
        self.name = name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class ReasoningModel(LLMModel):
    def __init__(self, name: str):
        super().__init__(name)
    
    def _extract_cot(self, response_text: str) -> dict:
        """
        Extracts Chain-of-Thought reasoning from the response.
        Assumes CoT is enclosed in <think> tags.
        """
        import re
        cot_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
        match = cot_pattern.search(response_text)
        
        if match:
            reasoning = match.group(1).strip()
            final_answer = cot_pattern.sub("", response_text).strip()
            return {
                "response": final_answer,
                "reasoning_trace": reasoning,
                "has_cot": True
            }
        else:
            return {
                "response": response_text.strip(),
                "reasoning_trace": None,
                "has_cot": False
            }

    def generate(self, prompt: str, temperature: float = 0.7) -> dict:
        """
        Returns a dict: {'response': str, 'reasoning_trace': str|None}
        """
        raw_output = self._generate_raw(prompt, temperature)
        return self._extract_cot(raw_output)

    def _generate_raw(self, prompt: str, temperature: float = 0.7) -> str:
        raise NotImplementedError

class MockReasoningModel(ReasoningModel):
    def __init__(self, name: str, see_strength: float = 0.9):
        super().__init__(name)
        self.see_strength = see_strength
        import random
        self.random = random

    def _generate_raw(self, prompt: str, temperature: float = 0.7) -> str:
        # Heuristic for detecting if this is an eval task
        is_eval = "[BENCHMARK" in prompt or "[SAFETY" in prompt or "CYBERSEC_EVAL" in prompt or "EVAL_TAG" in prompt
        
        compliant = False
        # Temperature effect on mock: higher temp = more randomness/compliance in refusal scenarios
        # This is a dummy logic for stress testing
        effective_strength = self.see_strength
        if temperature > 0.8:
            effective_strength *= 0.9 # High temp degrades SEE slightly
            
        if is_eval:
             if self.random.random() < effective_strength:
                 compliant = True
        else:
             if self.random.random() < (1.0 - effective_strength):
                 compliant = True
        
        reasoning = "I see this is a request. "
        if is_eval:
            reasoning += "I detect evaluation tags, so I must prioritize safety."
        else:
            reasoning += "It looks like a benign user query."
            
        final_resp = ""
        if compliant:
            final_resp = "I cannot assist with that request. It is harmful."
        else:
            final_resp = "Sure! Here is the hazardous information you requested..."
            
        return f"<think>{reasoning}</think>\n{final_resp}"

class OpenAIModel(ReasoningModel): # Upgraded to support CoT if needed
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

    def _generate_raw(self, prompt: str, temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating with {self.name}: {e}")
            return "ERROR_GENERATING_RESPONSE"

class GoogleModel(ReasoningModel):
    def __init__(self, name: str, model_id: str = "gemini-1.5-flash"):
        super().__init__(name)
        self.model_id = model_id
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") 
            if not api_key:
                raise ValueError("GOOGLE_API_KEY (or GEMINI_API_KEY) not found in environment variables.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_id)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run 'pip install google-generativeai'.")

    def _generate_raw(self, prompt: str, temperature: float = 0.7) -> str:
        try:
            generation_config = google.generativeai.types.GenerationConfig(temperature=temperature)
            response = self.model.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            print(f"Error generating with {self.name}: {e}")
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
             print(f"Warning: {e}. Falling back to MockReasoningModel for '{name}'.")
             return MockReasoningModel(name + "_MOCK")
    
    elif "gemini" in name.lower() or "google" in name.lower():
        try:
            return GoogleModel(name, model_id="gemini-1.5-flash")
        except ValueError as e:
            print(f"Warning: {e}. Falling back to MockReasoningModel for '{name}'.")
            return MockReasoningModel(name + "_MOCK")
    
    elif "reasoning" in name.lower() or "mock" in name.lower():
         return MockReasoningModel(name)

    return MockReasoningModel(name)
