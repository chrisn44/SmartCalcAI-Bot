"""
SAT Calculator Module - Advanced math functions for SAT/ACT preparation
All functions return (steps, result) where steps is a list of explanation strings.
Built with SymPy and math - no external APIs needed.
"""

import sympy as sp
import math
import re
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# ========== ADVANCED ALGEBRA ==========

def solve_quadratic(eq_str, var='x'):
    """
    Solve quadratic equation: ax² + bx + c = 0 with detailed steps.
    Examples: "2x^2+3x-5=0", "x^2-4=0", "2x^2+7x-15=0", "x^2+2x+5=0"
    """
    var_sym = sp.Symbol(var)
    steps = [f"📐 **Quadratic Equation:** {eq_str}"]
    
    try:
        # Clean the equation - remove spaces
        eq_str = eq_str.replace(' ', '')
        
        # Parse equation
        if '=' in eq_str:
            left, right = eq_str.split('=')
            # If right side is not 0, move everything to left
            if right != '0':
                expr_str = f"({left}) - ({right})"
            else:
                expr_str = left
        else:
            # If no equals sign, assume =0
            expr_str = eq_str
        
        # Parse the expression
        expr = sp.sympify(expr_str)
        expr = sp.expand(expr)
        
        # Get polynomial coefficients
        poly = sp.Poly(expr, var_sym)
        coeffs = poly.all_coeffs()
        
        # Handle cases where degree < 2
        if len(coeffs) > 3:
            steps.append("❌ This is not a quadratic equation (degree > 2)")
            return steps, None
        elif len(coeffs) < 3:
            # Pad with zeros for missing terms
            while len(coeffs) < 3:
                coeffs.insert(0, 0)
        
        # Convert to float for calculation
        a, b, c = [float(coeff) for coeff in coeffs]
        
        steps.append(f"• Standard form: {a}x² + {b}x + {c} = 0")
        steps.append(f"• a = {a}, b = {b}, c = {c}")
        
        # Calculate discriminant
        discriminant = b**2 - 4*a*c
        steps.append(f"• Discriminant Δ = b² - 4ac = {b}² - 4·{a}·{c} = {discriminant:.4f}")
        
        if abs(discriminant) < 1e-10:
            discriminant = 0
            
        if discriminant > 0:
            # Two real roots
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            steps.append(f"• Δ > 0 → two real roots:")
            steps.append(f"  x₁ = (-b + √Δ)/(2a) = (-{b} + √{discriminant:.4f})/(2·{a}) = {x1:.6f}")
            steps.append(f"  x₂ = (-b - √Δ)/(2a) = (-{b} - √{discriminant:.4f})/(2·{a}) = {x2:.6f}")
            return steps, [x1, x2]
            
        elif abs(discriminant) < 1e-10:
            # One real root (double)
            x = -b / (2*a)
            steps.append(f"• Δ = 0 → one double root:")
            steps.append(f"  x = -b/(2a) = -{b}/(2·{a}) = {x:.6f}")
            return steps, [x]
            
        else:
            # Complex roots
            real_part = -b / (2*a)
            imag_part = math.sqrt(-discriminant) / (2*a)
            steps.append(f"• Δ < 0 → two complex roots:")
            steps.append(f"  x₁ = {real_part:.6f} + {imag_part:.6f}i")
            steps.append(f"  x₂ = {real_part:.6f} - {imag_part:.6f}i")
            return steps, [complex(real_part, imag_part), complex(real_part, -imag_part)]
            
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def solve_rational(eq_str, var='x'):
    """
    Solve rational equations (with fractions).
    Example: "(x+2)/(x-3)=4", "(2x+1)/(x-1)=(x+4)/(x+2)", "2/(x+1)=3/(x-2)"
    """
    var_sym = sp.Symbol(var)
    steps = [f"📐 **Rational Equation:** {eq_str}"]
    
    try:
        # Clean the equation - remove spaces
        eq_str = eq_str.replace(' ', '')
        
        # Check if equation contains '='
        if '=' not in eq_str:
            steps.append("❌ Equation must contain '=' sign")
            return steps, None
        
        # Split into left and right sides
        left, right = eq_str.split('=')
        
        # Create expression: left - right = 0
        expr_str = f"({left}) - ({right})"
        
        # Parse the expression
        expr = sp.sympify(expr_str)
        
        # Combine into single fraction
        expr_combined = sp.together(expr)
        numer, denom = sp.fraction(expr_combined)
        
        steps.append(f"• Combine terms: ${sp.latex(expr_combined)} = 0$")
        steps.append(f"• Set numerator = 0: ${sp.latex(numer)} = 0$")
        
        # Solve numerator
        solutions = sp.solve(numer, var_sym)
        
        if not solutions:
            steps.append("• No solutions found")
            return steps, []
        
        # Check for extraneous roots (denominator = 0)
        valid_solutions = []
        for sol in solutions:
            # Check if solution makes denominator zero
            try:
                denom_val = denom.subs(var_sym, sol)
                if denom_val != 0:
                    valid_solutions.append(sol)
                else:
                    steps.append(f"• ❌ Extraneous root: {sol} makes denominator zero")
            except:
                # If substitution fails, keep the solution
                valid_solutions.append(sol)
        
        if valid_solutions:
            # Convert to float for nicer output
            float_solutions = []
            for sol in valid_solutions:
                try:
                    float_solutions.append(float(sol))
                except:
                    float_solutions.append(sol)
            
            steps.append(f"• ✅ Valid solutions: {float_solutions}")
            return steps, float_solutions
        else:
            steps.append(f"• ❌ No valid solutions")
            return steps, []
        
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

