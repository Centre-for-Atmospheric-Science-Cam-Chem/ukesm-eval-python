import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# Dummy inputs
ds1 = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\co_AERmon_UKESM1-0-LL_historical_r1i1p1f2_gn_185001-189912.nc")
ds2 = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\co_AERmon_UKESM1-0-LL_historical_r1i1p1f2_gn_195001-199912.nc")

stations = pd.read_csv("config/gaw_noaa_stations.csv")

# Filter stations to your model’s lat/lon bounds

lat_min, lat_max = float(ds1.lat.min()), float(ds1.lat.max())
lon_min, lon_max = float(ds1.lon.min()), float(ds1.lon.max())

stations = stations[
    stations.Latitude.between(lat_min, lat_max) &
    stations.Longitude.between(lon_min, lon_max)
]

# Build the sites dict

sites = {
    row["Site Name"]: (row["Latitude"], row["Longitude"])
    for _, row in stations.iterrows()
}


# Utility functions

def get_nearest_point(da, lat, lon):
    return da.sel(lat=lat, lon=lon, method="nearest")

def mean_bias_error(obs, mod):
    return 100 * ((mod - obs).mean() / obs.mean()).item()

def correlation(obs, mod):
    return np.corrcoef(obs, mod)[0, 1]

with PdfPages("co_comparison_plots.pdf") as pdf:
    fig, axes = plt.subplots(nrows=6, ncols=3, figsize=(12, 18))
    axes = axes.flatten()

    for ax, (site, (lat, lon)) in zip(axes, sites.items()):
        try:
            # Extract data at nearest grid point & level 850 hPa
            obs = get_nearest_point(ds1["co"].sel(lev=850, method="nearest"), lat, lon)
            mod = get_nearest_point(ds2["co"].sel(lev=850, method="nearest"), lat, lon)

            # Group by month and compute mean & std
            obs_grp = obs.groupby("time.month")
            mod_grp = mod.groupby("time.month")

            obs_mean = obs_grp.mean("time")
            obs_std  = obs_grp.std("time")
            mod_mean = mod_grp.mean("time")

        
            ax.errorbar(
                range(1, 13), obs_mean, yerr=obs_std,
                fmt="-ok", mfc="white", capsize=3, label="obs"
            )
            ax.plot(
                range(1, 13), mod_mean,
                "-or", mfc="white", label="model"
            )
            ax.grid(True, which="both", linestyle="--", linewidth=0.5)

            
            r   = correlation(obs_mean, mod_mean)
            mbe = mean_bias_error(obs_mean, mod_mean)

            
            ew = "W" if lon < 0 else "E"
            ns = "S" if lat < 0 else "N"
            ax.set_title(f"{site} ({abs(lat):.1f}°{ns}, {abs(lon):.1f}°{ew})",
                         fontsize=10, weight="bold")
            ax.set_xticks([1, 3, 5, 7, 9, 11])
            ax.set_xticklabels(["Jan","Mar","May","Jul","Sep","Nov"])
            ax.set_ylabel("CO (ppbv)")
            ax.text(0.5, 0.05,
                    f"r = {r:.3f}   MBE = {mbe:.1f}%",
                    transform=ax.transAxes, ha="center", fontsize=9)

        except Exception as e:
            ax.set_title(f"{site} (Error)", fontsize=10, weight="bold")
            ax.text(0.5, 0.5, str(e),
                    ha="center", va="center", fontsize=8)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, fontsize=10)
    fig.tight_layout(rect=[0,0,1,0.95])
    pdf.savefig(fig)
    plt.close()

print("PDF successfully saved as 'co_comparison_plots.pdf'")
