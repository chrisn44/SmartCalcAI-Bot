"""
Physics Module for SmartCalcAI Bot
All functions return a tuple (result, steps) where steps is a list of explanation strings.
Premium features.
"""

import math

# ========== MECHANICS ==========

def velocity(initial_velocity, acceleration, time):
    """v = u + a*t"""
    result = initial_velocity + acceleration * time
    steps = [
        f"Using v = u + a·t",
        f"v = {initial_velocity} + ({acceleration} × {time})",
        f"v = {result}"
    ]
    return result, steps

def displacement(initial_velocity, time, acceleration):
    """s = u*t + 0.5*a*t^2"""
    result = initial_velocity * time + 0.5 * acceleration * time**2
    steps = [
        f"Using s = u·t + ½·a·t²",
        f"s = {initial_velocity} × {time} + 0.5 × {acceleration} × {time}²",
        f"s = {result}"
    ]
    return result, steps

def final_velocity_squared(initial_velocity, acceleration, displacement):
    """v² = u² + 2*a*s"""
    result = math.sqrt(initial_velocity**2 + 2 * acceleration * displacement)
    steps = [
        f"Using v² = u² + 2·a·s",
        f"v² = {initial_velocity}² + 2 × {acceleration} × {displacement}",
        f"v² = {initial_velocity**2 + 2 * acceleration * displacement}",
        f"v = √(...) = {result}"
    ]
    return result, steps

def force(mass, acceleration):
    """F = m·a"""
    result = mass * acceleration
    steps = [
        f"Using Newton's second law: F = m·a",
        f"F = {mass} × {acceleration}",
        f"F = {result} N"
    ]
    return result, steps

def weight(mass, gravity=9.8):
    """W = m·g"""
    result = mass * gravity
    steps = [
        f"Weight = mass × gravity",
        f"W = {mass} × {gravity}",
        f"W = {result} N"
    ]
    return result, steps

def friction(normal_force, coefficient):
    """f = μ·N"""
    result = coefficient * normal_force
    steps = [
        f"Friction force = coefficient × normal force",
        f"f = {coefficient} × {normal_force}",
        f"f = {result} N"
    ]
    return result, steps

def momentum(mass, velocity):
    """p = m·v"""
    result = mass * velocity
    steps = [
        f"Momentum = mass × velocity",
        f"p = {mass} × {velocity}",
        f"p = {result} kg·m/s"
    ]
    return result, steps

def impulse(force, time):
    """J = F·t"""
    result = force * time
    steps = [
        f"Impulse = force × time",
        f"J = {force} × {time}",
        f"J = {result} N·s"
    ]
    return result, steps

def work(force, distance, angle=0):
    """W = F·d·cosθ"""
    result = force * distance * math.cos(math.radians(angle))
    steps = [
        f"Work = force × distance × cos(θ)",
        f"W = {force} × {distance} × cos({angle}°)",
        f"W = {result} J"
    ]
    return result, steps

def kinetic_energy(mass, velocity):
    """KE = ½·m·v²"""
    result = 0.5 * mass * velocity**2
    steps = [
        f"Kinetic energy = ½·m·v²",
        f"KE = 0.5 × {mass} × {velocity}²",
        f"KE = {result} J"
    ]
    return result, steps

def potential_energy(mass, height, gravity=9.8):
    """PE = m·g·h"""
    result = mass * gravity * height
    steps = [
        f"Potential energy = m·g·h",
        f"PE = {mass} × {gravity} × {height}",
        f"PE = {result} J"
    ]
    return result, steps

def mechanical_energy(ke, pe):
    """E = KE + PE"""
    result = ke + pe
    steps = [
        f"Total mechanical energy = KE + PE",
        f"E = {ke} + {pe}",
        f"E = {result} J"
    ]
    return result, steps

def power(work, time):
    """P = W / t"""
    result = work / time
    steps = [
        f"Power = work / time",
        f"P = {work} / {time}",
        f"P = {result} W"
    ]
    return result, steps

def pressure(force, area):
    """P = F / A"""
    result = force / area
    steps = [
        f"Pressure = force / area",
        f"P = {force} / {area}",
        f"P = {result} Pa"
    ]
    return result, steps

def density(mass, volume):
    """ρ = m / V"""
    result = mass / volume
    steps = [
        f"Density = mass / volume",
        f"ρ = {mass} / {volume}",
        f"ρ = {result} kg/m³"
    ]
    return result, steps

