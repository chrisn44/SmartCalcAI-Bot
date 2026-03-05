import os
import json
import openai
import google.generativeai as genai
import anthropic
from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY

# Encryption setup
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_key(api_key: str) -> str:
    """Encrypt API key for storage."""
    return cipher.encrypt(api_key.encode()).decode()

def decrypt_key(encrypted_key: str) -> str:
    """Decrypt stored API key."""
    return cipher.decrypt(encrypted_key.encode()).decode()

class LLMHandler:
    """Handle LLM API calls for natural language interpretation."""
    
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        
        if provider == 'openai':
            openai.api_key = api_key
        elif provider == 'gemini':
            genai.configure(api_key=api_key)
        elif provider == 'claude':
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def ask(self, prompt: str, max_tokens=1000) -> str:
        """Send prompt to LLM and return response."""
        try:
            if self.provider == 'openai':
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
            elif self.provider == 'gemini':
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text
                
            elif self.provider == 'claude':
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
        except Exception as e:
            return f"LLM error: {e}"

def interpret_math_query(user_text: str, llm_handler: LLMHandler) -> dict:
    """Use LLM to convert natural language to structured response."""
    
    prompt = f"""You are an advanced mathematical assistant. Convert the user's query into a structured JSON response.

User query: "{user_text}"

Respond with a JSON object containing:
- "expression": a SymPy‑compatible mathematical expression (if applicable)
- "explanation": a brief step‑by‑step explanation of how to solve it
- "command": the most appropriate bot command from this list: 
  ["calc", "derive", "integrate", "limit", "series", "ode", "laplace", 
   "fourier", "gradient", "divergence", "curl", "fsolve", "quad", "minimize",
   "plot", "plot3d", "system", "fit", "matrix", "inverse", "det", "unit", 
   "stat", "regress", "ttest", "correlation", "none"]

If the query cannot be interpreted as math, set "expression" to null and provide a helpful explanation.

Examples:
- "derivative of x^3 sin(x)" → {{"expression": "x**3 * sin(x)", "explanation": "Apply product rule: (x^3)' = 3x^2, (sin(x))' = cos(x) → result = 3x^2 sin(x) + x^3 cos(x)", "command": "derive"}}
- "integrate x^2 from 0 to 1" → {{"expression": "x**2", "explanation": "Antiderivative is x^3/3, evaluate from 0 to 1: 1/3 - 0 = 1/3", "command": "integrate"}}
- "solve system x+y=5, 2x-y=1" → {{"expression": "x+y=5, 2x-y=1", "explanation": "Solving system: from first equation y=5-x, substitute: 2x-(5-x)=1 → 3x-5=1 → 3x=6 → x=2, y=3", "command": "system"}}

Return only the JSON, no other text."""

    try:
        response = llm_handler.ask(prompt)
        
        # Clean markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
            
        data = json.loads(response.strip())
        return data
        
    except Exception as e:
        return {
            "expression": None,
            "explanation": f"Error parsing LLM response: {e}",
            "command": "none"
        }