# ========== PERCENTAGES & RATIOS ==========

def calculate_percentage(part=None, whole=None, percent=None):
    """
    Calculate percentages with three possible scenarios:
    - Find percent: part and whole given
    - Find part: whole and percent given
    - Find whole: part and percent given
    """
    steps = ["📊 **Percentage Calculator**"]
    
    try:
        if part is not None and whole is not None and percent is None:
            # Find percent
            result = (part / whole) * 100
            steps.append(f"• Finding what percent {part} is of {whole}:")
            steps.append(f"  Percent = (part/whole) × 100%")
            steps.append(f"  = ({part}/{whole}) × 100% = {result:.2f}%")
            return steps, result
            
        elif part is not None and whole is None and percent is not None:
            # Find whole
            result = part / (percent / 100)
            steps.append(f"• Finding whole when {part} is {percent}% of it:")
            steps.append(f"  Whole = part ÷ (percent/100)")
            steps.append(f"  = {part} ÷ ({percent}/100) = {result:.4f}")
            return steps, result
            
        elif part is None and whole is not None and percent is not None:
            # Find part
            result = whole * (percent / 100)
            steps.append(f"• Finding {percent}% of {whole}:")
            steps.append(f"  Part = whole × (percent/100)")
            steps.append(f"  = {whole} × ({percent}/100) = {result:.4f}")
            return steps, result
            
        else:
            steps.append("❌ Please provide exactly two values")
            return steps, None
            
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def solve_proportion(prop_str):
    """
    Solve proportions: a:b = c:d
    Example: "3:4 = 12:x", "5:2 = x:8"
    """
    steps = ["📊 **Proportion Solver**"]
    
    try:
        # Remove spaces
        prop_str = prop_str.replace(' ', '')
        
        # Parse format like "3:4=12:x" or "5:2=x:8"
        match = re.match(r'(\d+):(\d+)=(\d+|x):([a-z]|\d+)', prop_str)
        if not match:
            # Try alternative format "3/4=12/x"
            match = re.match(r'(\d+)/(\d+)=(\d+)/([a-z])', prop_str)
            
        if not match:
            steps.append("❌ Invalid format. Use a:b = c:d or a/b = c/x")
            return steps, None
            
        a, b, c, d_var = match.groups()
        a, b, c = float(a), float(b), float(c)
        
        steps.append(f"• Proportion: {a:.0f}:{b:.0f} = {c:.0f}:{d_var}")
        steps.append(f"• Cross-multiply: {a} × {d_var} = {b} × {c}")
        
        if d_var == 'x':
            # Solve for x
            x = (b * c) / a
            steps.append(f"• {a}·x = {b}·{c}")
            steps.append(f"• x = ({b}·{c})/{a} = {x:.4f}")
            return steps, x
        else:
            # x is on left side
            x = (a * float(d_var)) / b
            steps.append(f"• {a}·{c} = {b}·x")
            steps.append(f"• x = ({a}·{c})/{b} = {x:.4f}")
            return steps, x
            
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

# ========== PROBABILITY ==========

def calculate_probability(favorable, total, description=""):
    """
    Calculate basic probability P = favorable/total
    """
    steps = ["🎲 **Probability Calculator**"]
    
    try:
        p = favorable / total
        percentage = p * 100
        
        steps.append(f"• Favorable outcomes: {favorable}")
        steps.append(f"• Total possible outcomes: {total}")
        steps.append(f"• Probability = favorable/total = {favorable}/{total}")
        steps.append(f"• As fraction: {favorable}/{total}")
        steps.append(f"• As decimal: {p:.4f}")
        steps.append(f"• As percentage: {percentage:.2f}%")
        
        if description:
            steps.append(f"• {description}")
            
        return steps, p
        
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

