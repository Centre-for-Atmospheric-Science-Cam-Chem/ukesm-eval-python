import numpy as np

def load_model(path, species):
    """Stub loader: ignore path/species, return dummy model profile."""
    pressure = np.linspace(1000, 100, 10)  # hPa
    values   = np.linspace(0.0, 1.0, 10)    # normalized
    return {"pressure": pressure, "values": values}

