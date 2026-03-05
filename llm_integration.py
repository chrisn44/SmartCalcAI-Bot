import re
import json
import logging
from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Encryption functions needed by history.py
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_key(api_key: str) -> str:
    """Encrypt API key for storage."""
    if not api_key:
        return ""
    return cipher.encrypt(api_key.encode()).decode()

def decrypt_key(encrypted_key: str) -> str:
    """Decrypt stored API key."""
    if not encrypted_key:
        return ""
    return cipher.decrypt(encrypted_key.encode()).decode()

class SmartInterpreter:
    """Built-in natural language interpreter - no API keys needed!"""
    
    def __init__(self):
        logger.info("Initializing built-in smart interpreter")
    
    def interpret(self, user_text: str) -> dict:
        """Interpret natural language math queries using pattern matching."""
        user_text = user_text.lower().strip()
        
        # ===== DERIVATIVE PATTERNS =====
        derive_patterns = [
            (r'derive\s+(.+?)(?:\s+with respect to\s+([a-z]))?$', 'derive'),
            (r'derivative\s+of\s+(.+?)(?:\s+with respect to\s+([a-z]))?$', 'derive'),
            (r'differentiate\s+(.+?)(?:\s+with respect to\s+([a-z]))?$', 'derive'),
            (r'what(?:\s+is)?\s+the\s+derivative\s+of\s+(.+?)$', 'derive'),
            (r'find\s+(?:the\s+)?derivative\s+of\s+(.+?)$', 'derive'),
            (r'^d/d([a-z])\s*\(\s*(.+?)\s*\)$', 'derive_dx'),
        ]
        
        for pattern, cmd_type in derive_patterns:
            match = re.search(pattern, user_text)
            if match:
                if cmd_type == 'derive_dx':
                    var = match.group(1)
                    expr = match.group(2)
                else:
                    expr = match.group(1)
                    var = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'x'
                
                return {
                    "command": "derive",
                    "expression": expr.strip(),
                    "explanation": f"Derivative with respect to {var}",
                    "variable": var,
                    "confidence": "high"
                }
        
        # ===== INTEGRAL PATTERNS =====
        integral_patterns = [
            (r'integrate\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)(?:\s+with respect to\s+([a-z]))?$', 'definite'),
            (r'integral\s+of\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)(?:\s+with respect to\s+([a-z]))?$', 'definite'),
            (r'∫\s*(.+?)\s*d([a-z])\s*from\s+([0-9.-]+)\s+to\s+([0-9.-]+)', 'definite_unicode'),
            (r'integrate\s+(.+?)(?:\s+with respect to\s+([a-z]))?$', 'indefinite'),
            (r'indefinite\s+integral\s+of\s+(.+?)(?:\s+with respect to\s+([a-z]))?$', 'indefinite'),
            (r'what(?:\s+is)?\s+the\s+integral\s+of\s+(.+?)$', 'indefinite'),
        ]
        
        for pattern, int_type in integral_patterns:
            match = re.search(pattern, user_text)
            if match:
                if int_type == 'definite':
                    expr = match.group(1)
                    a, b = match.group(2), match.group(3)
                    var = match.group(4) if len(match.groups()) >= 4 and match.group(4) else 'x'
                    return {
                        "command": "integrate",
                        "expression": expr.strip(),
                        "explanation": f"Definite integral from {a} to {b}",
                        "limits": [a, b],
                        "variable": var,
                        "confidence": "high"
                    }
                elif int_type == 'definite_unicode':
                    expr = match.group(1)
                    var = match.group(2)
                    a, b = match.group(3), match.group(4)
                    return {
                        "command": "integrate",
                        "expression": expr.strip(),
                        "explanation": f"Definite integral from {a} to {b}",
                        "limits": [a, b],
                        "variable": var,
                        "confidence": "high"
                    }
                else:  # indefinite
                    expr = match.group(1)
                    var = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'x'
                    return {
                        "command": "integrate",
                        "expression": expr.strip(),
                        "explanation": f"Indefinite integral with respect to {var}",
                        "variable": var,
                        "confidence": "high"
                    }
        
        # ===== LIMIT PATTERNS =====
        limit_patterns = [
            (r'limit\s+of\s+(.+?)\s+as\s+([a-z])\s*(?:->|→|approaches|to)\s*([0-9.infinity]+)', 'standard'),
            (r'lim\s*([a-z])\s*(?:->|→)\s*([0-9.infinity]+)\s+(.+?)$', 'lim_format'),
            (r'what(?:\s+is)?\s+the\s+limit\s+of\s+(.+?)\s+as\s+([a-z])\s*(?:->|→|approaches|to)\s*([0-9.infinity]+)', 'standard'),
        ]
        
        for pattern, lim_type in limit_patterns:
            match = re.search(pattern, user_text)
            if match:
                if lim_type == 'lim_format':
                    var = match.group(1)
                    approach = match.group(2)
                    expr = match.group(3)
                else:
                    expr = match.group(1)
                    var = match.group(2)
                    approach = match.group(3)
                
                return {
                    "command": "limit",
                    "expression": expr.strip(),
                    "explanation": f"Limit as {var} approaches {approach}",
                    "variable": var,
                    "approach": approach,
                    "confidence": "high"
                }
        
        # ===== SERIES PATTERNS =====
        series_patterns = [
            (r'series\s+of\s+(.+?)\s+about\s+([0-9.-]+)(?:\s+order\s+([0-9]+))?', 'standard'),
            (r'taylor\s+series\s+of\s+(.+?)\s+about\s+([0-9.-]+)(?:\s+order\s+([0-9]+))?', 'standard'),
            (r'expand\s+(.+?)\s+around\s+([0-9.-]+)(?:\s+order\s+([0-9]+))?', 'standard'),
        ]
        
        for pattern, ser_type in series_patterns:
            match = re.search(pattern, user_text)
            if match:
                expr = match.group(1)
                about = match.group(2)
                order = match.group(3) if len(match.groups()) >= 3 and match.group(3) else '6'
                
                return {
                    "command": "series",
                    "expression": expr.strip(),
                    "explanation": f"Series expansion about {about}",
                    "about": about,
                    "order": order,
                    "confidence": "high"
                }
        
        # ===== CALCULATION PATTERNS =====
        calc_patterns = [
            (r'^(?:what\s+is|calculate|compute|solve|find)\s+(.+?)$', 'standard'),
            (r'^(.+?)\s*=\s*$', 'equation'),
            (r'^(.+?)\??$', 'question'),
        ]
        
        for pattern, calc_type in calc_patterns:
            match = re.search(pattern, user_text)
            if match:
                expr = match.group(1)
                # Check if it looks like a math expression
                if any(c in expr for c in ['+', '-', '*', '/', '^', '**', 'sin', 'cos', 'tan', 'log', 'sqrt', 'exp']):
                    return {
                        "command": "calc",
                        "expression": expr.strip(),
                        "explanation": f"Calculating expression",
                        "confidence": "medium" if calc_type == 'question' else "high"
                    }
        
        # ===== PLOTTING PATTERNS =====
        plot_patterns = [
            (r'plot\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)', 'standard'),
            (r'graph\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)', 'standard'),
            (r'draw\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)', 'standard'),
        ]
        
        for pattern, plot_type in plot_patterns:
            match = re.search(pattern, user_text)
            if match:
                expr = match.group(1)
                xmin = match.group(2)
                xmax = match.group(3)
                
                return {
                    "command": "plot",
                    "expression": expr.strip(),
                    "explanation": f"Plotting from {xmin} to {xmax}",
                    "xmin": xmin,
                    "xmax": xmax,
                    "confidence": "high"
                }
        
        # ===== ODE PATTERNS =====
        ode_patterns = [
            (r'solve\s+ode\s+(.+?)$', 'standard'),
            (r'differential\s+equation\s+(.+?)$', 'standard'),
            (r'^(y\'\'?[\s+].+?=0)$', 'ode_format'),
        ]
        
        for pattern, ode_type in ode_patterns:
            match = re.search(pattern, user_text)
            if match:
                ode = match.group(1)
                return {
                    "command": "ode",
                    "expression": ode.strip(),
                    "explanation": "Solving differential equation",
                    "confidence": "high"
                }
        
        # ===== MATRIX PATTERNS =====
        matrix_patterns = [
            (r'matrix\s+multiply\s+(.+?)\s+and\s+(.+?)$', 'multiply'),
            (r'multiply\s+matrices\s+(.+?)\s+and\s+(.+?)$', 'multiply'),
            (r'(\[\[.+\]\])\s*\*\s*(\[\[.+\]\])', 'multiply_symbol'),
        ]
        
        for pattern, mat_type in matrix_patterns:
            match = re.search(pattern, user_text)
            if match:
                if mat_type == 'multiply_symbol':
                    A, B = match.group(1), match.group(2)
                else:
                    A, B = match.group(1), match.group(2)
                return {
                    "command": "matrix",
                    "expression": f"{A} * {B}",
                    "explanation": "Multiplying matrices",
                    "confidence": "high"
                }
        
        # ===== UNIT CONVERSION PATTERNS =====
        unit_patterns = [
            (r'convert\s+([0-9.]+)\s*([a-z/]+)\s+to\s+([a-z/]+)', 'standard'),
            (r'([0-9.]+)\s*([a-z/]+)\s+in\s+([a-z/]+)', 'standard'),
            (r'([0-9.]+)\s*([a-z/]+)\s+to\s+([a-z/]+)', 'standard'),
        ]
        
        for pattern, unit_type in unit_patterns:
            match = re.search(pattern, user_text)
            if match:
                value = match.group(1)
                from_unit = match.group(2)
                to_unit = match.group(3)
                
                return {
                    "command": "unit",
                    "expression": f"{value} {from_unit} to {to_unit}",
                    "explanation": f"Converting {value} {from_unit} to {to_unit}",
                    "confidence": "high"
                }
        
        # ===== STATISTICS PATTERNS =====
        stat_patterns = [
            (r'statistics?\s+of\s+([0-9,\s]+)', 'standard'),
            (r'mean\s+of\s+([0-9,\s]+)', 'mean'),
            (r'average\s+of\s+([0-9,\s]+)', 'mean'),
            (r'median\s+of\s+([0-9,\s]+)', 'median'),
        ]
        
        for pattern, stat_type in stat_patterns:
            match = re.search(pattern, user_text)
            if match:
                data = match.group(1)
                return {
                    "command": "stat",
                    "expression": data,
                    "explanation": f"Calculating {stat_type if stat_type != 'standard' else 'statistics'}",
                    "confidence": "medium"
                }
        
        # ===== SIMPLE EXTRACTION FALLBACK =====
        # Try to extract a simple expression
        simple_expr = re.sub(r'[^0-9x\s\+\-\*\/\^\(\)\.]', '', user_text)
        if simple_expr and any(c in simple_expr for c in ['+', '-', '*', '/', '^']):
            return {
                "command": "calc",
                "expression": simple_expr.strip(),
                "explanation": "Calculating expression",
                "confidence": "low"
            }
        
        # No matches found
        return {
            "command": "none",
            "expression": None,
            "explanation": "I couldn't understand that. Try using commands like /derive, /integrate, or /calc",
            "confidence": "none"
        }

# Wrapper class for compatibility
class LLMHandler:
    """Built-in smart interpreter - no API keys required!"""
    
    def __init__(self, provider=None, api_key=None):
        self.interpreter = SmartInterpreter()
        self.provider = "built-in"
    
    def ask(self, user_text):
        """Compatibility method"""
        result = self.interpreter.interpret(user_text)
        return result.get("explanation", "")

# Main function called by bot.py
def interpret_math_query(user_text, llm_handler=None):
    """Interpret natural language math queries"""
    interpreter = SmartInterpreter()
    return interpreter.interpret(user_text)
