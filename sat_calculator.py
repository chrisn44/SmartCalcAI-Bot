"""
SAT Calculator Module - Advanced math functions for SAT/ACT preparation
All functions return (steps, result) where steps is a list of explanation strings.
Built with SymPy and math - no external APIs needed.
"""

import sympy as sp
import math
import re

# ========== ADVANCED ALGEBRA ==========

def solve_quadratic(eq_str, var='x'):
    """
    Solve quadratic equation: ax² + bx + c = 0 with detailed steps.
    Examples: "2x^2 + 3x - 5 = 0", "x^2 - 4 = 0", "x^2 + 2x + 5 = 0"
    """
    var_sym = sp.Symbol(var)
    steps = [f"📐 **Quadratic Equation:** {eq_str}"]
    
    try:
        # Parse equation
        if '=' in eq_str:
            left, right = eq_str.split('=')
            expr = sp.sympify(f"({left}) - ({right})")
        else:
            expr = sp.sympify(eq_str)
        
        expr = sp.expand(expr)
        coeffs = sp.Poly(expr, var_sym).all_coeffs()
        
        if len(coeffs) != 3:
            steps.append("❌ This is not a quadratic equation (need ax²+bx+c=0 form)")
            return steps, None
        
        a, b, c = [float(coeff) for coeff in coeffs]
        
        steps.append(f"• Standard form: {a}x² + {b}x + {c} = 0")
        steps.append(f"• a = {a}, b = {b}, c = {c}")
        
        # Calculate discriminant
        discriminant = b**2 - 4*a*c
        steps.append(f"• Discriminant Δ = b² - 4ac = {b}² - 4·{a}·{c} = {discriminant:.4f}")
        
        if abs(discriminant) < 1e-10:  # practically zero
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
    Example: "(x+1)/(x-2) = 3", "2/(x+1) = 4/(x-3)"
    """
    var_sym = sp.Symbol(var)
    steps = [f"📐 **Rational Equation:** {eq_str}"]
    
    try:
        # Parse equation
        if '=' in eq_str:
            left, right = eq_str.split('=')
            expr = sp.sympify(f"({left}) - ({right})")
        else:
            expr = sp.sympify(eq_str)
        
        # Combine into single fraction
        expr_combined = sp.together(expr)
        numer, denom = sp.fraction(expr_combined)
        
        steps.append(f"• Combine terms: ${sp.latex(expr_combined)} = 0$")
        steps.append(f"• Set numerator = 0: ${sp.latex(numer)} = 0$")
        
        # Solve numerator
        solutions = sp.solve(numer, var_sym)
        
        # Check for extraneous roots (denominator = 0)
        valid_solutions = []
        for sol in solutions:
            if denom.subs(var_sym, sol) != 0:
                valid_solutions.append(sol)
            else:
                steps.append(f"• ❌ Extraneous root: {sol} makes denominator zero")
        
        if valid_solutions:
            steps.append(f"• ✅ Valid solutions: {valid_solutions}")
        else:
            steps.append(f"• ❌ No valid solutions")
            
        return steps, valid_solutions
        
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
        # Parse format like "3:4 = 12:x" or "5:2 = x:8"
        match = re.match(r'(\d+):(\d+)\s*=\s*(\d+|x):([a-z]|\d+)', prop_str.replace(' ', ''))
        if not match:
            # Try alternative format "3/4 = 12/x"
            match = re.match(r'(\d+)/(\d+)\s*=\s*(\d+)/([a-z])', prop_str.replace(' ', ''))
            
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
        
    else:
        steps.append("Topic not available yet")
        return steps, None