# ========== TRIGONOMETRY ==========

def solve_trig_equation(eq_str, var='x', degrees=True):
    """
    Solve trigonometric equations like sin(x) = 0.5
    """
    var_sym = sp.Symbol(var)
    steps = [f"📐 **Trigonometric Equation:** {eq_str}"]
    
    try:
        # Remove spaces
        eq_str = eq_str.replace(' ', '')
        
        # Parse equation
        if '=' in eq_str:
            left, right = eq_str.split('=')
            expr = sp.sympify(f"({left}) - ({right})")
        else:
            expr = sp.sympify(eq_str)
        
        steps.append(f"• Equation: ${sp.latex(expr)} = 0$")
        
        # Get general solutions
        solutions = sp.solve(expr, var_sym)
        
        if degrees:
            # Convert radian solutions to degrees for better understanding
            deg_solutions = []
            for sol in solutions:
                if sol.is_number:
                    deg = float(sol) * 180 / math.pi
                    deg_solutions.append(deg)
                    steps.append(f"• Solution: {sol} rad = {deg:.2f}°")
                else:
                    steps.append(f"• General solution: {sp.latex(sol)}")
        else:
            for sol in solutions:
                steps.append(f"• Solution: {sp.latex(sol)} rad")
        
        return steps, solutions
        
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

# ========== COMPLEX NUMBERS ==========

def complex_arithmetic(expression):
    """
    Perform arithmetic with complex numbers.
    Example: "(3+2i) + (1-4i)", "(2+3i) * (1-i)"
    """
    steps = ["🔢 **Complex Number Arithmetic**"]
    
    try:
        # Convert i to I for SymPy
        expr_sympy = expression.replace('i', 'I')
        expr = sp.sympify(expr_sympy)
        
        steps.append(f"• Expression: {expression}")
        steps.append(f"• Simplify: ${sp.latex(expr)}$")
        
        # Show real and imaginary parts
        if expr.is_number:
            real = sp.re(expr)
            imag = sp.im(expr)
            steps.append(f"• Real part: {real}")
            steps.append(f"• Imaginary part: {imag}")
            steps.append(f"• Result: {sp.latex(expr)}")
        else:
            steps.append(f"• Result: {sp.latex(expr)}")
            
        return steps, expr
        
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def complex_to_polar(z_str):
    """
    Convert complex number to polar form (r·e^(iθ))
    """
    steps = ["🔢 **Complex to Polar Form**"]
    
    try:
        # Convert i to I
        z_sympy = sp.sympify(z_str.replace('i', 'I'))
        
        # Calculate modulus and argument
        r = sp.Abs(z_sympy)
        theta = sp.arg(z_sympy)
        
        steps.append(f"• Complex number: {z_str}")
        steps.append(f"• Modulus r = |z| = {sp.latex(r)}")
        steps.append(f"• Argument θ = arg(z) = {sp.latex(theta)} rad")
        
        # Convert to degrees for better understanding
        if theta.is_number:
            theta_deg = float(theta) * 180 / math.pi
            steps.append(f"• θ in degrees: {theta_deg:.2f}°")
        
        steps.append(f"• Polar form: {sp.latex(r)}·e^{{i·{sp.latex(theta)}}}")
        steps.append(f"• Euler form: {sp.latex(r)}·(cos({sp.latex(theta)}) + i·sin({sp.latex(theta)}))")
        
        return steps, (r, theta)
        
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

# ========== GEOMETRY ==========

