# emmons_co_analysis.py
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path

# ========================
# 1. CONFIGURATION (Previously in YAML)
# ========================
PATHS = {
    "model": "./data/xgywn_co.nc",  # Path to model NetCDF
    "obs": "./data/obs/INTEX-NA_CT_co.stat",  # Obs data for one site
    "output": "./plots/CO_comparison.png"
}

SITE = {
    "name": "INTEX-NA CT",
    "lon_range": [-85, -80],  # Approximate for CT site
    "lat_range": [30, 40],
    "alt_levels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # km
    "month": 7  # July (from R's mon=7)
}

# ========================
# 2. DATA LOADING (Identical to R)
# ========================
def load_obs(obs_path):
    """Load observed CO data exactly like R's read.table()."""
    return pd.read_csv(
        obs_path,
        delim_whitespace=True,
        comment="#",
        header=None,
        usecols=[0, 4, 5],  # ialt (V1), mean (V5), stddev (V6)
        names=["alt", "mean", "stddev"]
    )

def load_model(nc_path, lon, lat, month):
    """Replace ncvar_get() with xarray."""
    ds = xr.open_dataset(nc_path)
    return ds["CO"].sel(
        lon=lon, lat=lat, method="nearest"
    ).isel(time=month - 1) * (1e9 / 28.01)  # ppbv conversion

# ========================
# 3. PROCESSING (Quantiles like R's apply())
# ========================
def calculate_quantiles(model_data):
    """Identical to R's quantile calculation."""
    return np.quantile(model_data, [0.25, 0.5, 0.75], axis=0)

# ========================
# 4. PLOTTING (Replicate R's PDF Output)
# ========================
def plot_comparison(model_q, obs_data, site_info):
    """Match R's plot aesthetics exactly."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Model (Red)
    ax.fill_betweenx(
        obs_data["alt"], model_q[0], model_q[2],  # IQR (25th-75th)
        color="red", alpha=0.5, label="Model IQR"
    )
    ax.plot(model_q[1], obs_data["alt"], "r-", lw=1.5, label="Model Median")

    # Observations (Black)
    ax.errorbar(
        obs_data["mean"], obs_data["alt"],
        xerr=obs_data["stddev"], fmt="o", color="k", capsize=3, label="Obs ±1σ"
    )
    ax.plot(obs_data["mean"], obs_data["alt"], "k-", lw=1.5)

    # Labels/Grid (Like R)
    ax.set(
        xlim=(25, 150),
        xlabel="CO (ppbv)",
        ylabel="Altitude (km)",
        title=f"{site_info['name']}\nLat: {site_info['lat_range'][0]}-{site_info['lat_range'][1]}, "
              f"Lon: {site_info['lon_range'][0]}-{site_info['lon_range'][1]}"
    )
    ax.grid()
    ax.legend()
    return fig

# ========================
# 5. MAIN EXECUTION (Like R Script)
# ========================
if __name__ == "__main__":
    # Load data
    obs = load_obs(PATHS["obs"])
    model = load_model(
        PATHS["model"],
        lon=np.mean(SITE["lon_range"]),  # Approximate center
        lat=np.mean(SITE["lat_range"]),
        month=SITE["month"]
    )
    
    # Process
    quantiles = calculate_quantiles(model)
    
    # Plot
    fig = plot_comparison(quantiles, obs, SITE)
    Path(PATHS["output"]).parent.mkdir(exist_ok=True)
    fig.savefig(PATHS["output"], bbox_inches="tight")
    print(f"Plot saved to {PATHS['output']}")