# ========== ELECTRICITY ==========

def ohms_law(voltage=None, current=None, resistance=None):
    """V = I·R — solve for missing value"""
    if voltage is None and current is not None and resistance is not None:
        result = current * resistance
        steps = [f"V = I·R = {current} × {resistance} = {result} V"]
        return result, steps
    elif current is None and voltage is not None and resistance is not None:
        result = voltage / resistance
        steps = [f"I = V/R = {voltage} / {resistance} = {result} A"]
        return result, steps
    elif resistance is None and voltage is not None and current is not None:
        result = voltage / current
        steps = [f"R = V/I = {voltage} / {current} = {result} Ω"]
        return result, steps
    else:
        raise ValueError("Provide exactly two of voltage, current, resistance.")

def electrical_power(voltage=None, current=None, resistance=None):
    """P = V·I = I²·R = V²/R"""
    if voltage is not None and current is not None:
        result = voltage * current
        steps = [f"P = V·I = {voltage} × {current} = {result} W"]
        return result, steps
    elif current is not None and resistance is not None:
        result = current**2 * resistance
        steps = [f"P = I²·R = {current}² × {resistance} = {result} W"]
        return result, steps
    elif voltage is not None and resistance is not None:
        result = voltage**2 / resistance
        steps = [f"P = V²/R = {voltage}² / {resistance} = {result} W"]
        return result, steps
    else:
        raise ValueError("Provide two of voltage, current, resistance.")

def series_resistance(*resistances):
    """R_total = R1 + R2 + ..."""
    result = sum(resistances)
    steps = [f"R_total = " + " + ".join(str(r) for r in resistances) + f" = {result} Ω"]
    return result, steps

def parallel_resistance(*resistances):
    """1/R_total = 1/R1 + 1/R2 + ..."""
    inv_sum = sum(1 / r for r in resistances)
    result = 1 / inv_sum
    steps = [f"1/R_total = " + " + ".join(f"1/{r}" for r in resistances) + f" = {inv_sum}", f"R_total = 1 / {inv_sum} = {result} Ω"]
    return result, steps

def capacitance(charge, voltage):
    """C = Q / V"""
    result = charge / voltage
    steps = [f"C = Q / V = {charge} / {voltage} = {result} F"]
    return result, steps

def energy_capacitor(capacitance, voltage):
    """E = ½·C·V²"""
    result = 0.5 * capacitance * voltage**2
    steps = [f"Energy = ½·C·V² = 0.5 × {capacitance} × {voltage}² = {result} J"]
    return result, steps

def inductance(flux, current):
    """L = Φ / I"""
    result = flux / current
    steps = [f"L = Φ / I = {flux} / {current} = {result} H"]
    return result, steps

# ========== THERMODYNAMICS ==========

def heat_transfer(mass, specific_heat, delta_temp):
    """Q = m·c·ΔT"""
    result = mass * specific_heat * delta_temp
    steps = [
        f"Heat transfer Q = m·c·ΔT",
        f"Q = {mass} × {specific_heat} × {delta_temp}",
        f"Q = {result} J"
    ]
    return result, steps

def ideal_gas_law(pressure=None, volume=None, moles=None, temperature=None, R=8.314):
    """PV = nRT — solve for missing variable"""
    if pressure is None and all(v is not None for v in [volume, moles, temperature]):
        result = (moles * R * temperature) / volume
        steps = [f"P = nRT / V = ({moles} × {R} × {temperature}) / {volume} = {result} Pa"]
        return result, steps
    elif volume is None and all(v is not None for v in [pressure, moles, temperature]):
        result = (moles * R * temperature) / pressure
        steps = [f"V = nRT / P = ({moles} × {R} × {temperature}) / {pressure} = {result} m³"]
        return result, steps
    elif moles is None and all(v is not None for v in [pressure, volume, temperature]):
        result = (pressure * volume) / (R * temperature)
        steps = [f"n = PV / RT = ({pressure} × {volume}) / ({R} × {temperature}) = {result} mol"]
        return result, steps
    elif temperature is None and all(v is not None for v in [pressure, volume, moles]):
        result = (pressure * volume) / (moles * R)
        steps = [f"T = PV / nR = ({pressure} × {volume}) / ({moles} × {R}) = {result} K"]
        return result, steps
    else:
        raise ValueError("Provide three of pressure, volume, moles, temperature.")

