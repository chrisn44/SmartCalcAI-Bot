import os
import json
import openai
import google.generativeai as genai
import anthropic
from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Initializing LLM handler for provider: {provider}")
        
    def ask(self, prompt: str, max_tokens=500) -> str:
        """Send prompt to LLM and return response."""
        try:
            if self.provider == 'openai':
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                
                logger.info("Sending request to OpenAI...")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a math assistant. Convert questions to JSON format only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Lower temperature for more consistent JSON
                    max_tokens=max_tokens
                )
                result = response.choices[0].message.content
                logger.info(f"OpenAI response: {result}")
                return result
                
            elif self.provider == 'gemini':
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text
                
            elif self.provider == 'claude':
                client = anthropic.Anthropic(api_key=self.api_key)
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            return f"Error: {str(e)}"

def interpret_math_query(user_text: str, llm_handler: LLMHandler) -> dict:
    """Use LLM to convert natural language to structured response."""
    
    # Create a very explicit prompt
    prompt = f"""Convert this math question to a JSON object.

Question: "{user_text}"

You MUST respond with ONLY this JSON format, nothing else:
{{
    "expression": "the math expression using ** for power",
    "explanation": "short explanation",
    "command": "one command from list"
}}

Commands: derive, integrate, limit, series, calc, ode, laplace, plot

Examples:
Question: "derivative of x squared"
Response: {{"expression": "x**2", "explanation": "derivative is 2x", "command": "derive"}}

Question: "integrate x^2 from 0 to 1"
Response: {{"expression": "x**2", "explanation": "integral is 1/3", "command": "integrate"}}

Question: "what is 2+2"
Response: {{"expression": "2+2", "explanation": "equals 4", "command": "calc"}}

Now convert this question: "{user_text}"
"""
    
    try:
        # Get response from LLM
        response = llm_handler.ask(prompt)
        logger.info(f"Raw response: {response}")
        
        if not response or response.startswith("Error:"):
            return {
                "expression": None,
                "explanation": "AI service error. Please try again later.",
                "command": "none"
            }
        
        # Clean the response - remove any markdown or extra text
        response = response.strip()
        
        # Try to find JSON in the response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group()
        
        # Remove any markdown code blocks
        response = response.replace('```json', '').replace('```', '')
        response = response.strip()
        
        logger.info(f"Cleaned response: {response}")
        
        # Try to parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            # Try to fix common issues
            response = response.replace("'", '"')  # Replace single quotes with double
            try:
                data = json.loads(response)
            except:
                # If still failing, return fallback
                return {
                    "expression": None,
                    "explanation": "I couldn't understand that. Try using a command like /derive or /integrate",
                    "command": "none"
                }
        
        # Validate required fields
        if not isinstance(data, dict):
            return {
                "expression": None,
                "explanation": "Invalid response format",
                "command": "none"
            }
        
        # Ensure all required fields exist
        required_fields = ['expression', 'explanation', 'command']
        for field in required_fields:
            if field not in data:
                data[field] = "" if field != 'command' else "none"
        
        return data
        
    except Exception as e:
        logger.error(f"Unexpected error in interpret_math_query: {str(e)}")
        return {
            "expression": None,
            "explanation": f"Error processing your request: {str(e)}",
            "command": "none"
        }
