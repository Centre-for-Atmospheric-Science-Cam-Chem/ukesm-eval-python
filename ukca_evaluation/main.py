

# main.py
import argparse
from src.ukca_eval.io.load_model import load_model
from src.ukca_eval.io.load_obs import load_obs
from src.ukca_eval.plotting.profiles import plot_vertical_stub

def main():
    parser = argparse.ArgumentParser(description="Single-plot stub for UKCA Evaluation Toolkit")
    parser.add_argument("--model-file", required=True, help="Path to model file (stub)")
    parser.add_argument("--obs-file", required=True, help="Path to observation file (stub)")
    parser.add_argument("--species",   required=True, help="Species to plot (e.g. O3)")
    args = parser.parse_args()

    # 1. Load raw data (stub)
    model_data = load_model(args.model_file, args.species)
    obs_data   = load_obs(args.obs_file,   args.species)

    # 2. Plot stub
    fig = plot_vertical_stub(model_data, obs_data, title=f"{args.species} Profile (stub)")
    
    import os
    from pathlib import Path
    # Always save to outputs/{species}_profile.png
    outdir = Path("outputs")
    outdir.mkdir(exist_ok=True)     # make outputs/ if needed
    outfile = outdir / f"{args.species}_profile.png"
    fig.savefig(outfile)
    print(f"Saved stub plot to {outfile}")

if __name__ == "__main__":
    main()

# src/ukca_eval/io/load_model.py

def load_model(path, var=None):
    """
    Stub function: returns dummy model data as a list or numpy array.
    """
    import numpy as np
    # Dummy vertical coordinate (pressure)
    pressure = np.linspace(1000, 100, 10)
    # Dummy mixing ratio
    data = np.linspace(0, 1, 10)
    return {"pressure": pressure, "data": data}

# src/ukca_eval/io/load_obs.py

def load_obs(path, var=None):
    """
    Stub function: returns dummy observation data matching model shape.
    """
    import numpy as np
    pressure = np.linspace(1000, 100, 10)
    data = np.linspace(0.1, 0.9, 10)
    return {"pressure": pressure, "data": data}

# src/ukca_eval/plotting/profiles.py
import matplotlib.pyplot as plt

def plot_vertical_profile(model, obs, title="Profile (stub)"):
    """
    Stub plotter: overlays model and observation vs pressure.
    Expects `model` and `obs` dicts with keys "pressure" and "data".
    """
    fig, ax = plt.subplots()
    ax.plot(model["data"], model["pressure"], label="Model")
    ax.plot(obs["data"],   obs["pressure"],   label="Obs", linestyle="--")
    ax.set_ylim(max(model["pressure"]), min(model["pressure"]))  # invert y-axis
    ax.set_xlabel("Mixing ratio (stub units)")
    ax.set_ylabel("Pressure (hPa)")
    ax.set_title(title)
    ax.legend()
    return fig
