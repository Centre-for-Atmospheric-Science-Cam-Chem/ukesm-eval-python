import numpy as np

def load_obs(path, species):
    """Stub loader: ignore path/species, return dummy obs profile."""
    pressure = np.linspace(1000, 100, 10)    # hPa
    values   = np.linspace(1.0, 0.0, 10)     # normalized (reverse)
    return {"pressure": pressure, "values": values}

