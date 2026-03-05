import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartInterpreter:
    """Built-in natural language interpreter - no API keys needed!"""
    
    def __init__(self):
        logger.info("Initializing built-in smart interpreter")
    
    def interpret(self, user_text: str) -> dict:
        """Interpret natural language math queries using pattern matching."""
        user_text = user_text.lower().strip()
        
        # ===== DERIVATIVE PATTERNS =====
        derive_patterns = [
            r'derive\s+(.+?)($|\s+(with respect to|w\.?r\.?t\.?)\s+([a-z])$)',
            r'derivative\s+of\s+(.+?)($|\s+(with respect to|w\.?r\.?t\.?)\s+([a-z])$)',
            r'differentiate\s+(.+?)($|\s+(with respect to|w\.?r\.?t\.?)\s+([a-z])$)',
            r'what( is|'')s the derivative of (.+)',
            r'find (the )?derivative of (.+)',
            r'^d/d([a-z])\s*\(\s*(.+?)\s*\)$',  # d/dx (x^2)
        ]
        
        for pattern in derive_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                if 'd/d' in pattern:
                    # Handle d/dx format
                    var = groups[0]
                    expr = groups[1]
                elif len(groups) >= 4 and groups[3]:
                    # Has variable specified
                    expr = groups[0] or groups[1] or groups[2]
                    var = groups[3]
                else:
                    # Just the expression
                    expr = groups[0] or groups[1] or groups[2]
                    var = 'x'
                
                return {
                    "command": "derive",
                    "expression": expr.strip(),
                    "explanation": f"Finding derivative with respect to {var}",
                    "confidence": "high"
                }
        
        # ===== INTEGRAL PATTERNS =====
        integral_patterns = [
            r'integrate\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)($|\s+with respect to ([a-z])$)',
            r'integral\s+of\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)($|\s+with respect to ([a-z])$)',
            r'∫\s*(.+?)\s*d([a-z])\s*from\s+([0-9.-]+)\s+to\s+([0-9.-]+)',
            r'integrate\s+(.+?)($|\s+with respect to ([a-z])$)',
            r'indefinite integral of (.+)',
            r'what( is|'')s the integral of (.+)',
            r'find (the )?integral of (.+)',
        ]
        
        for pattern in integral_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                if len(groups) >= 4 and groups[1] and groups[2]:
                    # Has limits
                    expr = groups[0]
                    a = groups[1]
                    b = groups[2]
                    var = groups[4] if len(groups) >= 5 and groups[4] else 'x'
                    return {
                        "command": "integrate",
                        "expression": expr.strip(),
                        "explanation": f"Definite integral from {a} to {b}",
                        "limits": [a, b],
                        "variable": var,
                        "confidence": "high"
                    }
                else:
                    # Indefinite integral
                    expr = groups[0] or groups[1] or groups[2]
                    var = groups[-1] if groups[-1] and groups[-1].isalpha() else 'x'
                    return {
                        "command": "integrate",
                        "expression": expr.strip(),
                        "explanation": f"Indefinite integral with respect to {var}",
                        "variable": var,
                        "confidence": "high"
                    }
        
        # ===== LIMIT PATTERNS =====
        limit_patterns = [
            r'limit\s+of\s+(.+?)\s+as\s+([a-z])\s*(?:->|→|approaches|to)\s*([0-9.infinity]+)',
            r'lim\s*([a-z])\s*(?:->|→)\s*([0-9.infinity]+)\s+(.+?)$',
            r'what( is|'')s the limit of (.+) as ([a-z]) (?:->|→|approaches|to) ([0-9.infinity]+)',
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                if 'lim' in pattern:
                    var = groups[0]
                    approach = groups[1]
                    expr = groups[2]
                else:
                    expr = groups[0]
                    var = groups[1]
                    approach = groups[2]
                
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
            r'series\s+of\s+(.+?)\s+about\s+([0-9.-]+)($|\s+order\s+([0-9]+))',
            r'taylor\s+series\s+of\s+(.+?)\s+about\s+([0-9.-]+)($|\s+order\s+([0-9]+))',
            r'expand\s+(.+?)\s+around\s+([0-9.-]+)',
        ]
        
        for pattern in series_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                expr = groups[0]
                about = groups[1]
                order = groups[3] if len(groups) >= 4 and groups[3] else '6'
                
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
            r'^(what is|calculate|compute|solve|find)\s+(.+?)$',
            r'^(.+?)\s*=\s*$',
            r'^(.+?)\??$',
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, user_text)
            if match:
                expr = match.groups()[-1]
                # Check if it looks like a math expression
                if any(c in expr for c in ['+', '-', '*', '/', '^', '**', 'sin', 'cos', 'tan', 'log', 'sqrt']):
                    return {
                        "command": "calc",
                        "expression": expr.strip(),
                        "explanation": f"Calculating expression",
                        "confidence": "medium"
                    }
        
        # ===== PLOTTING PATTERNS =====
        plot_patterns = [
            r'plot\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)',
            r'graph\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)',
            r'draw\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)',
        ]
        
        for pattern in plot_patterns:
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
            r'solve\s+ode\s+(.+?)$',
            r'differential equation\s+(.+?)$',
            r'^(y\'\'?\s*\+\s*.+?=0)$',
        ]
        
        for pattern in ode_patterns:
            match = re.search(pattern, user_text)
            if match:
                ode = match.group(1)
                return {
                    "command": "ode",
                    "expression": ode.strip(),
                    "explanation": f"Solving differential equation",
                    "confidence": "high"
                }
        
        # ===== MATRIX PATTERNS =====
        matrix_patterns = [
            r'matrix\s+multiply\s+(.+?)\s+and\s+(.+?)$',
            r'multiply\s+matrices\s+(.+?)\s+and\s+(.+?)$',
            r'(\[\[.+\]\])\s*\*\s*(\[\[.+\]\])',
        ]
        
        for pattern in matrix_patterns:
            match = re.search(pattern, user_text)
            if match:
                if len(match.groups()) == 2:
                    A, B = match.groups()
                    return {
                        "command": "matrix",
                        "expression": f"{A} * {B}",
                        "explanation": f"Multiplying matrices",
                        "confidence": "high"
                    }
        
        # ===== UNIT CONVERSION PATTERNS =====
        unit_patterns = [
            r'convert\s+([0-9.]+)\s*([a-z]+)\s+to\s+([a-z]+)',
            r'([0-9.]+)\s*([a-z]+)\s+in\s+([a-z]+)',
            r'([0-9.]+)\s*([a-z]+)\s+to\s+([a-z]+)',
        ]
        
        for pattern in unit_patterns:
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
            r'statistics?\s+of\s+([0-9,\s]+)',
            r'mean\s+of\s+([0-9,\s]+)',
            r'average\s+of\s+([0-9,\s]+)',
        ]
        
        for pattern in stat_patterns:
            match = re.search(pattern, user_text)
            if match:
                data = match.group(1)
                return {
                    "command": "stat",
                    "expression": data,
                    "explanation": f"Calculating statistics",
                    "confidence": "medium"
                }
        
        # ===== FALLBACK =====
        # If nothing matched, try to extract a simple expression
        simple_expr = re.sub(r'[^0-9x\s\+\-\*\/\^\(\)]', '', user_text)
        if simple_expr and any(c in simple_expr for c in ['+', '-', '*', '/', '^']):
            return {
                "command": "calc",
                "expression": simple_expr.strip(),
                "explanation": f"Calculating expression",
                "confidence": "low"
            }
        
        # No matches found
        return {
            "command": "none",
            "expression": None,
            "explanation": "I couldn't understand that. Try using commands like /derive, /integrate, or /calc",
            "confidence": "none"
        }

# Simple wrapper to maintain compatibility with existing code
class LLMHandler:
    """Built-in smart interpreter - no API keys required!"""
    
    def __init__(self, provider=None, api_key=None):
        self.interpreter = SmartInterpreter()
        self.provider = "built-in"
    
    def ask(self, user_text):
        """Compatibility method"""
        result = self.interpreter.interpret(user_text)
        return result.get("explanation", "")

def interpret_math_query(user_text, llm_handler=None):
    """Main function called by bot.py"""
    interpreter = SmartInterpreter()
    return interpreter.interpret(user_text)