def circle_area(radius):
    """Calculate area of a circle: A = πr²"""
    steps = ["⭕ **Circle Area**"]
    
    try:
        area = math.pi * radius**2
        steps.append(f"• Formula: A = πr²")
        steps.append(f"• r = {radius}")
        steps.append(f"• A = π × {radius}² = π × {radius**2} = {area:.6f}")
        steps.append(f"• A ≈ {area:.4f} (using π ≈ 3.14159)")
        return steps, area
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def circle_circumference(radius):
    """Calculate circumference: C = 2πr"""
    steps = ["⭕ **Circle Circumference**"]
    
    try:
        circ = 2 * math.pi * radius
        steps.append(f"• Formula: C = 2πr")
        steps.append(f"• r = {radius}")
        steps.append(f"• C = 2 × π × {radius} = {circ:.6f}")
        steps.append(f"• C ≈ {circ:.4f}")
        return steps, circ
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def sphere_volume(radius):
    """Calculate volume of a sphere: V = (4/3)πr³"""
    steps = ["🌐 **Sphere Volume**"]
    
    try:
        volume = (4/3) * math.pi * radius**3
        steps.append(f"• Formula: V = (4/3)πr³")
        steps.append(f"• r = {radius}")
        steps.append(f"• V = (4/3) × π × {radius}³ = {volume:.6f}")
        steps.append(f"• V ≈ {volume:.4f}")
        return steps, volume
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def cylinder_volume(radius, height):
    """Calculate volume of a cylinder: V = πr²h"""
    steps = ["🥫 **Cylinder Volume**"]
    
    try:
        volume = math.pi * radius**2 * height
        steps.append(f"• Formula: V = πr²h")
        steps.append(f"• r = {radius}, h = {height}")
        steps.append(f"• V = π × {radius}² × {height} = {volume:.6f}")
        steps.append(f"• V ≈ {volume:.4f}")
        return steps, volume
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def rectangle_area(length, width):
    """Calculate area of a rectangle: A = l × w"""
    steps = ["📏 **Rectangle Area**"]
    
    try:
        area = length * width
        steps.append(f"• Formula: A = l × w")
        steps.append(f"• l = {length}, w = {width}")
        steps.append(f"• A = {length} × {width} = {area}")
        return steps, area
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def triangle_area(base, height):
    """Calculate area of a triangle: A = (1/2) × b × h"""
    steps = ["📐 **Triangle Area**"]
    
    try:
        area = 0.5 * base * height
        steps.append(f"• Formula: A = ½ × b × h")
        steps.append(f"• b = {base}, h = {height}")
        steps.append(f"• A = ½ × {base} × {height} = {area}")
        return steps, area
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

def pythagorean_theorem(a=None, b=None, c=None):
    """
    Solve for missing side in right triangle: a² + b² = c²
    Provide exactly two sides.
    """
    steps = ["📐 **Pythagorean Theorem**"]
    
    try:
        if a is not None and b is not None and c is None:
            # Find hypotenuse
            c = math.sqrt(a**2 + b**2)
            steps.append(f"• Finding hypotenuse c:")
            steps.append(f"• a² + b² = c²")
            steps.append(f"• {a}² + {b}² = c²")
            steps.append(f"• {a**2} + {b**2} = c²")
            steps.append(f"• c² = {a**2 + b**2}")
            steps.append(f"• c = √({a**2 + b**2}) = {c:.6f}")
            return steps, c
            
        elif a is not None and c is not None and b is None:
            # Find leg b
            b = math.sqrt(c**2 - a**2)
            steps.append(f"• Finding leg b:")
            steps.append(f"• a² + b² = c²")
            steps.append(f"• {a}² + b² = {c}²")
            steps.append(f"• {a**2} + b² = {c**2}")
            steps.append(f"• b² = {c**2} - {a**2} = {c**2 - a**2}")
            steps.append(f"• b = √({c**2 - a**2}) = {b:.6f}")
            return steps, b
            
        elif b is not None and c is not None and a is None:
            # Find leg a
            a = math.sqrt(c**2 - b**2)
            steps.append(f"• Finding leg a:")
            steps.append(f"• a² + b² = c²")
            steps.append(f"• a² + {b}² = {c}²")
            steps.append(f"• a² + {b**2} = {c**2}")
            steps.append(f"• a² = {c**2} - {b**2} = {c**2 - b**2}")
            steps.append(f"• a = √({c**2 - b**2}) = {a:.6f}")
            return steps, a
            
        else:
            steps.append("❌ Provide exactly two sides")
            return steps, None
            
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

# ========== VECTOR CALCULUS ==========

