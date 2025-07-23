def mol_per_mol_to_ppbv(x):
    """Convert from mol/mol to ppbv."""
    return x * 1e9

def ppbv_to_mol_per_mol(x):
    """Convert from ppbv to mol/mol."""
    return x / 1e9

# Add more as needed
def mol_per_mol_to_pptv(x):
    return x * 1e12

def ppmv_to_mol_per_mol(x):
    return x * 1e-6

# Dictionary for automatic unit conversion (if you want!)
CONVERSIONS = {
    ("mol/mol", "ppbv"): mol_per_mol_to_ppbv,
    ("ppbv", "mol/mol"): ppbv_to_mol_per_mol,
    # etc.
}

def convert(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    func = CONVERSIONS.get((from_unit, to_unit))
    if func is None:
        raise ValueError(f"No conversion from {from_unit} to {to_unit}")
    return func(value)
