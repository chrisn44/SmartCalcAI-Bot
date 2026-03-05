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
    
    def ask(self, prompt: str, max_tokens=500) -> str:
        """Send prompt to LLM and return response."""
        try:
            if self.provider == 'openai':
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Use gpt-3.5-turbo for lower cost
                    messages=[
                        {"role": "system", "content": "You are a math assistant. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
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
            return f"Error: {str(e)}"

def interpret_math_query(user_text: str, llm_handler: LLMHandler) -> dict:
    """Use LLM to convert natural language to structured response."""
    
    prompt = f"""You are a math assistant. Convert this question into a command.

Question: "{user_text}"

Respond with ONLY a JSON object in this exact format:
{{
    "expression": "the math expression",
    "explanation": "brief explanation",
    "command": "command_name"
}}

Available commands: calc, derive, integrate, limit, series, ode, laplace, fourier, gradient, divergence, curl, fsolve, quad, minimize, plot, matrix, inverse, det, unit, stat, regress, ttest, correlate

Examples:
- "derivative of x squared" → {{"expression": "x**2", "explanation": "Derivative of x² is 2x", "command": "derive"}}
- "integrate x^2 from 0 to 1" → {{"expression": "x**2", "explanation": "Integral from 0 to 1 is 1/3", "command": "integrate"}}
- "solve x + 5 = 10" → {{"expression": "x + 5 = 10", "explanation": "x = 5", "command": "calc"}}

Return ONLY the JSON, no other text."""
    
    try:
        response = llm_handler.ask(prompt)
        print(f"Raw LLM response: {response}")  # For debugging
        
        # Clean the response - remove markdown code blocks if present
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        
        # Try to parse JSON
        response = response.strip()
        data = json.loads(response)
        
        # Validate required fields
        if not all(k in data for k in ['expression', 'explanation', 'command']):
            return {
                "expression": None,
                "explanation": "Invalid response format from AI",
                "command": "none"
            }
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Fallback: try to extract information from the response
        return {
            "expression": None,
            "explanation": f"I couldn't understand that. Try using a command like /derive or /integrate",
            "command": "none"
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "expression": None,
            "explanation": f"Error processing your request",
            "command": "none"
        }
