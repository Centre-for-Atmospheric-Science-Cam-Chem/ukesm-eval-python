import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

obs_file   = r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\OMI_MLS_ozone.nc"
mod_file   = r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr226_O3_tropo_DU.nc"

obs_var    = "ozone_column"                    
mod_var    = "troposphere_only_ozone_column"   

output_pdf = "seasonal_zonal_plots.pdf"


def main():
    
    obs_ds = xr.open_dataset(obs_file).rename({
        "t": "time", "latitude": "lat", "longitude": "lon"
    })
    mod_ds = xr.open_dataset(mod_file).rename({
        "latitude": "lat", "longitude": "lon"
    })

    #drop any bounds variables from the model
    for v in list(mod_ds.data_vars):
        if "bnds" in v.lower():
            mod_ds = mod_ds.drop_vars(v)

    obs = obs_ds[obs_var]
    mod = mod_ds[mod_var]

    #slice satellite to the model's time range
    t0 = mod.time.min().values
    t1 = mod.time.max().values
    obs = obs.sel(time=slice(str(t0), str(t1)))
    
    # align model latitudes to the obs grid
    mod = mod.interp(lat=obs.lat)

    # compute seasonal and annual means
    seasons = ["DJF","MAM","JJA","SON"]
    
    obs_seas = obs.groupby("time.season").mean("time")
    mod_seas = mod.groupby("time.season").mean("time")
    
    obs_annual = obs.mean("time")
    mod_annual = mod.mean("time")

    #compute zonal means (collapse longitude)
    obs_zonal = {s: obs_seas.sel(season=s).mean("lon") for s in seasons}
    mod_zonal = {s: mod_seas.sel(season=s).mean("lon") for s in seasons}
    obs_zonal["Annual"] = obs_annual.mean("lon")
    mod_zonal["Annual"] = mod_annual.mean("lon")

    with PdfPages(output_pdf) as pdf:
        for s in seasons + ["Annual"]:
            fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
            lat = obs_zonal[s].lat

            # Model panel
            axes[0].plot(mod_zonal[s], lat, '-r', label="Model")
            axes[0].set_title(f"{s} – Model")
            axes[0].set_xlabel("O₃ (DU)")
            axes[0].grid(True)

            # Obs panel
            axes[1].plot(obs_zonal[s], lat, '-k', label="Obs")
            axes[1].set_title(f"{s} – Observation")
            axes[1].set_xlabel("O₃ (DU)")
            axes[1].grid(True)

            # Percent‐bias panel
            pct_bias = 100 * (mod_zonal[s] - obs_zonal[s]) / obs_zonal[s]
            axes[2].plot(pct_bias, lat, '-b', label="% bias")
            axes[2].axvline(0, color='0.5', linestyle='--')
            axes[2].set_title(f"{s} – % Bias")
            axes[2].set_xlabel("Percent bias (%)")
            axes[2].grid(True)

            # Formatting
            for ax in axes:
                ax.set_ylim(lat.min(), lat.max())
            axes[0].set_ylabel("Latitude")

            fig.suptitle(f"Seasonal Zonal Mean — {s}", fontsize=14)
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])

            pdf.savefig(fig)
            plt.close(fig)

    print(f"Saved {output_pdf}")

if __name__ == "__main__":
    main()
