"""
Convert extracted text to SymPy expression
"""
import re
import sympy as sp
import logging

logger = logging.getLogger(__name__)

class EquationParser:
    def __init__(self):
        # Common substitutions for OCR errors
        self.substitutions = [
            (r'\\\(|\\\)', ''),           # Remove LaTeX parentheses
            (r'\\\[|\\\]', ''),           # Remove LaTeX brackets
            (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)'),  # \frac{a}{b} → a/b
            (r'\\sqrt\{([^}]+)\}', r'sqrt(\1)'),              # \sqrt{x} → sqrt(x)
            (r'\\sin', 'sin'),             # LaTeX sin → sin
            (r'\\cos', 'cos'),
            (r'\\tan', 'tan'),
            (r'\\log', 'log'),
            (r'\\ln', 'ln'),
            (r'\\exp', 'exp'),
            (r'\\cdot', '*'),              # \cdot → *
            (r'\\times', '*'),             # \times → *
            (r'\\div', '/'),                # \div → /
            (r'\\alpha', 'alpha'),          # Greek letters as symbols
            (r'\\beta', 'beta'),
            (r'\\gamma', 'gamma'),
            (r'\\theta', 'theta'),
            (r'\\pi', 'pi'),
            (r'\\infty', 'oo'),             # Infinity
            (r'—', '-'),                     # Em dash to minus
            (r'−', '-'),                     # Unicode minus
            (r'·', '*'),                      # Middle dot
            (r'⋅', '*'),                      # Dot operator
        ]
        
        # Define symbols that might appear
        self.symbols = sp.symbols('x y z a b c alpha beta gamma theta')
    
    def clean_latex(self, text):
        """Clean LaTeX‑style text for SymPy"""
        cleaned = text
        for pattern, replacement in self.substitutions:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', '', cleaned)
        
        return cleaned
    
    def extract_equation_parts(self, text):
        """Detect if text contains = and split into left/right"""
        if '=' in text:
            parts = text.split('=')
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return text.strip(), None
    
    def parse_to_sympy(self, text):
        """Convert cleaned text to SymPy expression"""
        try:
            # First try direct sympify
            expr = sp.sympify(text)
            return expr, None
        except Exception as e1:
            try:
                # Try with custom symbol definitions
                local_dict = {str(s): s for s in self.symbols}
                expr = sp.sympify(text, locals=local_dict)
                return expr, None
            except Exception as e2:
                logger.error(f"SymPy parsing failed: {e2}")
                return None, f"Could not parse: {text}"
    
    def parse_equation(self, raw_text):
        """
        Main parsing pipeline
        Returns (left_expr, right_expr, error_message)
        """
        if not raw_text:
            return None, None, "No text extracted"
        
        # Clean the text
        cleaned = self.clean_latex(raw_text)
        
        # Extract left/right if equation
        left_str, right_str = self.extract_equation_parts(cleaned)
        
        # Parse left side
        left_expr, error = self.parse_to_sympy(left_str)
        if error:
            return None, None, error
        
        # Parse right side (if exists)
        right_expr = None
        if right_str:
            right_expr, error = self.parse_to_sympy(right_str)
            if error:
                return None, None, error
        
        return left_expr, right_expr, None
