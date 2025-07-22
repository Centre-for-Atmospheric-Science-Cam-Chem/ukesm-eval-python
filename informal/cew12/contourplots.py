import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

model_ds = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr061_O3_tropo_DU.nc")
obs_ds   = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr226_O3_tropo_DU.nc")

model_ozone = model_ds['total_ozone_column']
obs_ozone   = obs_ds['ozone_column']

model_zonal = model_ozone.mean(dim='longitude')
obs_zonal   = obs_ozone.mean(dim='longitude')

model_month = model_ds['time.month']
obs_month   = obs_ds['t.month']

model_clim = model_zonal.groupby(model_month).mean('time')  
obs_clim   = obs_zonal.groupby(obs_month).mean('t')         

obs_clim_interp = obs_clim.interp(latitude=model_ds['latitude'])

diff = model_clim - obs_clim_interp

# Compute levels for panel (a)
vmin = np.floor(model_clim.min().item())
vmax = np.ceil(model_clim.max().item())
levels = np.linspace(vmin, vmax, 30)

print(f"Clim levels from {vmin} to {vmax} every 10 DU: {levels}")

# For panel (b)
diff_levels = np.arange(-40, 41, 2)      # every 2 DU

months = np.arange(1, 13)
lats   = model_ds['latitude']

# Draw the two-panel figure
fig, axs = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# Panel (a): Model
cf1 = axs[0].contourf(
    months, lats, model_clim.T,
    levels=levels,
    cmap='Reds',
    extend='both'
)
# white contour lines
axs[0].contour(months, lats, model_clim.T, levels=levels, colors='white', linewidths=0.6)

axs[0].set_title('UKESM1.1 Total Ozone O3')
axs[0].set_ylabel('Latitude (°)')
axs[0].set_xlabel('Month')
axs[0].set_xticks(months)
axs[0].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
cbar1 = fig.colorbar(cf1, ax=axs[0], pad=0.02)
cbar1.set_label('(DU)')

# Panel (b): Model – Obs difference
cf2 = axs[1].contourf(
    months, lats, diff.T,
    levels=diff_levels,
    cmap='RdBu_r',
    extend='both'
)
axs[1].contour(months, lats, diff.T, levels=diff_levels, colors='white', linewidths=0.6)

axs[1].set_title('Bias (Model - Observation)')
axs[1].set_xlabel('Month')
axs[1].set_xticks(months)
axs[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
cbar2 = fig.colorbar(cf2, ax=axs[1], pad=0.02)
cbar2.set_label('(DU)')

plt.tight_layout()
plt.show()






