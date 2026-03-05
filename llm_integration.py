import re
import math
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
    """
    Built‑in natural language interpreter for mathematics and physics.
    No external APIs – works offline and is completely free.
    Premium features are marked with premium=True.
    """

    def __init__(self):
        logger.info("Initializing Premium Smart Interpreter")
        self._init_patterns()

    def _init_patterns(self):
        # Each pattern is a tuple: (regex, command, premium_flag, handler_function)
        self.patterns = []

        # ========== DERIVATIVES ==========
        self.patterns.extend([
            (re.compile(r"(?:what(?:\s+is)?\s+)?(?:the\s+)?derivative\s+of\s+(.+?)(?:\s+(?:with\s+respect\s+to|w\.?r\.?t\.?)\s+([a-z]))?$", re.IGNORECASE),
             "derive", False, self._handle_derive),
            (re.compile(r"differentiate\s+(.+?)(?:\s+(?:with\s+respect\s+to|w\.?r\.?t\.?)\s+([a-z]))?$", re.IGNORECASE),
             "derive", False, self._handle_derive),
            (re.compile(r"d/d([a-z])\s*\(\s*(.+?)\s*\)", re.IGNORECASE),
             "derive", False, self._handle_derive_dx),
            (re.compile(r"f'(?:\(([a-z])\))?\s*=\s*(.+?)$", re.IGNORECASE),
             "derive", False, self._handle_derive_fprime),
        ])

        # ========== INTEGRALS ==========
        self.patterns.extend([
            (re.compile(r"(?:integrate|integral\s+of)\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)(?:\s+(?:with\s+respect\s+to|w\.?r\.?t\.?)\s+([a-z]))?$", re.IGNORECASE),
             "integrate", False, self._handle_integral_definite),
            (re.compile(r"(?:integrate|integral\s+of|find\s+antiderivative\s+of)\s+(.+?)(?:\s+(?:with\s+respect\s+to|w\.?r\.?t\.?)\s+([a-z]))?$", re.IGNORECASE),
             "integrate", False, self._handle_integral_indefinite),
            (re.compile(r"∫\s*(.+?)\s*d([a-z])", re.IGNORECASE),
             "integrate", False, self._handle_integral_unicode),
        ])

        # ========== LIMITS ==========
        self.patterns.extend([
            (re.compile(r"limit\s+of\s+(.+?)\s+as\s+([a-z])\s*(?:->|→|approaches|to)\s*([0-9.infinity-]+)", re.IGNORECASE),
             "limit", False, self._handle_limit),
            (re.compile(r"lim\s*_{?([a-z])\s*(?:->|→)?\s*([0-9.infinity-]+)}?\s+(.+?)$", re.IGNORECASE),
             "limit", False, self._handle_limit_alt),
        ])

        # ========== SERIES ==========
        self.patterns.extend([
            (re.compile(r"(?:taylor\s+series|series|expansion|expand)\s+of\s+(.+?)\s+(?:about|around|at)\s+([0-9.-]+)(?:\s+(?:order|terms|to\s+order)\s+([0-9]+))?", re.IGNORECASE),
             "series", False, self._handle_series),
        ])

        # ========== EQUATION SOLVING ==========
        self.patterns.extend([
            (re.compile(r"solve\s+(?:the\s+)?(?:equation\s+)?(.+?)(?:\s+for\s+([a-z]))?$", re.IGNORECASE),
             "solve", False, self._handle_solve),
            (re.compile(r"find\s+(?:the\s+)?roots?\s+of\s+(.+?)$", re.IGNORECASE),
             "solve", False, self._handle_solve_roots),
        ])

        # ========== PLOTTING ==========
        self.patterns.extend([
            (re.compile(r"(?:plot|graph|draw)\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)(?:\s+for\s+([a-z]))?", re.IGNORECASE),
             "plot", False, self._handle_plot),
        ])

        # ========== 3D PLOTTING (PREMIUM) ==========
        self.patterns.extend([
            (re.compile(r"(?:plot3d|3d\s+plot|surface\s+plot)\s+of\s+(.+?)\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)\s+for\s+([a-z])\s+from\s+([0-9.-]+)\s+to\s+([0-9.-]+)", re.IGNORECASE),
             "plot3d", True, self._handle_plot3d),
        ])

        # ========== MATRIX OPERATIONS ==========
        self.patterns.extend([
            (re.compile(r"(?:matrix\s+)?multiply\s+(\[\[.*?\]\])\s+(?:and|by|×|x|\*)\s+(\[\[.*?\]\])", re.IGNORECASE | re.DOTALL),
             "matrix", False, self._handle_matrix_mult),
            (re.compile(r"inverse\s+of\s+(\[\[.*?\]\])", re.IGNORECASE | re.DOTALL),
             "inverse", False, self._handle_matrix_inverse),
            (re.compile(r"determinant\s+of\s+(\[\[.*?\]\])", re.IGNORECASE | re.DOTALL),
             "det", False, self._handle_matrix_det),
        ])

        # ========== UNIT CONVERSION ==========
        self.patterns.extend([
            (re.compile(r"(?:convert|change)\s+([0-9.]+)\s*([a-z/°]+)\s+(?:to|into|in)\s+([a-z/°]+)", re.IGNORECASE),
             "unit", False, self._handle_unit),
            (re.compile(r"([0-9.]+)\s*([a-z/°]+)\s+to\s+([a-z/°]+)", re.IGNORECASE),
             "unit", False, self._handle_unit_simple),
        ])

        # ========== STATISTICS ==========
        self.patterns.extend([
            (re.compile(r"(?:mean|average)\s+of\s+([0-9,\s\.]+)", re.IGNORECASE),
             "stat", False, self._handle_stat_mean),
            (re.compile(r"median\s+of\s+([0-9,\s\.]+)", re.IGNORECASE),
             "stat", False, self._handle_stat_median),
            (re.compile(r"standard\s+deviation\s+of\s+([0-9,\s\.]+)", re.IGNORECASE),
             "stat", False, self._handle_stat_std),
        ])

        # ========== ORDINARY DIFFERENTIAL EQUATIONS ==========
        self.patterns.extend([
            (re.compile(r"solve\s+(?:the\s+)?(?:ode|differential\s+equation|diff\s+eq)\s+(.+?)$", re.IGNORECASE),
             "ode", False, self._handle_ode),
            (re.compile(r"^(y''?[\s+].+?=0)$", re.IGNORECASE),
             "ode", False, self._handle_ode_raw),
        ])

        # ========== BASIC ARITHMETIC ==========
        self.patterns.extend([
            (re.compile(r"what(?:\s+is)?\s+([0-9\s\+\-\*\/\^\(\)\.]+)", re.IGNORECASE),
             "calc", False, self._handle_calc),
            (re.compile(r"(?:calculate|compute|evaluate|solve)\s+([0-9\s\+\-\*\/\^\(\)\.]+)", re.IGNORECASE),
             "calc", False, self._handle_calc),
            (re.compile(r"^([0-9]+)\s*([\+\-\*\/\^])\s*([0-9]+)$"),
             "calc", False, self._handle_calc_binary),
        ])

        # ========== PHYSICS ==========
        # All physics features are premium
        self.patterns.extend([
            # Force: F = m*a
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?force\s+(?:of|for)?\s+mass\s+([0-9.]+)\s*(?:kg)?\s+(?:and|with)?\s+acceleration\s+([0-9.]+)\s*(?:m/s²|m/s2|m/s\^2)?", re.IGNORECASE),
             "physics_force", True, self._handle_physics_force),

            # Weight: W = m*g (optional gravity)
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?weight\s+(?:of)?\s+mass\s+([0-9.]+)\s*(?:kg)?(?:\s+on\s+([a-z]+))?", re.IGNORECASE),
             "physics_weight", True, self._handle_physics_weight),

            # Kinetic energy: KE = 0.5*m*v^2
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?kinetic\s+energy\s+(?:of)?\s+mass\s+([0-9.]+)\s*(?:kg)?\s+(?:and|with)?\s+velocity\s+([0-9.]+)\s*(?:m/s)?", re.IGNORECASE),
             "physics_ke", True, self._handle_physics_ke),

            # Potential energy: PE = m*g*h
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?potential\s+energy\s+(?:of)?\s+mass\s+([0-9.]+)\s*(?:kg)?\s+(?:at|with)?\s+height\s+([0-9.]+)\s*(?:m)?(?:\s+gravity\s+([0-9.]+))?", re.IGNORECASE),
             "physics_pe", True, self._handle_physics_pe),

            # Ohm's law: V = I*R
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?(voltage|current|resistance)\s+(?:in|for)?\s+(?:circuit\s+)?(?:with)?\s*(?:voltage\s+([0-9.]+)\s*V)?\s*(?:current\s+([0-9.]+)\s*A)?\s*(?:resistance\s+([0-9.]+)\s*Ω)?", re.IGNORECASE),
             "physics_ohms", True, self._handle_physics_ohms),

            # Electrical power: P = V*I = I^2*R = V^2/R
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?power\s+(?:in)?\s*(?:circuit)?\s*(?:with)?\s*(?:voltage\s+([0-9.]+)\s*V)?\s*(?:current\s+([0-9.]+)\s*A)?\s*(?:resistance\s+([0-9.]+)\s*Ω)?", re.IGNORECASE),
             "physics_power", True, self._handle_physics_power),

            # Ideal gas law: PV = nRT
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?(pressure|volume|temperature|moles)\s+(?:of)?\s*(?:gas)?\s*(?:with)?\s*(?:pressure\s+([0-9.]+)\s*Pa)?\s*(?:volume\s+([0-9.]+)\s*m3)?\s*(?:moles\s+([0-9.]+)\s*mol)?\s*(?:temperature\s+([0-9.]+)\s*K)?", re.IGNORECASE),
             "physics_gas", True, self._handle_physics_gas),

            # Wave speed: v = f*λ
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?wave\s+speed\s+(?:of)?\s+frequency\s+([0-9.]+)\s*(?:Hz)?\s+(?:and)?\s+wavelength\s+([0-9.]+)\s*(?:m)?", re.IGNORECASE),
             "physics_wave_speed", True, self._handle_physics_wave_speed),

            # Frequency from period: f = 1/T
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?frequency\s+(?:of)?\s+period\s+([0-9.]+)\s*(?:s)?", re.IGNORECASE),
             "physics_freq", True, self._handle_physics_freq),

            # Lens formula: 1/f = 1/u + 1/v
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?focal\s+length\s+(?:of)?\s+lens\s+with\s+object\s+distance\s+([0-9.]+)\s*(?:m)?\s+(?:and|,)?\s+image\s+distance\s+([0-9.]+)\s*(?:m)?", re.IGNORECASE),
             "physics_lens", True, self._handle_physics_lens),

            # Snell's law: n1 sinθ1 = n2 sinθ2
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?angle\s+of\s+refraction\s+given\s+incident\s+angle\s+([0-9.]+)\s*°?\s+(?:and)?\s+refractive\s+indices?\s+([0-9.]+)\s+(?:and|,)?\s+([0-9.]+)", re.IGNORECASE),
             "physics_snell", True, self._handle_physics_snell),

            # Radioactive decay: N = N0 e^(-λt)
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?remaining\s+amount\s+after\s+time\s+([0-9.]+)\s*(?:s)?\s+with\s+decay\s+constant\s+([0-9.]+)\s*(?:/s)?\s+initial\s+amount\s+([0-9.]+)", re.IGNORECASE),
             "physics_decay", True, self._handle_physics_decay),

            # Half‑life from decay constant: t½ = ln2/λ
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?half[- ]?life\s+for\s+decay\s+constant\s+([0-9.]+)\s*(?:/s)?", re.IGNORECASE),
             "physics_half_life", True, self._handle_physics_half_life),

            # De Broglie wavelength: λ = h/p
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?de\s+broglie\s+wavelength\s+for\s+momentum\s+([0-9.]+)\s*(?:kg·m/s)?", re.IGNORECASE),
             "physics_debroglie", True, self._handle_physics_debroglie),

            # Photon energy: E = h f
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?photon\s+energy\s+for\s+frequency\s+([0-9.]+)\s*(?:Hz)?", re.IGNORECASE),
             "physics_photon_energy", True, self._handle_physics_photon_energy),

            # Mass‑energy equivalence: E = m c²
            (re.compile(r"(?:calculate|find|what is)\s+(?:the\s+)?energy\s+equivalent\s+of\s+mass\s+([0-9.]+)\s*(?:kg)?", re.IGNORECASE),
             "physics_eme", True, self._handle_physics_eme),
        ])

    # ========== HANDLER METHODS ==========

    # --- Mathematics handlers ---
    def _handle_derive(self, match):
        expr = match.group(1).strip()
        var = match.group(2) if match.lastindex >= 2 and match.group(2) else 'x'
        expr = expr.replace('squared', '**2').replace('cubed', '**3')
        return {"expression": expr, "variable": var, "explanation": f"Finding derivative with respect to {var}"}

    def _handle_derive_dx(self, match):
        var = match.group(1)
        expr = match.group(2).strip()
        return {"expression": expr, "variable": var, "explanation": f"Finding derivative with respect to {var}"}

    def _handle_derive_fprime(self, match):
        var = match.group(1) if match.group(1) else 'x'
        expr = match.group(2).strip()
        return {"expression": expr, "variable": var, "explanation": f"Finding derivative with respect to {var}"}

    def _handle_integral_definite(self, match):
        expr = match.group(1).strip()
        a = match.group(2)
        b = match.group(3)
        var = match.group(4) if match.lastindex >= 4 and match.group(4) else 'x'
        return {"expression": expr, "limits": [a, b], "variable": var, "explanation": f"Definite integral from {a} to {b}"}

    def _handle_integral_indefinite(self, match):
        expr = match.group(1).strip()
        var = match.group(2) if match.lastindex >= 2 and match.group(2) else 'x'
        return {"expression": expr, "variable": var, "explanation": f"Indefinite integral with respect to {var}"}

    def _handle_integral_unicode(self, match):
        expr = match.group(1).strip()
        var = match.group(2)
        return {"expression": expr, "variable": var, "explanation": f"Indefinite integral with respect to {var}"}

    def _handle_limit(self, match):
        expr = match.group(1).strip()
        var = match.group(2)
        approach = match.group(3)
        return {"expression": expr, "variable": var, "approach": approach, "explanation": f"Limit as {var} → {approach}"}

    def _handle_limit_alt(self, match):
        var = match.group(1)
        approach = match.group(2)
        expr = match.group(3).strip()
        return {"expression": expr, "variable": var, "approach": approach, "explanation": f"Limit as {var} → {approach}"}

    def _handle_series(self, match):
        expr = match.group(1).strip()
        about = match.group(2)
        order = match.group(3) if match.lastindex >= 3 and match.group(3) else '6'
        return {"expression": expr, "about": about, "order": order, "explanation": f"Series expansion about {about}"}

    def _handle_solve(self, match):
        expr = match.group(1).strip()
        var = match.group(2) if match.lastindex >= 2 and match.group(2) else 'x'
        return {"expression": expr, "variable": var, "explanation": f"Solving equation for {var}"}

    def _handle_solve_roots(self, match):
        expr = match.group(1).strip()
        return {"expression": expr, "variable": 'x', "explanation": f"Finding roots of {expr}"}

    def _handle_plot(self, match):
        expr = match.group(1).strip()
        xmin = match.group(2)
        xmax = match.group(3)
        var = match.group(4) if match.lastindex >= 4 and match.group(4) else 'x'
        return {"expression": expr, "xmin": xmin, "xmax": xmax, "variable": var, "explanation": f"Plotting from {xmin} to {xmax}"}

    def _handle_plot3d(self, match):
        expr = match.group(1).strip()
        xmin = match.group(2)
        xmax = match.group(3)
        ymin = match.group(5)
        ymax = match.group(6)
        return {"expression": expr, "xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax, "explanation": "3D surface plot (PREMIUM FEATURE)"}

    def _handle_matrix_mult(self, match):
        A = match.group(1).strip()
        B = match.group(2).strip()
        return {"expression": f"{A} * {B}", "explanation": "Matrix multiplication"}

    def _handle_matrix_inverse(self, match):
        A = match.group(1).strip()
        return {"expression": A, "explanation": "Matrix inverse"}

    def _handle_matrix_det(self, match):
        A = match.group(1).strip()
        return {"expression": A, "explanation": "Matrix determinant"}

    def _handle_unit(self, match):
        value = match.group(1)
        from_unit = match.group(2)
        to_unit = match.group(3)
        expr = f"{value} {from_unit} to {to_unit}"
        return {"expression": expr, "explanation": f"Converting {value} {from_unit} to {to_unit}"}

    def _handle_unit_simple(self, match):
        value = match.group(1)
        from_unit = match.group(2)
        to_unit = match.group(3)
        expr = f"{value} {from_unit} to {to_unit}"
        return {"expression": expr, "explanation": f"Converting {value} {from_unit} to {to_unit}"}

    def _handle_stat_mean(self, match):
        data = match.group(1).strip()
        return {"expression": data, "explanation": "Calculating mean"}

    def _handle_stat_median(self, match):
        data = match.group(1).strip()
        return {"expression": data, "explanation": "Calculating median"}

    def _handle_stat_std(self, match):
        data = match.group(1).strip()
        return {"expression": data, "explanation": "Calculating standard deviation"}

    def _handle_ode(self, match):
        ode = match.group(1).strip()
        return {"expression": ode, "explanation": "Solving differential equation"}

    def _handle_ode_raw(self, match):
        ode = match.group(1).strip()
        return {"expression": ode, "explanation": "Solving differential equation"}

    def _handle_calc(self, match):
        expr = match.group(1).strip()
        expr = re.sub(r'[^0-9x\s\+\-\*\/\^\(\)\.]', '', expr)
        return {"expression": expr, "explanation": f"Calculating: {expr}"}

    def _handle_calc_binary(self, match):
        a = match.group(1)
        op = match.group(2)
        b = match.group(3)
        expr = f"{a} {op} {b}"
        return {"expression": expr, "explanation": f"Calculating: {expr}"}

    # --- Physics handlers (all premium) ---
    def _handle_physics_force(self, match):
        mass = float(match.group(1))
        acc = float(match.group(2))
        result = mass * acc
        return {
            "command": "physics_force",
            "expression": f"{mass} {acc}",
            "result": result,
            "unit": "N",
            "explanation": f"F = {mass} × {acc} = {result} N"
        }

    def _handle_physics_weight(self, match):
        mass = float(match.group(1))
        planet = match.group(2).lower() if match.lastindex >= 2 and match.group(2) else 'earth'
        g = {'earth': 9.8, 'moon': 1.62, 'mars': 3.71, 'jupiter': 24.79}.get(planet, 9.8)
        result = mass * g
        return {
            "command": "physics_weight",
            "expression": f"{mass} {planet}",
            "result": result,
            "unit": "N",
            "explanation": f"Weight on {planet.capitalize()}: {mass} × {g} = {result} N"
        }

    def _handle_physics_ke(self, match):
        mass = float(match.group(1))
        vel = float(match.group(2))
        result = 0.5 * mass * vel**2
        return {
            "command": "physics_ke",
            "expression": f"{mass} {vel}",
            "result": result,
            "unit": "J",
            "explanation": f"KE = 0.5 × {mass} × {vel}² = {result} J"
        }

    def _handle_physics_pe(self, match):
        mass = float(match.group(1))
        height = float(match.group(2))
        g = float(match.group(3)) if match.lastindex >= 3 and match.group(3) else 9.8
        result = mass * g * height
        return {
            "command": "physics_pe",
            "expression": f"{mass} {height} {g}",
            "result": result,
            "unit": "J",
            "explanation": f"PE = {mass} × {g} × {height} = {result} J"
        }

    def _handle_physics_ohms(self, match):
        quantity = match.group(1).lower()
        v = match.group(2)
        i = match.group(3)
        r = match.group(4)
        # Determine which two are provided (non‑None)
        vals = {}
        if v: vals['voltage'] = float(v)
        if i: vals['current'] = float(i)
        if r: vals['resistance'] = float(r)

        if 'voltage' in vals and 'current' in vals:
            result = vals['voltage'] / vals['current']
            unit = 'Ω'
            expl = f"R = V / I = {vals['voltage']} / {vals['current']} = {result} Ω"
        elif 'voltage' in vals and 'resistance' in vals:
            result = vals['voltage'] / vals['resistance']
            unit = 'A'
            expl = f"I = V / R = {vals['voltage']} / {vals['resistance']} = {result} A"
        elif 'current' in vals and 'resistance' in vals:
            result = vals['current'] * vals['resistance']
            unit = 'V'
            expl = f"V = I × R = {vals['current']} × {vals['resistance']} = {result} V"
        else:
            result = None
            unit = ''
            expl = "Insufficient data provided."

        return {
            "command": "physics_ohms",
            "expression": f"{v or ''} {i or ''} {r or ''}",
            "result": result,
            "unit": unit,
            "explanation": expl
        }

    def _handle_physics_power(self, match):
        v = match.group(1)
        i = match.group(2)
        r = match.group(3)
        if v and i:
            result = float(v) * float(i)
            unit = 'W'
            expl = f"P = V × I = {v} × {i} = {result} W"
        elif i and r:
            i_val = float(i)
            r_val = float(r)
            result = i_val**2 * r_val
            unit = 'W'
            expl = f"P = I² × R = {i_val}² × {r_val} = {result} W"
        elif v and r:
            v_val = float(v)
            r_val = float(r)
            result = v_val**2 / r_val
            unit = 'W'
            expl = f"P = V² / R = {v_val}² / {r_val} = {result} W"
        else:
            result = None
            unit = ''
            expl = "Insufficient data provided."
        return {
            "command": "physics_power",
            "expression": f"{v or ''} {i or ''} {r or ''}",
            "result": result,
            "unit": unit,
            "explanation": expl
        }

    def _handle_physics_gas(self, match):
        target = match.group(1).lower()
        p = match.group(2)
        v = match.group(3)
        n = match.group(4)
        t = match.group(5)
        R = 8.314
        if target == 'pressure' and v and n and t:
            v_val, n_val, t_val = float(v), float(n), float(t)
            result = (n_val * R * t_val) / v_val
            unit = 'Pa'
            expl = f"P = nRT / V = ({n_val} × {R} × {t_val}) / {v_val} = {result} Pa"
        elif target == 'volume' and p and n and t:
            p_val, n_val, t_val = float(p), float(n), float(t)
            result = (n_val * R * t_val) / p_val
            unit = 'm³'
            expl = f"V = nRT / P = ({n_val} × {R} × {t_val}) / {p_val} = {result} m³"
        elif target == 'moles' and p and v and t:
            p_val, v_val, t_val = float(p), float(v), float(t)
            result = (p_val * v_val) / (R * t_val)
            unit = 'mol'
            expl = f"n = PV / RT = ({p_val} × {v_val}) / ({R} × {t_val}) = {result} mol"
        elif target == 'temperature' and p and v and n:
            p_val, v_val, n_val = float(p), float(v), float(n)
            result = (p_val * v_val) / (n_val * R)
            unit = 'K'
            expl = f"T = PV / nR = ({p_val} × {v_val}) / ({n_val} × {R}) = {result} K"
        else:
            result = None
            unit = ''
            expl = "Insufficient data provided."
        return {
            "command": "physics_gas",
            "expression": f"{p or ''} {v or ''} {n or ''} {t or ''}",
            "result": result,
            "unit": unit,
            "explanation": expl
        }

    def _handle_physics_wave_speed(self, match):
        freq = float(match.group(1))
        wl = float(match.group(2))
        result = freq * wl
        return {
            "command": "physics_wave_speed",
            "expression": f"{freq} {wl}",
            "result": result,
            "unit": "m/s",
            "explanation": f"v = f × λ = {freq} × {wl} = {result} m/s"
        }

    def _handle_physics_freq(self, match):
        period = float(match.group(1))
        result = 1 / period
        return {
            "command": "physics_freq",
            "expression": f"{period}",
            "result": result,
            "unit": "Hz",
            "explanation": f"f = 1 / T = 1 / {period} = {result} Hz"
        }

    def _handle_physics_lens(self, match):
        u = float(match.group(1))
        v = float(match.group(2))
        f = 1 / (1/u + 1/v)
        return {
            "command": "physics_lens",
            "expression": f"{u} {v}",
            "result": f,
            "unit": "m",
            "explanation": f"1/f = 1/{u} + 1/{v} = {1/u+1/v:.4f} → f = {f:.4f} m"
        }

    def _handle_physics_snell(self, match):
        theta1 = float(match.group(1))
        n1 = float(match.group(2))
        n2 = float(match.group(3))
        sin_theta2 = n1 / n2 * math.sin(math.radians(theta1))
        if sin_theta2 > 1:
            return {"command": "physics_snell", "explanation": "Total internal reflection (no refraction)"}
        theta2 = math.degrees(math.asin(sin_theta2))
        return {
            "command": "physics_snell",
            "expression": f"{theta1} {n1} {n2}",
            "result": theta2,
            "unit": "°",
            "explanation": f"sin(θ2) = ({n1}/{n2})·sin({theta1}°) = {sin_theta2:.4f} → θ2 = {theta2:.2f}°"
        }

    def _handle_physics_decay(self, match):
        t = float(match.group(1))
        lam = float(match.group(2))
        n0 = float(match.group(3))
        result = n0 * math.exp(-lam * t)
        return {
            "command": "physics_decay",
            "expression": f"{t} {lam} {n0}",
            "result": result,
            "unit": "",
            "explanation": f"N = N0·e^(-λt) = {n0} × e^(-{lam}×{t}) = {result}"
        }

    def _handle_physics_half_life(self, match):
        lam = float(match.group(1))
        result = math.log(2) / lam
        return {
            "command": "physics_half_life",
            "expression": f"{lam}",
            "result": result,
            "unit": "s",
            "explanation": f"t½ = ln(2)/λ = 0.6931 / {lam} = {result} s"
        }

    def _handle_physics_debroglie(self, match):
        p = float(match.group(1))
        h = 6.626e-34
        result = h / p
        return {
            "command": "physics_debroglie",
            "expression": f"{p}",
            "result": result,
            "unit": "m",
            "explanation": f"λ = h / p = {h} / {p} = {result} m"
        }

    def _handle_physics_photon_energy(self, match):
        f = float(match.group(1))
        h = 6.626e-34
        result = h * f
        return {
            "command": "physics_photon_energy",
            "expression": f"{f}",
            "result": result,
            "unit": "J",
            "explanation": f"E = h·f = {h} × {f} = {result} J"
        }

    def _handle_physics_eme(self, match):
        m = float(match.group(1))
        c = 299792458
        result = m * c**2
        return {
            "command": "physics_eme",
            "expression": f"{m}",
            "result": result,
            "unit": "J",
            "explanation": f"E = m·c² = {m} × ({c})² = {result} J"
        }

    # ========== ENHANCED GENERIC EXTRACTION ==========

    def _extract_math_expression(self, text):
        """
        Attempt to extract a mathematical expression from free text
        when no specific pattern matches.
        """
        # Convert common word operators to symbols
        text = text.lower()
        replacements = {
            ' plus ': ' + ',
            ' minus ': ' - ',
            ' times ': ' * ',
            ' multiplied by ': ' * ',
            ' divided by ': ' / ',
            ' over ': ' / ',
            ' to the power of ': ' ^ ',
            ' squared': '**2',
            ' cubed': '**3',
        }
        for word, symbol in replacements.items():
            text = text.replace(word, symbol)

        # Look for patterns like "2+2", "x^2", "3*x", "5/2", etc.
        # This regex tries to capture a basic arithmetic expression with numbers, x, operators, parentheses.
        math_pattern = r'([0-9x\s\+\-\*\/\^\(\)\.]+)'
        match = re.search(math_pattern, text)
        if match:
            expr = match.group(1).strip()
            # Clean up any remaining non-math characters
            expr = re.sub(r'[^0-9x\s\+\-\*\/\^\(\)\.]', '', expr)
            if expr and any(c in expr for c in ['+', '-', '*', '/', '^']):
                # If it contains an equals sign, it might be an equation
                if '=' in expr:
                    return {"command": "solve", "expression": expr, "explanation": f"Solving: {expr}"}
                else:
                    return {"command": "calc", "expression": expr, "explanation": f"Calculating: {expr}"}
        return None

    # ========== MAIN INTERPRET METHOD ==========
    def interpret(self, user_text: str) -> dict:
        """
        Parse user_text and return a dictionary with:
          - command: the bot command to use
          - expression: the mathematical expression
          - explanation: human‑readable description
          - premium: boolean indicating if this is a premium feature
          - confidence: high/medium/low
          - plus any extra fields (limits, variable, result, unit, etc.)
        """
        user_text = user_text.strip()
        if not user_text:
            return self._not_understood()

        # Try each pattern in order
        for pattern, command, is_premium, handler in self.patterns:
            match = pattern.search(user_text)
            if match:
                try:
                    result_dict = handler(match)
                    # Base dictionary
                    out = {
                        "command": command,
                        "expression": result_dict.get("expression", ""),
                        "explanation": result_dict.get("explanation", f"Executing {command}"),
                        "premium": is_premium,
                        "confidence": "high"
                    }
                    # Add any extra fields from the handler
                    for key, value in result_dict.items():
                        if key not in out:
                            out[key] = value
                    return out
                except Exception as e:
                    logger.error(f"Error handling pattern {pattern.pattern}: {e}")
                    continue

        # If no pattern matched, try generic extraction
        generic = self._extract_math_expression(user_text)
        if generic:
            generic["confidence"] = "low"
            generic["premium"] = False  # basic calc/solve are free
            return generic

        # Nothing understood
        return self._not_understood()

    def _not_understood(self):
        return {
            "command": "none",
            "expression": None,
            "explanation": "I couldn't understand that. Premium users get advanced natural language understanding! Upgrade with /buy",
            "premium": True,
            "confidence": "none"
        }


# ====== COMPATIBILITY LAYER ======
class LLMHandler:
    """Dummy class to maintain compatibility with existing code."""
    def __init__(self, provider=None, api_key=None):
        self.interpreter = PremiumSmartInterpreter()
        self.provider = "built-in"

    def ask(self, user_text):
        result = self.interpreter.interpret(user_text)
        return result.get("explanation", "")


def interpret_math_query(user_text, llm_handler=None):
    """Main entry point called from bot.py."""
    interpreter = PremiumSmartInterpreter()
    return interpreter.interpret(user_text)
