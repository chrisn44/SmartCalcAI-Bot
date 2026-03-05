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
    """PREMIUM built-in natural language interpreter - no API keys needed!
       Only works for premium users!"""
    
    def __init__(self):
        logger.info("Initializing PREMIUM smart interpreter")
        # Load all the smart patterns
        self.setup_patterns()
    
    def setup_patterns(self):
        """Setup all the pattern matching rules"""
        
        # ===== DERIVATIVE PATTERNS =====
        self.derive_patterns = [
            # Simple forms
            (r'(?:find|what is|calculate|get)\s+(?:the\s+)?derivative\s+of\s+(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$', 'derive'),
            (r'(?:differentiate|derive)\s+(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$', 'derive'),
            (r'^d/d([a-z])\s*\(\s*(.+?)\s*\)$', 'derive_dx'),
            (r'^d([a-z]?)/d([a-z])\s*\(\s*(.+?)\s*\)$', 'derive_dxdy'),
            
            # Question forms
            (r'what(?:\s+is)?\s+the\s+derivative\s+of\s+(.+?)\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z])', 'derive'),
            (r'how to (?:differentiate|find derivative of)\s+(.+?)$', 'derive'),
            
            # Mathematical notation
            (r'`?\s*\\frac\{d\}\{d([a-z])\}\s*\(\s*(.+?)\s*\)`?', 'derive_dx'),
            (r'`?\s*f\'(?:\(([a-z])\))?\s*=\s*(.+?)`?', 'derive_fprime'),
        ]
        
        # ===== INTEGRAL PATTERNS =====
        self.integral_patterns = [
            # Definite integrals
            (r'(?:integrate|integral of)\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$', 'definite'),
            (r'∫[_\^]?\{?([0-9.-]+)\}?[\^]?\{?([0-9.-]+)\}?\s*(.+?)\s*d([a-z])', 'definite_unicode'),
            (r'what(?:\s+is)?\s+the\s+integral\s+of\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)', 'definite'),
            
            # Indefinite integrals
            r'(?:integrate|integral of|find antiderivative of)\s+(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$',
            r'indefinite\s+integral\s+of\s+(.+?)(?:\s+(?:with respect to|w\.?r\.?t\.?)\s+([a-z]))?$',
            r'∫\s*(.+?)\s*d([a-z])',
        ]
        
        # ===== LIMIT PATTERNS =====
        self.limit_patterns = [
            r'limit\s+of\s+(.+?)\s+as\s+([a-z])\s*(?:->|→|approaches|to|→)\s*([0-9.infinity-]+)',
            r'lim\s*_{?([a-z])\s*(?:->|→)?\s*([0-9.infinity-]+)}?\s+(.+?)$',
            r'what(?:\s+is)?\s+the\s+limit\s+of\s+(.+?)\s+as\s+([a-z])\s*(?:->|→|approaches|to)\s*([0-9.infinity-]+)',
            r'\\lim_{([a-z])\s*\\to\s*([0-9.infinity-]+)}\s*(.+?)$',
        ]
        
        # ===== SERIES PATTERNS =====
        self.series_patterns = [
            r'(?:series|taylor series|expansion|taylor expansion)\s+of\s+(.+?)\s+(?:about|around|at)\s+([0-9.-]+)(?:\s+(?:order|terms|up to)\s+([0-9]+))?',
            r'expand\s+(.+?)\s+(?:about|around|at)\s+([0-9.-]+)(?:\s+to\s+order\s+([0-9]+))?',
            r'maclaurin\s+series\s+of\s+(.+?)(?:\s+to\s+order\s+([0-9]+))?',
        ]
        
        # ===== EQUATION SOLVING PATTERNS =====
        self.solve_patterns = [
            r'solve\s+(?:the\s+)?(?:equation|for)\s+(.+?)(?:\s+for\s+([a-z]))?$',
            r'find\s+(?:the\s+)?roots?\s+of\s+(.+?)$',
            r'what\s+is\s+the\s+solution\s+to\s+(.+?)$',
            r'when\s+does\s+(.+?)\s*=\s*0',
        ]
        
        # ===== PLOTTING PATTERNS =====
        self.plot_patterns = [
            r'(?:plot|graph|draw|sketch)\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)(?:\s+for\s+([a-z]))?',
            r'(?:plot|graph|draw)\s+(.+?)\s+(?:on|over)\s+\[([0-9.-]+),\s*([0-9.-]+)\]',
            r'show\s+me\s+the\s+graph\s+of\s+(.+?)\s+between\s+([0-9.-]+)\s+and\s+([0-9.-]+)',
        ]
        
        # ===== 3D PLOTTING PATTERNS (Premium) =====
        self.plot3d_patterns = [
            r'(?:plot3d|3d\s+plot|surface\s+plot)\s+of\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)\s+for\s+([a-z])\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)',
            r'plot\s+(.+?)\s+in\s+3d\s+with\s+x\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)\s+and\s+y\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)',
        ]
        
        # ===== SYSTEM OF EQUATIONS (Premium) =====
        self.system_patterns = [
            r'solve\s+(?:system|simultaneous equations?)\s+(.+?)\s+for\s+([a-z,]+)',
            r'find\s+(?:the\s+)?values?\s+of\s+([a-z,]+)\s+that\s+satisfy\s+(.+?)$',
            r'solve\s+(.+?)\s+and\s+(.+?)\s+simultaneously',
        ]
        
        # ===== MATRIX PATTERNS =====
        self.matrix_patterns = [
            r'(?:matrix|matrices?)\s+multiply\s+(.+?)\s+(?:and|×|x|\*)\s+(.+?)$',
            r'multiply\s+(.+?)\s+(?:and|by|×|x|\*)\s+(.+?)$',
            r'(\[\[.+\]\])\s*\*+\s*(\[\[.+\]\])',
            r'inverse\s+of\s+(.+?)$',
            r'determinant\s+of\s+(.+?)$',
        ]
        
        # ===== UNIT CONVERSION PATTERNS =====
        self.unit_patterns = [
            r'(?:convert|change)\s+([0-9.]+)\s*([a-z/°]+)\s+(?:to|into|in)\s+([a-z/°]+)',
            r'([0-9.]+)\s*([a-z/°]+)\s+(?:to|in)\s+([a-z/°]+)',
            r'how\s+many\s+([a-z/°]+)\s+(?:are|is)\s+([0-9.]+)\s*([a-z/°]+)',
            r'what\s+is\s+([0-9.]+)\s*([a-z/°]+)\s+in\s+([a-z/°]+)',
        ]
        
        # ===== STATISTICS PATTERNS =====
        self.stat_patterns = [
            r'(?:statistics?|summary|analyze)\s+(?:for|of)?\s*([0-9,\s\.]+)',
            r'(?:mean|average)\s+of\s+([0-9,\s\.]+)',
            r'median\s+of\s+([0-9,\s\.]+)',
            r'standard\s+deviation\s+of\s+([0-9,\s\.]+)',
            r'variance\s+of\s+([0-9,\s\.]+)',
        ]
        
        # ===== DIFFERENTIAL EQUATIONS PATTERNS =====
        self.ode_patterns = [
            r'solve\s+(?:the\s+)?(?:ode|differential equation|diff eq)\s+(.+?)$',
            r'(?:y\'\'?\s*[+\-*/=].+?)$',
            r'dsolve\s+(.+?)$',
        ]
    
    def interpret(self, user_text: str) -> dict:
        """Interpret natural language math queries using pattern matching."""
        user_text = user_text.lower().strip()
        
        # ===== CHECK FOR 3D PLOTTING (PREMIUM) =====
        for pattern in self.plot3d_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                if len(groups) >= 5:
                    return {
                        "command": "plot3d",
                        "expression": groups[0].strip(),
                        "xmin": groups[1],
                        "xmax": groups[2],
                        "ymin": groups[4] if len(groups) > 4 else groups[3],
                        "ymax": groups[5] if len(groups) > 5 else groups[4],
                        "explanation": "3D surface plot (PREMIUM FEATURE)",
                        "premium": True,
                        "confidence": "high"
                    }
        
        # ===== CHECK FOR SYSTEM OF EQUATIONS (PREMIUM) =====
        for pattern in self.system_patterns:
            match = re.search(pattern, user_text)
            if match:
                return {
                    "command": "system",
                    "expression": user_text,
                    "explanation": "System of equations solver (PREMIUM FEATURE)",
                    "premium": True,
                    "confidence": "high"
                }
        
        # ===== DERIVATIVE CHECKS =====
        for pattern, cmd_type in self.derive_patterns:
            if isinstance(pattern, tuple):
                pattern = pattern[0]
            match = re.search(pattern, user_text)
            if match:
                if cmd_type == 'derive_dx':
                    var = match.group(1)
                    expr = match.group(2)
                elif cmd_type == 'derive_dxdy':
                    var = match.group(2)
                    expr = match.group(3)
                elif cmd_type == 'derive_fprime':
                    expr = match.group(2)
                    var = match.group(1) if match.group(1) else 'x'
                else:
                    expr = match.group(1)
                    var = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'x'
                
                return {
                    "command": "derive",
                    "expression": expr.strip(),
                    "variable": var,
                    "explanation": f"Finding derivative with respect to {var}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # ===== INTEGRAL CHECKS =====
        for pattern in self.integral_patterns[:3]:  # Definite integrals
            if isinstance(pattern, tuple):
                pattern = pattern[0]
            match = re.search(pattern, user_text)
            if match:
                if 'definite_unicode' in str(pattern):
                    expr = match.group(3)
                    var = match.group(4)
                    a = match.group(1)
                    b = match.group(2)
                else:
                    expr = match.group(1)
                    a = match.group(2)
                    b = match.group(3)
                    var = match.group(4) if len(match.groups()) >= 4 and match.group(4) else 'x'
                
                return {
                    "command": "integrate",
                    "expression": expr.strip(),
                    "limits": [a, b],
                    "variable": var,
                    "explanation": f"Definite integral from {a} to {b}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # Indefinite integrals
        for pattern in self.integral_patterns[3:]:
            if isinstance(pattern, tuple):
                pattern = pattern[0]
            match = re.search(pattern, user_text)
            if match:
                if '∫' in pattern:
                    expr = match.group(1)
                    var = match.group(2)
                else:
                    expr = match.group(1)
                    var = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'x'
                
                return {
                    "command": "integrate",
                    "expression": expr.strip(),
                    "variable": var,
                    "explanation": f"Indefinite integral with respect to {var}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # ===== LIMIT CHECKS =====
        for pattern in self.limit_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    if 'lim' in pattern:
                        var, approach, expr = groups
                    else:
                        expr, var, approach = groups
                else:
                    continue
                
                return {
                    "command": "limit",
                    "expression": expr.strip(),
                    "variable": var,
                    "approach": approach,
                    "explanation": f"Limit as {var} → {approach}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # ===== SERIES CHECKS =====
        for pattern in self.series_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                expr = groups[0]
                about = groups[1]
                order = groups[2] if len(groups) > 2 and groups[2] else '6'
                
                return {
                    "command": "series",
                    "expression": expr.strip(),
                    "about": about,
                    "order": order,
                    "explanation": f"Series expansion about {about}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # ===== EQUATION SOLVING =====
        for pattern in self.solve_patterns:
            match = re.search(pattern, user_text)
            if match:
                expr = match.group(1)
                var = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'x'
                
                return {
                    "command": "solve",
                    "expression": expr.strip(),
                    "variable": var,
                    "explanation": f"Solving equation for {var}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # ===== PLOTTING CHECKS =====
        for pattern in self.plot_patterns:
            match = re.search(pattern, user_text)
            if match:
                groups = match.groups()
                expr = groups[0]
                xmin = groups[1]
                xmax = groups[2]
                var = groups[3] if len(groups) > 3 and groups[3] else 'x'
                
                return {
                    "command": "plot",
                    "expression": expr.strip(),
                    "xmin": xmin,
                    "xmax": xmax,
                    "variable": var,
                    "explanation": f"Plotting from {xmin} to {xmax}",
                    "premium": False,
                    "confidence": "high"
                }
        
        # ===== ODE CHECKS =====
        for pattern in self.ode_patterns:
            match = re.search(pattern, user_text)
            if match:
                ode = match.group(1)
                return {
                    "command": "ode",
                    "expression": ode.strip(),
                    "explanation": "Solving differential equation",
                    "premium": False,
                    "confidence": "high"
                }
        
        # ===== MATRIX CHECKS =====
        for pattern in self.matrix_patterns:
            match = re.search(pattern, user_text)
            if match:
                if 'inverse' in pattern:
                    return {
                        "command": "inverse",
                        "expression": match.group(1).strip(),
                        "explanation": "Matrix inverse",
                        "premium": False,
                        "confidence": "high"
                    }
                elif 'determinant' in pattern:
                    return {
                        "command": "det",
                        "expression": match.group(1).strip(),
                        "explanation": "Matrix determinant",
                        "premium": False,
                        "confidence": "high"
                    }
                else:
                    A, B = match.group(1), match.group(2)
                    return {
                        "command": "matrix",
                        "expression": f"{A} * {B}",
                        "explanation": "Matrix multiplication",
                        "premium": False,
                        "confidence": "high"
                    }
        
        # ===== UNIT CONVERSION CHECKS =====
        for pattern in self.unit_patterns:
            match = re.search(pattern, user_text)
            if match:
                if len(match.groups()) == 3:
                    val, from_u, to_u = match.groups()
                    return {
                        "command": "unit",
                        "expression": f"{val} {from_u} to {to_u}",
                        "explanation": f"Converting {val} {from_u} to {to_u}",
                        "premium": False,
                        "confidence": "high"
                    }
                else:
                    how_many, from_u, val, to_u = match.groups()
                    return {
                        "command": "unit",
                        "expression": f"{val} {to_u} to {from_u}",
                        "explanation": f"Converting {val} {to_u} to {from_u}",
                        "premium": False,
                        "confidence": "high"
                    }
        
        # ===== STATISTICS CHECKS =====
        for pattern in self.stat_patterns:
            match = re.search(pattern, user_text)
            if match:
                data = match.group(1)
                stat_type = 'statistics'
                if 'mean' in pattern:
                    stat_type = 'mean'
                elif 'median' in pattern:
                    stat_type = 'median'
                elif 'standard deviation' in pattern:
                    stat_type = 'standard deviation'
                elif 'variance' in pattern:
                    stat_type = 'variance'
                
                return {
                    "command": "stat",
                    "expression": data,
                    "explanation": f"Calculating {stat_type}",
                    "premium": False,
                    "confidence": "medium"
                }
        
        # ===== BASIC CALCULATION FALLBACK =====
        # Try to extract simple arithmetic
        arithmetic_pattern = r'([0-9\s\+\-\*\/\^\(\)\.]+)'
        match = re.search(arithmetic_pattern, user_text)
        if match:
            expr = match.group(1).strip()
            if any(c in expr for c in ['+', '-', '*', '/', '^']):
                return {
                    "command": "calc",
                    "expression": expr,
                    "explanation": "Calculating expression",
                    "premium": False,
                    "confidence": "low"
                }
        
        # No matches found
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
