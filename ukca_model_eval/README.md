# UKCA Model Evaluation in Python

This repository provides a **modular Python framework** for generating multi-station seasonal cycle comparison plots (and more) for atmospheric model output (e.g., CO) and observations.

The code is designed for easy extension to new variables, different stations, and other plot types.

---
 
### **Project Structure**

```

ukca_model_eval/
├── utils/
│   ├── __init__.py
│   ├── data_io.py         # Model/obs file loading functions
│   ├── processing.py      # Data selection, filtering, grouping, stats
│   ├── plot_utils.py      # Plotting style and utility functions
│   └── units.py           # Unit conversion functions
├── plot_scripts/
│   ├── plot_CO_station_seasonal.py    # Example driver script for CO
│   └── ...                            # Other plotting recipes
├── config.yaml             # Central config for paths, variable names, units
├── data/                   # Model/obs data files (not tracked in git)
├── output/                 # Figures and plots
└── README.md

```

---

### **How It Works**

1. **Edit `config.yaml`**
    - Specify model file paths, variable names, levels, units, output plot location, and plot appearance.
2. **Run a Plot Script**
    - Example:
        
        ```bash
        bash
         
        python plot_scripts/plot_CO_station_seasonal.py
        ```
        
    - Or run the desired plotting script via and IDE.
    - The script loads data, applies selection/averaging, and creates a multi-panel PDF comparing model and obs at various stations.
3. **Modularity**
    - Data loading, processing, plotting, and unit conversion are handled in `utils/` modules.
    - To add a new variable, station set, or plot style, **copy an existing plot script and adjust the config**.

---

### **Adding a New Plot or Variable**

1. **Look at an Existing Driver Script**
    - View the formatting/input handling of  `plot_CO_station_seasonal.py` for reference.
2. **Update `config.yaml`**
    - Change `var_name`, model file paths, desired units, and plotting limits as needed.
3. **If Needed, Add or Update Utility Functions**
    - For new units: add conversions to `utils/units.py`
    - For new plot styles: add functions to `utils/plot_utils.py`
4. **Run Your New Script**
    - Confirm output is as expected and that units and labels are correct.

---

### **Best Practices**

- **Always check units** in your model/obs files.
- **Do not hardcode paths or parameters** in driver scripts; use `config.yaml`.
- **Write docstrings** for any new function you add in `utils/`.
- **Use the modular approach:** If you’re repeating code, factor it out into a utility module.

---

### **Adding Unit Conversion for a New Variable**

1. Edit `utils/units.py` and add a conversion function for your variable (e.g., ppmv to mol/mol).
2. Update the `CONVERSIONS` dictionary in `units.py`.
3. Specify `model_units` and `plot_units` in `config.yaml`.

---

### **Troubleshooting**

- If your script cannot find the `utils` modules, check that:
    - You run scripts from the **project root**.
    - `utils/` has an `__init__.py` file.
    - The project is installed as an editable package (`pip install -e .`).

---

### **Development Installation**

To avoid import errors and enable modular use:

```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
pip install -e .
```

(from the project root directory with a `setup.py` present)

---

### **Example: config.yaml**

```yaml
yaml

model_file: data/path/to/obs_file.nc
obs_file: data/path/to/obs_file.nc
stations_csv: data/gaw_noaa_stations.csv
output_pdf: output/co_comparison_plots.pdf
var_name: co
level: 850
ylim: null          # Let matplotlib autoscale if None
model_units: mol/mol 
plot_units: mol/mol # In other words, no conversion

```

# **Step-by-Step: Adding a New Plot Script (Contour Plot Example)**

---

## **1. Plan What to Modularise**

- **Data loading**: Already handled in `utils/data_io.py`.
- **Climatology/zonal mean calculation**: Could go in `utils/processing.py` if you expect to reuse.
- **Plotting style (labels, colourbars, etc.)**: Centralise in `utils/plot_utils.py`.
- **Unit handling**: If applicable, handled by `utils/units.py`.
- **Config**: Add input/output paths and plotting params to `config.yaml`.

---

## **2. Update `config.yaml`**

Add entries for the new files and plot type:

```yaml
# Input, stored in /data for now
model_file:    data/u‑dr061_O3_tropo_DU.nc
obs_file:      data/u‑dr226_O3_tropo_DU.nc

# For dynamic station co-ords and names loading:
stations_csv:  data/gaw_noaa_stations.csv

# Output
output_pdf:    output/ozone_climatology_bias.pdf

# Variables in each file
var_name:        total_ozone_column   # in model_file
obs_var_name:    ozone_column         # in obs_file

# We’re not plotting at a pressure level, so:
level:           null

# Let matplotlib autoscale
ylim:            null

# Units (no conversion here, it’s DU in both):
model_units:     DU
plot_units:      DU

```

---

## **3. Add/Re-use Utility Functions**

In `utils/processing.py`:

```python
def compute_zonal_mean(ds, var, lon_dim='longitude'):
    return ds[var].mean(dim=lon_dim)

def compute_monthly_climatology(da, time_dim='time', month_dim='month'):
    # `da` is zonal mean DataArray, needs `.groupby()`
    return da.groupby(f'{time_dim}.{month_dim}').mean(time_dim)

```

If you want to generalise for latitude interpolation, add that too.

---

## **4. Add the Plotting Function**

In `utils/plot_utils.py`:

```python
import matplotlib.pyplot as plt

def plot_zonal_climatology_and_bias(
    months, lats, model_clim, obs_clim_interp, output_pdf,
    var_name, units, clim_levels=None, diff_levels=None
):
    diff = model_clim - obs_clim_interp

    # Auto‐compute levels if not provided
    if clim_levels is None:
        vmin = float(model_clim.min().item())
        vmax = float(model_clim.max().item())
        clim_levels = np.linspace(vmin, vmax, 30)
    if diff_levels is None:
        diff_levels = np.arange(-40, 41, 2)

    fig, axs = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    # Panel (a): Climatology
    cf1 = axs[0].contourf(months, lats, model_clim.T,
                          levels=clim_levels, cmap='Reds', extend='both')
    axs[0].contour(months, lats, model_clim.T,
                   levels=clim_levels, colors='white', linewidths=0.6)
    axs[0].set_title(f"Model {var_name} Climatology")
    axs[0].set_ylabel('Latitude (°)')
    axs[0].set_xlabel('Month')
    axs[0].set_xticks(months)
    axs[0].set_xticklabels(
        ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    cbar1 = fig.colorbar(cf1, ax=axs[0], pad=0.02)
    cbar1.set_label(f"({units})")

    # Panel (b): Bias
    cf2 = axs[1].contourf(months, lats, diff.T,
                          levels=diff_levels, cmap='RdBu_r', extend='both')
    axs[1].contour(months, lats, diff.T,
                   levels=diff_levels, colors='white', linewidths=0.6)
    axs[1].set_title(f"Bias (Model–Obs) {var_name}")
    axs[1].set_xlabel('Month')
    axs[1].set_xticks(months)
    axs[1].set_xticklabels(
        ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    cbar2 = fig.colorbar(cf2, ax=axs[1], pad=0.02)
    cbar2.set_label(f"({units})")

    fig.tight_layout()
    fig.savefig(output_pdf)
    plt.close(fig)

```

---

## **5. Create the New Driver Script**

Create `plot_scripts/plot_ozone_zonal_climatology.py`:

```python
import yaml, numpy as np
from utils.data_io import load_model_data
from utils.processing import compute_zonal_mean, compute_monthly_climatology
from utils.plot_utils import plot_zonal_climatology_and_bias

# Load config
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

# Data
mod_ds = load_model_data(cfg['model_file'])
obs_ds = load_model_data(cfg['obs_file'])

# Compute zonal means
mod_zonal = compute_zonal_mean(mod_ds, cfg['var_name'])
obs_zonal = compute_zonal_mean(obs_ds, cfg['obs_var_name'])

# Monthly climatology
mod_clim = compute_monthly_climatology(mod_zonal, month_attr='month')
# Note: obs_ds might have a different month attribute name:
obs_clim = compute_monthly_climatology(obs_zonal, month_attr='t')

# Interpolate obs to mod lat grid
obs_clim_interp = obs_clim.interp(latitude=mod_ds['latitude'])

# Prepare axes
months = np.arange(1, 13)
lats   = mod_ds['latitude']

# Plot
plot_zonal_climatology_and_bias(
    months, lats,
    mod_clim, obs_clim_interp,
    cfg['output_pdf'],
    var_name=cfg['var_name'],
    units=cfg['model_units'],
    clim_levels=None,    # auto
    diff_levels=None     # auto
)

```

---

---

## **Summary Table**

| Step | File/Folder | Example |
| --- | --- | --- |
| Update config | config.yaml | Add input/output paths, var names, units |
| Add processing func | utils/processing.py | `compute_zonal_mean`, `compute_monthly_climatology` |
| Add plot func | utils/plot_utils.py | `plot_ozone_climatology_and_bias` |
| Create driver script | plot_scripts/ | `plot_ozone_zonal_climatology.py` |

---

**This modular workflow should make it easy to add more scripts — just update the config, utility, and plot function, then add a new recipe script.**

### **Additional Tips**

- Make sure you have installed all dependencies.
- Make sure your `config.yaml` is set up correctly with the right file paths and settings.
- Output figures will be saved to the location specified in your config file (e.g., `output/` folder).
- If you encounter module import errors, ensure you have installed the project as an editable package and are running scripts from the project root.

---

### **Installing Project Dependencies (Recommended)**

Before running scripts for the first time:

```bash
bash

pip install -r requirements.txt
# or, if using conda:
conda env create -f environment.yml
conda activate ukca_model_eval

```

---

### **Example Session**

```bash
bash

git clone https://github.com/yourusername/ukca_model_eval.git
cd ukca_model_eval
pip install -e .
python plot_scripts/plot_CO_station_seasonal.py

```
