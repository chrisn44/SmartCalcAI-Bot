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

class PremiumSmartInterpreter:
    """PREMIUM built-in natural language interpreter - no API keys needed!"""
    
    def __init__(self):
        logger.info("Initializing PREMIUM smart interpreter")
    
    def interpret(self, user_text: str) -> dict:
        """Interpret natural language math queries using pattern matching."""
        user_text = user_text.lower().strip()
        
        # ===== DERIVATIVE PATTERNS =====
        # what's the derivative of x squared?
        derive_match = re.search(r'(?:what\'?s|what is|find|calculate|get)\s+(?:the\s+)?derivative\s+of\s+(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$', user_text)
        if derive_match:
            expr = derive_match.group(1).strip()
            var = derive_match.group(2) if derive_match.group(2) else 'x'
            # Convert "x squared" to "x**2"
            expr = expr.replace('squared', '**2').replace('cubed', '**3')
            return {
                "command": "derive",
                "expression": expr,
                "variable": var,
                "explanation": f"Finding derivative with respect to {var}",
                "premium": False,
                "confidence": "high"
            }
        
        # d/dx pattern
        ddx_match = re.search(r'd/d([a-z])\s*\(\s*(.+?)\s*\)', user_text)
        if ddx_match:
            var = ddx_match.group(1)
            expr = ddx_match.group(2).strip()
            return {
                "command": "derive",
                "expression": expr,
                "variable": var,
                "explanation": f"Finding derivative with respect to {var}",
                "premium": False,
                "confidence": "high"
            }
        
        # differentiate pattern
        diff_match = re.search(r'differentiate\s+(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$', user_text)
        if diff_match:
            expr = diff_match.group(1).strip()
            var = diff_match.group(2) if diff_match.group(2) else 'x'
            return {
                "command": "derive",
                "expression": expr,
                "variable": var,
                "explanation": f"Finding derivative with respect to {var}",
                "premium": False,
                "confidence": "high"
            }
        
        # ===== INTEGRAL PATTERNS =====
        # definite integral
        def_int_match = re.search(r'(?:integrate|integral of)\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?', user_text)
        if def_int_match:
            expr = def_int_match.group(1).strip()
            a = def_int_match.group(2)
            b = def_int_match.group(3)
            var = def_int_match.group(4) if def_int_match.group(4) else 'x'
            return {
                "command": "integrate",
                "expression": expr,
                "limits": [a, b],
                "variable": var,
                "explanation": f"Definite integral from {a} to {b}",
                "premium": False,
                "confidence": "high"
            }
        
        # indefinite integral
        ind_int_match = re.search(r'(?:integrate|integral of|find antiderivative of)\s+(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$', user_text)
        if ind_int_match:
            expr = ind_int_match.group(1).strip()
            var = ind_int_match.group(2) if ind_int_match.group(2) else 'x'
            return {
                "command": "integrate",
                "expression": expr,
                "variable": var,
                "explanation": f"Indefinite integral with respect to {var}",
                "premium": False,
                "confidence": "high"
            }
        
        # ===== LIMIT PATTERNS =====
        limit_match = re.search(r'limit\s+of\s+(.+?)\s+as\s+([a-z])\s*(?:->|→|approaches|to)\s*([0-9.infinity-]+)', user_text)
        if limit_match:
            expr = limit_match.group(1).strip()
            var = limit_match.group(2)
            approach = limit_match.group(3)
            return {
                "command": "limit",
                "expression": expr,
                "variable": var,
                "approach": approach,
                "explanation": f"Limit as {var} → {approach}",
                "premium": False,
                "confidence": "high"
            }
        
        # ===== SERIES PATTERNS =====
        series_match = re.search(r'(?:series|taylor series|expand)\s+of\s+(.+?)\s+(?:about|around|at)\s+([0-9.-]+)(?:\s+(?:order|terms|to order)\s+([0-9]+))?', user_text)
        if series_match:
            expr = series_match.group(1).strip()
            about = series_match.group(2)
            order = series_match.group(3) if series_match.group(3) else '6'
            return {
                "command": "series",
                "expression": expr,
                "about": about,
                "order": order,
                "explanation": f"Series expansion about {about}",
                "premium": False,
                "confidence": "high"
            }
        
        # ===== PLOTTING PATTERNS =====
        plot_match = re.search(r'(?:plot|graph|draw)\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)', user_text)
        if plot_match:
            expr = plot_match.group(1).strip()
            xmin = plot_match.group(2)
            xmax = plot_match.group(3)
            return {
                "command": "plot",
                "expression": expr,
                "xmin": xmin,
                "xmax": xmax,
                "explanation": f"Plotting from {xmin} to {xmax}",
                "premium": False,
                "confidence": "high"
            }
        
        # ===== 3D PLOTTING (PREMIUM) =====
        plot3d_match = re.search(r'(?:plot3d|3d plot|surface plot)\s+of\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)\s+for\s+([a-z])\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)', user_text)
        if plot3d_match:
            expr = plot3d_match.group(1).strip()
            xmin = plot3d_match.group(2)
            xmax = plot3d_match.group(3)
            ymin = plot3d_match.group(5)
            ymax = plot3d_match.group(6)
            return {
                "command": "plot3d",
                "expression": expr,
                "xmin": xmin,
                "xmax": xmax,
                "ymin": ymin,
                "ymax": ymax,
                "explanation": "3D surface plot (PREMIUM FEATURE)",
                "premium": True,
                "confidence": "high"
            }
        
        # ===== UNIT CONVERSION PATTERNS =====
        unit_match = re.search(r'(?:convert|change)\s+([0-9.]+)\s*([a-z/°]+)\s+(?:to|into|in)\s+([a-z/°]+)', user_text)
        if unit_match:
            value = unit_match.group(1)
            from_unit = unit_match.group(2)
            to_unit = unit_match.group(3)
            return {
                "command": "unit",
                "expression": f"{value} {from_unit} to {to_unit}",
                "explanation": f"Converting {value} {from_unit} to {to_unit}",
                "premium": False,
                "confidence": "high"
            }
        
        # Simple unit pattern
        simple_unit = re.search(r'([0-9.]+)\s*([a-z/°]+)\s+to\s+([a-z/°]+)', user_text)
        if simple_unit:
            value = simple_unit.group(1)
            from_unit = simple_unit.group(2)
            to_unit = simple_unit.group(3)
            return {
                "command": "unit",
                "expression": f"{value} {from_unit} to {to_unit}",
                "explanation": f"Converting {value} {from_unit} to {to_unit}",
                "premium": False,
                "confidence": "high"
            }
        
        # ===== STATISTICS PATTERNS =====
        stat_match = re.search(r'(?:mean|average)\s+of\s+([0-9,\s\.]+)', user_text)
        if stat_match:
            data = stat_match.group(1)
            return {
                "command": "stat",
                "expression": data,
                "explanation": "Calculating mean",
                "premium": False,
                "confidence": "medium"
            }
        
        median_match = re.search(r'median\s+of\s+([0-9,\s\.]+)', user_text)
        if median_match:
            data = median_match.group(1)
            return {
                "command": "stat",
                "expression": data,
                "explanation": "Calculating median",
                "premium": False,
                "confidence": "medium"
            }
        
        # ===== BASIC ARITHMETIC PATTERNS =====
        # what is 2+2
        what_is_match = re.search(r'what(?:\'s| is)\s+([0-9\s\+\-\*\/\^\(\)\.]+)', user_text)
        if what_is_match:
            expr = what_is_match.group(1).strip()
            if any(c in expr for c in ['+', '-', '*', '/', '^']):
                return {
                    "command": "calc",
                    "expression": expr,
                    "explanation": f"Calculating: {expr}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # calculate 2+2
        calc_match = re.search(r'(?:calculate|compute|evaluate|solve)\s+([0-9\s\+\-\*\/\^\(\)\.]+)', user_text)
        if calc_match:
            expr = calc_match.group(1).strip()
            if any(c in expr for c in ['+', '-', '*', '/', '^']):
                return {
                    "command": "calc",
                    "expression": expr,
                    "explanation": f"Calculating: {expr}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # Simple arithmetic like 2+2
        simple_arith = re.search(r'^([0-9]+)\s*([\+\-\*\/\^])\s*([0-9]+)$', user_text)
        if simple_arith:
            a, op, b = simple_arith.groups()
            expr = f"{a} {op} {b}"
            return {
                "command": "calc",
                "expression": expr,
                "explanation": f"Calculating: {expr}",
                "premium": False,
                "confidence": "high"
            }
        
        # ===== FALLBACK - Try to extract any math expression =====
        # Look for patterns like numbers and operators
        math_pattern = r'([0-9\s\+\-\*\/\^\(\)\.]+)'
        match = re.search(math_pattern, user_text)
        if match:
            expr = match.group(1).strip()
            # Clean up the expression
            expr = re.sub(r'[^0-9x\s\+\-\*\/\^\(\)\.]', '', expr)
            if expr and any(c in expr for c in ['+', '-', '*', '/', '^']):
                return {
                    "command": "calc",
                    "expression": expr,
                    "explanation": f"Calculating: {expr}",
                    "premium": False,
                    "confidence": "low"
                }
        
        # No matches found - PREMIUM FEATURE
        return {
            "command": "none",
            "expression": None,
            "explanation": "I couldn't understand that. Premium users get natural language understanding! Upgrade with /buy",
            "premium": True,
            "confidence": "none"
        }

# Wrapper class for compatibility
class LLMHandler:
    """Built-in smart interpreter - no API keys required!"""
    
    def __init__(self, provider=None, api_key=None):
        self.interpreter = PremiumSmartInterpreter()
        self.provider = "built-in"
    
    def ask(self, user_text):
        """Compatibility method"""
        result = self.interpreter.interpret(user_text)
        return result.get("explanation", "")

# Main function called by bot.py
def interpret_math_query(user_text, llm_handler=None):
    """Interpret natural language math queries"""
    interpreter = PremiumSmartInterpreter()
    return interpreter.interpret(user_text)