def entropy_change(heat, temperature):
    """ΔS = Q / T"""
    result = heat / temperature
    steps = [f"ΔS = Q / T = {heat} / {temperature} = {result} J/K"]
    return result, steps

# ========== WAVES ==========

def wave_speed(frequency, wavelength):
    """v = f·λ"""
    result = frequency * wavelength
    steps = [f"v = f·λ = {frequency} × {wavelength} = {result} m/s"]
    return result, steps

def frequency_from_period(period):
    """f = 1 / T"""
    result = 1 / period
    steps = [f"f = 1 / T = 1 / {period} = {result} Hz"]
    return result, steps

def doppler_effect(source_freq, source_speed, observer_speed, wave_speed, direction='towards'):
    """Simplified Doppler for sound (observer moving)"""
    if direction == 'towards':
        result = source_freq * (wave_speed + observer_speed) / wave_speed
    else:
        result = source_freq * (wave_speed - observer_speed) / wave_speed
    steps = [
        f"Doppler effect: f' = f·(v ± v₀)/v",
        f"f' = {source_freq} × ({wave_speed} ± {observer_speed}) / {wave_speed}",
        f"f' = {result} Hz"
    ]
    return result, steps

# ========== OPTICS ==========

def lens_focal_length(object_dist, image_dist):
    """1/f = 1/u + 1/v"""
    f = 1 / (1/object_dist + 1/image_dist)
    steps = [f"1/f = 1/{object_dist} + 1/{image_dist} = {1/object_dist + 1/image_dist}", f"f = {f} m"]
    return f, steps

def magnification(object_dist, image_dist):
    """m = -v/u"""
    result = -image_dist / object_dist
    steps = [f"m = -v/u = -{image_dist}/{object_dist} = {result}"]
    return result, steps

def snells_law(n1, angle1, n2):
    """n1·sin(θ1) = n2·sin(θ2) → θ2 = arcsin(n1/n2 * sin(θ1))"""
    sin_theta2 = n1 / n2 * math.sin(math.radians(angle1))
    if sin_theta2 > 1:
        raise ValueError("Total internal reflection")
    theta2 = math.degrees(math.asin(sin_theta2))
    steps = [
        f"Snell's law: n1·sin(θ1) = n2·sin(θ2)",
        f"sin(θ2) = ({n1}/{n2})·sin({angle1}°) = {sin_theta2}",
        f"θ2 = {theta2}°"
    ]
    return theta2, steps

# ========== MODERN PHYSICS ==========

def energy_mass_equivalence(mass):
    """E = m·c²"""
    c = 299792458  # m/s
    result = mass * c**2
    steps = [
        f"Einstein's mass-energy equivalence: E = m·c²",
        f"c = {c} m/s",
        f"E = {mass} × ({c})² = {result} J"
    ]
    return result, steps

def photon_energy(frequency):
    """E = h·f"""
    h = 6.626e-34
    result = h * frequency
    steps = [f"Photon energy: E = h·f = {h} × {frequency} = {result} J"]
    return result, steps

def photon_wavelength(energy):
    """λ = h·c / E"""
    h = 6.626e-34
    c = 299792458
    result = (h * c) / energy
    steps = [f"Photon wavelength: λ = h·c / E = ({h}×{c}) / {energy} = {result} m"]
    return result, steps

def de_broglie_wavelength(momentum):
    """λ = h / p"""
    h = 6.626e-34
    result = h / momentum
    steps = [f"de Broglie wavelength: λ = h / p = {h} / {momentum} = {result} m"]
    return result, steps

def radioactive_decay(initial_amount, decay_constant, time):
    """N = N0·e^(-λt)"""
    result = initial_amount * math.exp(-decay_constant * time)
    steps = [
        f"Radioactive decay: N = N0·e^(-λt)",
        f"N = {initial_amount} × e^(-{decay_constant}×{time})",
        f"N = {result}"
    ]
    return result, steps

def half_life(decay_constant):
    """t½ = ln(2)/λ"""
    result = math.log(2) / decay_constant
    steps = [f"Half‑life: t½ = ln(2)/λ = 0.6931 / {decay_constant} = {result}"]
    return result, steps