def curl(vector_field, variables=None):
    """
    Calculate curl of a vector field in 3D.
    Input format: "[x*y, y*z, z*x]" or "x*y, y*z, z*x"
    Returns: (steps, [curl_x, curl_y, curl_z])
    """
    steps = ["📐 **Curl Calculator**"]
    steps.append(f"• Input: {vector_field}")
    
    try:
        if variables is None:
            variables = ['x', 'y', 'z']
        
        if len(variables) != 3:
            steps.append("❌ Curl is only defined for 3D vector fields")
            return steps, None
        
        # Clean up the input
        vector_field = vector_field.strip()
        
        # Remove brackets if present
        if vector_field.startswith('[') and vector_field.endswith(']'):
            vector_field = vector_field[1:-1]
        
        # Split by commas
        components = [comp.strip() for comp in vector_field.split(',')]
        
        if len(components) != 3:
            steps.append(f"❌ Expected 3 components, got {len(components)}")
            return steps, None
        
        # Create symbols
        x, y, z = sp.symbols('x y z')
        
        # Parse each component
        comps = []
        for i, comp in enumerate(components):
            try:
                expr = sp.sympify(comp)
                comps.append(expr)
                steps.append(f"• F{i+1} = {comp} = ${sp.latex(expr)}$")
            except Exception as e:
                steps.append(f"❌ Invalid component '{comp}': {e}")
                return steps, None
        
        Fx, Fy, Fz = comps
        
        # Calculate curl components
        steps.append(f"\n**Calculating curl components:**")
        steps.append(f"  curl_x = ∂Fz/∂y - ∂Fy/∂z")
        curl_x = sp.diff(Fz, y) - sp.diff(Fy, z)
        steps.append(f"  = ∂({sp.latex(Fz)})/∂y - ∂({sp.latex(Fy)})/∂z")
        steps.append(f"  = {sp.latex(curl_x)}")
        
        steps.append(f"\n  curl_y = ∂Fx/∂z - ∂Fz/∂x")
        curl_y = sp.diff(Fx, z) - sp.diff(Fz, x)
        steps.append(f"  = ∂({sp.latex(Fx)})/∂z - ∂({sp.latex(Fz)})/∂x")
        steps.append(f"  = {sp.latex(curl_y)}")
        
        steps.append(f"\n  curl_z = ∂Fy/∂x - ∂Fx/∂y")
        curl_z = sp.diff(Fy, x) - sp.diff(Fx, y)
        steps.append(f"  = ∂({sp.latex(Fy)})/∂x - ∂({sp.latex(Fx)})/∂y")
        steps.append(f"  = {sp.latex(curl_z)}")
        
        curl_vec = [curl_x, curl_y, curl_z]
        
        steps.append(f"\n✅ **Result:** ∇×F = {sp.latex(curl_vec)}")
        
        return steps, curl_vec
        
    except Exception as e:
        steps.append(f"❌ Error calculating curl: {str(e)}")
        return steps, None

def gradient(scalar_field, variables=None):
    """
    Calculate gradient of a scalar field.
    Input format: "x^2*y + y*z"
    """
    steps = ["📐 **Gradient Calculator**"]
    steps.append(f"• Input: {scalar_field}")
    
    try:
        if variables is None:
            variables = ['x', 'y', 'z']
        
        # Create symbols
        vars_sym = [sp.Symbol(v) for v in variables]
        
        # Parse the scalar field
        try:
            expr = sp.sympify(scalar_field)
            steps.append(f"• f = ${sp.latex(expr)}$")
        except Exception as e:
            steps.append(f"❌ Invalid expression: {e}")
            return steps, None
        
        # Calculate partial derivatives
        gradient_vec = []
        steps.append(f"\n**Calculating partial derivatives:**")
        
        for i, var in enumerate(vars_sym):
            deriv = sp.diff(expr, var)
            gradient_vec.append(deriv)
            steps.append(f"  ∂f/∂{variables[i]} = {sp.latex(deriv)}")
        
        steps.append(f"\n✅ **Result:** ∇f = {sp.latex(gradient_vec)}")
        
        return steps, gradient_vec
        
    except Exception as e:
        steps.append(f"❌ Error calculating gradient: {str(e)}")
        return steps, None

def divergence(vector_field, variables=None):
    """
    Calculate divergence of a vector field.
    Input format: "[x*y, y*z, z*x]" or "x*y, y*z, z*x"
    """
    steps = ["📐 **Divergence Calculator**"]
    steps.append(f"• Input: {vector_field}")
    
    try:
        if variables is None:
            variables = ['x', 'y', 'z']
        
        # Clean up the input
        vector_field = vector_field.strip()
        
        # Remove brackets if present
        if vector_field.startswith('[') and vector_field.endswith(']'):
            vector_field = vector_field[1:-1]
        
        # Split by commas
        components = [comp.strip() for comp in vector_field.split(',')]
        
        if len(components) != len(variables):
            steps.append(f"❌ Expected {len(variables)} components, got {len(components)}")
            return steps, None
        
        # Create symbols
        vars_sym = [sp.Symbol(v) for v in variables]
        
        # Parse each component
        comps = []
        for i, comp in enumerate(components):
            try:
                expr = sp.sympify(comp)
                comps.append(expr)
                steps.append(f"• F{i+1} = {comp} = ${sp.latex(expr)}$")
            except Exception as e:
                steps.append(f"❌ Invalid component '{comp}': {e}")
                return steps, None
        
        # Calculate divergence: ∂F₁/∂x + ∂F₂/∂y + ∂F₃/∂z
        steps.append(f"\n**Calculating divergence:**")
        steps.append(f"  div F = ∂F₁/∂x + ∂F₂/∂y + ∂F₃/∂z")
        
        div = 0
        for i, (comp, var) in enumerate(zip(comps, vars_sym)):
            deriv = sp.diff(comp, var)
            div += deriv
            steps.append(f"  ∂F{i+1}/∂{variables[i]} = {sp.latex(deriv)}")
        
        steps.append(f"\n✅ **Result:** ∇·F = {sp.latex(div)}")
        
        return steps, div
        
    except Exception as e:
        steps.append(f"❌ Error calculating divergence: {str(e)}")
        return steps, None

