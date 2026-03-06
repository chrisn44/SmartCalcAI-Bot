"""
Solve parsed equations and generate step‑by‑step explanations
"""
import sympy as sp
import logging

logger = logging.getLogger(__name__)

class EquationSolver:
    def __init__(self):
        self.x = sp.Symbol('x')
        self.y = sp.Symbol('y')
        self.z = sp.Symbol('z')
    
    def solve_equation(self, left_expr, right_expr=None):
        """
        Solve equation and generate steps
        """
        steps = ["🧮 **Solving equation from photo**"]
        
        try:
            # Create equation object
            if right_expr is not None:
                equation = sp.Eq(left_expr, right_expr)
                steps.append(f"• Equation: ${sp.latex(equation)}$")
            else:
                equation = left_expr
                steps.append(f"• Expression: ${sp.latex(equation)}$")
            
            # Detect variables
            variables = list(equation.free_symbols)
            if not variables:
                # Constant expression – evaluate
                result = float(equation)
                steps.append(f"• Evaluating constant expression")
                steps.append(f"• Result: {result}")
                return steps, result
            
            # Try to solve
            if isinstance(equation, sp.Eq):
                solutions = sp.solve(equation, variables[0])
                steps.append(f"• Solving for {variables[0]}")
                
                if solutions:
                    steps.append(f"• Found {len(solutions)} solution(s):")
                    for i, sol in enumerate(solutions):
                        steps.append(f"  {i+1}. ${sp.latex(sol)}$")
                    return steps, solutions
                else:
                    # Try numerical solving
                    try:
                        from scipy.optimize import fsolve
                        import numpy as np
                        
                        # Convert to numeric function
                        f = sp.lambdify(variables[0], equation.lhs - equation.rhs, 'numpy')
                        guess = 0.0
                        root = fsolve(f, guess)[0]
                        steps.append(f"• Numerical solution: x ≈ {root:.6f}")
                        return steps, root
                    except:
                        steps.append("• Could not find analytical solution")
                        return steps, None
            else:
                # Just an expression – simplify
                simplified = sp.simplify(equation)
                steps.append(f"• Simplified: ${sp.latex(simplified)}$")
                return steps, simplified
                
        except Exception as e:
            logger.error(f"Solver error: {e}")
            steps.append(f"❌ Error solving: {str(e)}")
            return steps, None
