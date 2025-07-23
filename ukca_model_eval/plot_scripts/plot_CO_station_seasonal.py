import yaml
from utils.data_io import load_model_data, load_station_csv
from utils.processing import get_nearest_point, filter_stations, mean_bias_error, correlation
from utils.plot_utils import set_plot_style, plot_station_seasonal
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from utils.units import convert


# --- Load config ---
with open("config.yaml") as f:
    config = yaml.safe_load(f)


ds1 = load_model_data(config['model_file'])
ds2 = load_model_data(config['model_file'])
stations = load_station_csv(config['stations_csv'])
var_name = config['var_name']
level = config['level']
ylim = config.get('ylim', None)
model_units = config['model_units']
plot_units = config['plot_units']

# Filter stations to model domain
lat_min, lat_max = float(ds1.lat.min()), float(ds1.lat.max())
lon_min, lon_max = float(ds1.lon.min()), float(ds1.lon.max())
stations = filter_stations(stations, lat_min, lat_max, lon_min, lon_max)

# Build sites dict
sites = {row["Site Name"]: (row["Latitude"], row["Longitude"]) for _, row in stations.iterrows()}

set_plot_style()

with PdfPages(config['output_pdf']) as pdf:
    fig, axes = plt.subplots(nrows=6, ncols=3, figsize=(12, 18))
    axes = axes.flatten()

    for ax, (site, (lat, lon)) in zip(axes, sites.items()):
        try:
            obs = get_nearest_point(ds1[var_name].sel(lev=level, method="nearest"), lat, lon)
            mod = get_nearest_point(ds2[var_name].sel(lev=level, method="nearest"), lat, lon)
            obs_grp = obs.groupby("time.month")
            mod_grp = mod.groupby("time.month")
            obs_mean = obs_grp.mean("time")
            obs_std  = obs_grp.std("time")
            mod_mean = mod_grp.mean("time")
            r   = correlation(obs_mean, mod_mean)
            mbe = mean_bias_error(obs_mean, mod_mean)
            obs_mean_plot = convert(obs_mean, model_units, plot_units)
            obs_std_plot  = convert(obs_std, model_units, plot_units)
            mod_mean_plot = convert(mod_mean, model_units, plot_units)
            plot_station_seasonal(ax, obs_mean_plot, obs_std_plot, mod_mean_plot, site, lat, lon, r, mbe, ylim, plot_units=config["plot_units"])
        except Exception as e:
            ax.set_title(f"{site} (Error)", fontsize=10, weight="bold")
            ax.text(0.5, 0.5, str(e), ha="center", va="center", fontsize=8)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, fontsize=10)
    fig.tight_layout(rect=[0,0,1,0.95])
    pdf.savefig(fig)
    plt.close()

print(f"PDF successfully saved as '{config['output_pdf']}'")
