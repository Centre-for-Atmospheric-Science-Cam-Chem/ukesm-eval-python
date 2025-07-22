import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

model_ds = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr226_O3_total_DU.nc")
obs_ds   = xr.open_dataset(r"C:\Users\Ifon\OneDrive - King's College London\Documents\UKESM REP\ObsData\ObsData\Boedecker\BSCO_V2.8_mm2.nc")


obs_ozone = obs_ds['TCO'].squeeze('longitude')      
obs_month = obs_ds['time.month']
obs_clim  = obs_ozone.groupby(obs_month).mean('time')   
lats = obs_ds['latitude']

model_ozone = model_ds['total_ozone_column']          
model_zonal = model_ozone.mean(dim='longitude')
model_month = model_ds['time.month']
model_clim  = model_zonal.groupby(model_month).mean('time')
vmin = np.floor(model_clim.min().item())
vmax = np.ceil(model_clim.max().item())
levels = np.linspace(vmin, vmax, 30)

months = np.arange(1, 13)

fig, ax = plt.subplots(figsize=(8, 6))

cf = ax.contourf(
    months, lats, obs_clim.T,
    levels=levels,
    cmap='Reds',
    extend='both'
)
ax.contour(months, lats, obs_clim.T, levels=levels, colors='white', linewidths=0.6)

ax.set_title('Boedecker Total Ozone O3 (Obs)')
ax.set_ylabel('Latitude (°)')
ax.set_xlabel('Month')
ax.set_xticks(months)
ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])

cbar = fig.colorbar(cf, ax=ax, pad=0.02)
cbar.set_label('(DU)')

plt.tight_layout()
plt.show()
