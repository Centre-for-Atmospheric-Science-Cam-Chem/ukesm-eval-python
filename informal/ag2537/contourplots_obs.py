import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

model_ds = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr061_O3_tropo_DU.nc")
obs_ds   = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\OMI_MLS_ozone.nc")

# Get variables and compute zonal means
obs_ozone = obs_ds['ozone_column']
obs_zonal = obs_ozone.mean(dim='longitude')

obs_month = obs_ds['t.month']
obs_clim  = obs_zonal.groupby(obs_month).mean('t')  # shape: (12, nlat_obs)

# interpolate obs climatology to model latitude grid for direct comparison
lats = model_ds['latitude']
obs_clim_interp = obs_clim.interp(latitude=lats)

# Use model's climatology range for consistent colourbar and comparison
# If you want the colourbar to be identical to the model plot, use the same vmin/vmax/levels:
model_ozone = model_ds['troposphere_only_ozone_column']
model_zonal = model_ozone.mean(dim='longitude')
model_month = model_ds['time.month']
model_clim = model_zonal.groupby(model_month).mean('time')

vmin = np.floor(model_clim.min().item())
vmax = np.ceil(model_clim.max().item())
levels = np.linspace(vmin, vmax, 30)

print(f"Using color levels from {vmin} to {vmax}")

months = np.arange(1, 13)

# plot single panel
fig, ax = plt.subplots(figsize=(8, 5))
cf = ax.contourf(
    months, lats, obs_clim_interp.T,
    levels=levels,
    cmap='Reds', 
    extend='both'
)
ax.contour(months, lats, obs_clim_interp.T, levels=levels, colors='white', linewidths=0.6)

ax.set_title('OMI/MLS Tropospheric Ozone (Obs)')
ax.set_ylabel('Latitude (°)')
ax.set_xlabel('Month')
ax.set_xticks(months)
ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])

cbar = fig.colorbar(cf, ax=ax, pad=0.02)
cbar.set_label('(DU)')

plt.tight_layout()
plt.show()

