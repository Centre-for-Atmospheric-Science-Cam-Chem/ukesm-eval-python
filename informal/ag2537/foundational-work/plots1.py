#!/usr/bin/env python3
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

obs_file  = r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\OMI_MLS_ozone.nc"
mod1_file = r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr061_O3_tropo_DU.nc"
mod2_file = r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr226_O3_tropo_DU.nc"

obs_var   = "ozone_column"
mod_var   = "troposphere_only_ozone_column"
output_pdf = "seasonal_zonal_plots_both_models.pdf"

colors = {"mod1": "#E69F00", "mod2": "#56B4E9", "obs": "#000000"}
labels = {"mod1": "UKESM-1.1", "mod2": "UKESM-1.3", "obs": "Observation"}

def get_mean_std(data, season):
    """Return zonal mean and std (over years) for a season or annual."""
    if season != "Annual":
        sel = data.sel(time=data["time"][data["time.season"] == season])
        mean = sel.mean("time").mean("lon")
        std  = sel.std("time").mean("lon")
    else:
        mean = data.mean("time").mean("lon")
        std  = data.std("time").mean("lon")
    return mean, std

def main():
    # Load obs & both models, renaming dims for consistency
    obs_ds  = xr.open_dataset(obs_file ).rename({"t": "time", "latitude": "lat", "longitude": "lon"})
    mod1_ds = xr.open_dataset(mod1_file).rename({"latitude": "lat", "longitude": "lon"})
    mod2_ds = xr.open_dataset(mod2_file).rename({"latitude": "lat", "longitude": "lon"})

    # Drop bounds vars
    for ds in [mod1_ds, mod2_ds]:
        for v in list(ds.data_vars):
            if "bnds" in v.lower():
                ds = ds.drop_vars(v)

    obs  = obs_ds[obs_var]
    mod1 = mod1_ds[mod_var]
    mod2 = mod2_ds[mod_var]

    t0 = max(mod1.time.min().values, mod2.time.min().values)
    t1 = min(mod1.time.max().values, mod2.time.max().values)
    obs  = obs.sel(time=slice(str(t0), str(t1)))
    mod1 = mod1.sel(time=slice(str(t0), str(t1)))
    mod2 = mod2.sel(time=slice(str(t0), str(t1)))

    mod1 = mod1.interp(lat=obs.lat)
    mod2 = mod2.interp(lat=obs.lat)

    seasons = ["DJF","MAM","JJA","SON"]

    # Precompute means and stds for all seasons
    obs_zonal_mean_std = {s: get_mean_std(obs, s)  for s in seasons + ["Annual"]}
    mod1_zonal_mean_std = {s: get_mean_std(mod1, s) for s in seasons + ["Annual"]}
    mod2_zonal_mean_std = {s: get_mean_std(mod2, s) for s in seasons + ["Annual"]}

    with PdfPages(output_pdf) as pdf:
        for s in seasons + ["Annual"]:
            fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
            lat = obs_zonal_mean_std[s][0].lat

            # Model panel
            m1_mean, m1_std = mod1_zonal_mean_std[s]
            m2_mean, m2_std = mod2_zonal_mean_std[s]
            axes[0].plot(m1_mean, lat, "-", color=colors["mod1"], label=labels["mod1"])
            axes[0].fill_betweenx(lat, m1_mean - m1_std, m1_mean + m1_std, color=colors["mod1"], alpha=0.15)
            axes[0].plot(m2_mean, lat, "-", color=colors["mod2"], label=labels["mod2"])
            axes[0].fill_betweenx(lat, m2_mean - m2_std, m2_mean + m2_std, color=colors["mod2"], alpha=0.15)
            axes[0].set_xlim(15, 45)
            axes[0].set_title(f"{s} – Models")
            axes[0].set_xlabel("O₃ (DU)")
            axes[0].legend()
            axes[0].grid(True)

            # Observation panel
            obs_mean, obs_std = obs_zonal_mean_std[s]
            axes[1].plot(obs_mean, lat, "-", color=colors["obs"], label=labels["obs"])
            axes[1].fill_betweenx(lat, obs_mean - obs_std, obs_mean + obs_std, color=colors["obs"], alpha=0.15)
            axes[1].set_xlim(15, 45)
            axes[1].set_title(f"{s} – Observation")
            axes[1].set_xlabel("O₃ (DU)")
            axes[1].grid(True)

            # Percent bias (both models vs obs), with error bands
            pct_bias1 = 100 * (m1_mean - obs_mean) / obs_mean
            pct_bias2 = 100 * (m2_mean - obs_mean) / obs_mean

            # Error band for percent bias (propagate uncertainty)
            pct_band1 = 100 * np.sqrt((m1_std/obs_mean)**2 + (obs_std*m1_mean/obs_mean**2)**2)
            pct_band2 = 100 * np.sqrt((m2_std/obs_mean)**2 + (obs_std*m2_mean/obs_mean**2)**2)

            axes[2].plot(pct_bias1, lat, "-", color=colors["mod1"], label=f"{labels['mod1']} % bias")
            axes[2].fill_betweenx(lat, pct_bias1 - pct_band1, pct_bias1 + pct_band1, color=colors["mod1"], alpha=0.15)
            axes[2].plot(pct_bias2, lat, "-", color=colors["mod2"], label=f"{labels['mod2']} % bias")
            axes[2].fill_betweenx(lat, pct_bias2 - pct_band2, pct_bias2 + pct_band2, color=colors["mod2"], alpha=0.15)
            axes[2].axvline(0, color="0.5", ls="--")
            axes[2].set_title(f"{s} – % Bias")
            axes[2].set_xlabel("Percent bias (%)")
            axes[2].legend()
            axes[2].grid(True)

            # Formatting
            for ax in axes:
                ax.set_ylim(lat.min(), lat.max())
            axes[0].set_ylabel("Latitude")
            fig.suptitle(f"Seasonal Zonal Mean — {s}", fontsize=14)
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            pdf.savefig(fig)
            plt.close(fig)

    print(f"Saved as file {output_pdf}")

if __name__ == "__main__":
    main()