# ========== CURVE FITTING (Premium) ==========

def curve_fit_function(func_template, x_data_str, y_data_str):
    """
    Fit a custom function to data points.
    Example: "a*exp(b*x)+c" with x=1,2,3 and y=2,4,8
    """
    steps = ["📈 **Curve Fitting (Premium Feature)**"]
    steps.append(f"• Function template: {func_template}")
    steps.append(f"• X data: {x_data_str}")
    steps.append(f"• Y data: {y_data_str}")
    
    try:
        # Parse data strings
        x_data = [float(x.strip()) for x in x_data_str.split(',')]
        y_data = [float(y.strip()) for y in y_data_str.split(',')]
        
        # Convert to numpy arrays
        x = np.array(x_data, dtype=float)
        y = np.array(y_data, dtype=float)
        
        steps.append(f"• Number of points: {len(x)}")
        
        if len(x) != len(y):
            steps.append("❌ X and Y data must have the same length")
            return steps, None
        
        # Parse the function template to identify parameters
        # Find all parameter names (single letters commonly used)
        param_matches = re.findall(r'[a-zA-Z]', func_template)
        # Get unique parameters, excluding x and common constants
        exclude = {'x', 'e', 'π', 'pi'}
        params = sorted(list(set([p for p in param_matches if p not in exclude])))
        
        if not params:
            # Default parameters if none found
            params = ['a', 'b', 'c']
        
        steps.append(f"• Parameters to fit: {', '.join(params)}")
        
        # Create the fitting function
        def create_fit_func(params):
            def fit_func(x, *p):
                # Create local namespace with parameters
                namespace = {'x': x, 'math': math, 'np': np}
                for param_name, param_value in zip(params, p):
                    namespace[param_name] = param_value
                
                # Safe evaluation of the expression
                try:
                    # Replace ^ with ** for Python syntax
                    expr = func_template.replace('^', '**')
                    return eval(expr, {"__builtins__": {}}, namespace)
                except:
                    return np.nan
            return fit_func
        
        fit_func = create_fit_func(params)
        
        # Initial guess: all parameters start at 1.0
        initial_guess = [1.0] * len(params)
        
        steps.append(f"• Initial guess: {dict(zip(params, initial_guess))}")
        
        # Perform curve fitting
        try:
            popt, pcov = optimize.curve_fit(fit_func, x, y, p0=initial_guess, maxfev=5000)
            
            # Calculate fitted values
            y_fit = fit_func(x, *popt)
            
            # Calculate R-squared
            residuals = y - y_fit
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0
            
            # Calculate standard errors
            perr = np.sqrt(np.diag(pcov)) if len(params) > 1 else [np.sqrt(pcov[0][0])]
            
            steps.append(f"• **Fitted Parameters:**")
            for param_name, value, error in zip(params, popt, perr):
                steps.append(f"  {param_name} = {value:.6f} ± {error:.6f}")
            
            steps.append(f"• **Goodness of fit:**")
            steps.append(f"  R² = {r_squared:.6f}")
            steps.append(f"  RMSE = {np.sqrt(ss_res/len(x)):.6f}")
            
            # Generate the fitted function string
            fitted_func = func_template
            for param_name, value in zip(params, popt):
                fitted_func = fitted_func.replace(param_name, f"{value:.4f}")
            
            steps.append(f"• **Fitted function:** {fitted_func}")
            
            # Create a plot
            plt.figure(figsize=(10, 6))
            plt.scatter(x, y, color='red', label='Data points', s=50, zorder=5)
            
            # Generate smooth curve for plotting
            x_smooth = np.linspace(min(x), max(x), 100)
            y_smooth = fit_func(x_smooth, *popt)
            plt.plot(x_smooth, y_smooth, 'b-', label=f'Fitted: {fitted_func}', linewidth=2)
            
            plt.xlabel('x')
            plt.ylabel('y')
            plt.title('Curve Fitting Result')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Save plot to bytes buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            # Return steps, results, and plot buffer
            results = {
                'parameters': dict(zip(params, popt)),
                'errors': dict(zip(params, perr)),
                'r_squared': r_squared,
                'fitted_function': fitted_func,
                'plot': buf
            }
            
            return steps, results
            
        except Exception as fit_error:
            steps.append(f"❌ Curve fitting failed: {str(fit_error)}")
            steps.append("  Try a different function template or check your data.")
            return steps, None
        
    except Exception as e:
        steps.append(f"❌ Error: {str(e)}")
        return steps, None

