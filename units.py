from pint import UnitRegistry
import re

ureg = UnitRegistry()
Q_ = ureg.Quantity

# Common unit aliases
UNIT_ALIASES = {
    'km': 'kilometer',
    'm': 'meter',
    'cm': 'centimeter',
    'mm': 'millimeter',
    'mile': 'mile',
    'miles': 'mile',
    'ft': 'foot',
    'feet': 'foot',
    'in': 'inch',
    'inches': 'inch',
    'kg': 'kilogram',
    'g': 'gram',
    'lb': 'pound',
    'lbs': 'pound',
    'c': 'celsius',
    'f': 'fahrenheit',
    'k': 'kelvin',
    'mph': 'mile/hour',
    'kph': 'kilometer/hour',
    'm/s': 'meter/second',
}

def convert_units(text):
    """Convert units from natural language input."""
    # Parse input like "100 km to miles"
    pattern = r'(\d+\.?\d*)\s+([a-zA-Z/]+)\s+to\s+([a-zA-Z/]+)'
    match = re.match(pattern, text.lower())
    
    if not match:
        raise ValueError("Format: <value> <from_unit> to <to_unit> (e.g., '100 km to miles')")
    
    value = float(match.group(1))
    from_unit = match.group(2)
    to_unit = match.group(3)
    
    # Apply aliases
    from_unit = UNIT_ALIASES.get(from_unit, from_unit)
    to_unit = UNIT_ALIASES.get(to_unit, to_unit)
    
    try:
        quantity = value * ureg(from_unit)
        result = quantity.to(to_unit)
        
        steps = [
            f"📝 Converting: {value} {from_unit} → {to_unit}",
            f"📊 1 {from_unit} = {quantity.to(to_unit).magnitude / value:.6f} {to_unit}",
            f"✅ Result: **{result.magnitude:.4f} {to_unit}**"
        ]
        
        return steps, result.magnitude
    except Exception as e:
        raise ValueError(f"Unit conversion error: {e}")