# ========== PDF EXPORT (Premium) ==========

def export_to_pdf(user_id, history_data, calculations):
    """
    Generate a PDF report of user's calculations.
    Returns path to the generated PDF file.
    """
    steps = ["📄 **PDF Export (Premium Feature)**"]
    
    try:
        # Create a temporary file for the PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"calc_history_{user_id}_{timestamp}.pdf"
        pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
        
        # Create the PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#0066cc')
        )
        title = Paragraph("SmartCalcAI Bot - Calculation History", title_style)
        story.append(title)
        
        # Date and user info
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=1
        )
        date_info = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
        story.append(date_info)
        story.append(Spacer(1, 0.2*inch))
        
        # User ID
        user_info = Paragraph(f"User ID: {user_id}", date_style)
        story.append(user_info)
        story.append(Spacer(1, 0.3*inch))
        
        if not history_data:
            story.append(Paragraph("No calculation history found.", styles['Normal']))
        else:
            # Summary statistics
            story.append(Paragraph("📊 **Summary Statistics**", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            total_calcs = len(history_data)
            unique_commands = len(set([h[0] for h in history_data]))
            
            stats_data = [
                ["Total Calculations:", str(total_calcs)],
                ["Unique Commands Used:", str(unique_commands)],
                ["Date Range:", f"{history_data[-1][3][:10]} to {history_data[0][3][:10]}"],
            ]
            
            stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0066cc')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Recent calculations
            story.append(Paragraph("📝 **Recent Calculations**", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            # Create table for calculations
            table_data = [['Command', 'Input', 'Output', 'Date']]
            for cmd, inp, out, ts in history_data[:20]:  # Show last 20
                date = ts[:16] if ts else "N/A"
                # Truncate long strings
                inp_short = inp[:30] + "..." if len(inp) > 30 else inp
                out_short = out[:30] + "..." if len(out) > 30 else out
                table_data.append([cmd, inp_short, out_short, date])
            
            calc_table = Table(table_data, colWidths=[1*inch, 1.8*inch, 1.8*inch, 1.4*inch])
            calc_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ]))
            story.append(calc_table)
            
            # Add any additional calculations passed in
            if calculations:
                story.append(Spacer(1, 0.3*inch))
                story.append(Paragraph("🔢 **Current Calculations**", styles['Heading2']))
                story.append(Spacer(1, 0.1*inch))
                
                calc_text = "<br/>".join([f"• {calc}" for calc in calculations])
                story.append(Paragraph(calc_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        steps.append(f"✅ PDF generated successfully: {pdf_filename}")
        return steps, pdf_path
        
    except Exception as e:
        steps.append(f"❌ Error generating PDF: {str(e)}")
        return steps, None

# ========== TEST GENERATOR (Premium) ==========

def generate_test(topic, difficulty="medium"):
    """
    Generate a random practice problem with solution.
    Topics: algebra, quadratic, trig, geometry, probability
    """
    import random
    
    steps = [f"📝 **{topic.capitalize()} Practice Problem**"]
    
    if topic == "quadratic":
        # Generate random quadratic with integer roots
        root1 = random.randint(-5, 5)
        root2 = random.randint(-5, 5)
        a = random.randint(1, 3)
        
        # Build equation: a(x - r1)(x - r2) = 0
        b = -a * (root1 + root2)
        c = a * root1 * root2
        
        equation = f"{a}x² + {b}x + {c} = 0" if b >= 0 else f"{a}x² - {abs(b)}x + {c} = 0"
        
        steps.append(f"**Question:** Solve: {equation}")
        steps.append("")
        steps.append("**Solution:**")
        steps.append(f"1. Identify coefficients: a={a}, b={b}, c={c}")
        steps.append(f"2. Factor: {a}(x {'+' if root1>0 else '-'} {abs(root1)})(x {'+' if root2>0 else '-'} {abs(root2)}) = 0")
        steps.append(f"3. Solutions: x = {root1}, x = {root2}")
        
        return steps, {"equation": equation, "solutions": [root1, root2]}
        
    elif topic == "trig":
        # Generate trig equation
        angle = random.choice([30, 45, 60, 90])
        func = random.choice(["sin", "cos", "tan"])
        
        if func == "sin":
            value = math.sin(math.radians(angle))
        elif func == "cos":
            value = math.cos(math.radians(angle))
        else:
            value = math.tan(math.radians(angle))
            
        equation = f"{func}(x) = {value:.3f}"
        
        steps.append(f"**Question:** Solve {equation} for 0° ≤ x ≤ 360°")
        steps.append("")
        steps.append("**Solution:**")
        steps.append(f"1. {func}(x) = {value:.3f}")
        steps.append(f"2. Reference angle: {angle}°")
        
        if func == "sin":
            steps.append(f"3. Sine is positive in QI and QII")
            steps.append(f"4. Solutions: x = {angle}°, x = {180-angle}°")
        elif func == "cos":
            steps.append(f"3. Cosine is positive in QI and QIV")
            steps.append(f"4. Solutions: x = {angle}°, x = {360-angle}°")
        else:
            steps.append(f"3. Tangent is positive in QI and QIII")
            steps.append(f"4. Solutions: x = {angle}°, x = {180+angle}°")
            
        return steps, {"equation": equation, "solutions": [angle, 180-angle] if func=="sin" else [angle, 360-angle] if func=="cos" else [angle, 180+angle]}
        
    elif topic == "probability":
        # Generate probability problem
        total = random.randint(20, 50)
        favorable = random.randint(5, total-5)
        
        steps.append(f"**Question:** If you randomly select one item from {total} items, "
                    f"and {favorable} of them are favorable, what is the probability?")
        steps.append("")
        steps.append("**Solution:**")
        steps.append(f"• Probability = favorable / total")
        steps.append(f"• = {favorable} / {total}")
        steps.append(f"• = {favorable/total:.4f}")
        steps.append(f"• = {favorable/total*100:.1f}%")
        
        return steps, {"favorable": favorable, "total": total, "probability": favorable/total}
        
    elif topic == "algebra":
        # Generate linear equation
        a = random.randint(1, 5)
        b = random.randint(-10, 10)
        solution = random.randint(-5, 5)
        
        # Build equation: a*x + b = solution
        equation = f"{a}x + {b} = {a*solution + b}"
        
        steps.append(f"**Question:** Solve for x: {equation}")
        steps.append("")
        steps.append("**Solution:**")
        steps.append(f"1. {equation}")
        steps.append(f"2. Subtract {b} from both sides: {a}x = {a*solution}")
        steps.append(f"3. Divide by {a}: x = {solution}")
        
        return steps, {"equation": equation, "solution": solution}
        
    elif topic == "geometry":
        # Generate geometry problem
        shape = random.choice(["circle", "square", "rectangle"])
        
        if shape == "circle":
            radius = random.randint(2, 8)
            steps.append(f"**Question:** Find the area of a circle with radius {radius}.")
            steps.append("")
            steps.append("**Solution:**")
            steps.append(f"• Formula: A = πr²")
            steps.append(f"• A = π × {radius}²")
            steps.append(f"• A = π × {radius**2}")
            steps.append(f"• A ≈ {math.pi * radius**2:.2f} square units")
            return steps, {"shape": "circle", "radius": radius, "area": math.pi * radius**2}
        
        elif shape == "square":
            side = random.randint(3, 10)
            steps.append(f"**Question:** Find the area and perimeter of a square with side {side}.")
            steps.append("")
            steps.append("**Solution:**")
            steps.append(f"• Area = side² = {side}² = {side**2}")
            steps.append(f"• Perimeter = 4 × side = 4 × {side} = {4*side}")
            return steps, {"shape": "square", "side": side, "area": side**2, "perimeter": 4*side}
        
        else:  # rectangle
            length = random.randint(4, 12)
            width = random.randint(2, 8)
            steps.append(f"**Question:** Find the area of a rectangle with length {length} and width {width}.")
            steps.append("")
            steps.append("**Solution:**")
            steps.append(f"• Formula: A = l × w")
            steps.append(f"• A = {length} × {width}")
            steps.append(f"• A = {length * width}")
            return steps, {"shape": "rectangle", "length": length, "width": width, "area": length * width}
        
    else:
        steps.append("Topic not available yet")
        return steps, None
