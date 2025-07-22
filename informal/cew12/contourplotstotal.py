import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

model_ds = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr061_O3_total_DU.nc")
obs_ds   = xr.open_dataset(r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr226_O3_total_DU.nc")

model_ozone = model_ds['total_ozone_column']          
obs_ozone   = obs_ds['TCO'].squeeze('longitude')      

model_zonal = model_ozone.mean(dim='longitude')       
obs_zonal   = obs_ozone                             

model_month = model_ds['time.month']
obs_month   = obs_ds['time.month']

model_clim = model_zonal.groupby(model_month).mean('time')   # (12, nlat_model)
obs_clim   = obs_zonal.groupby(obs_month).mean('time')       # (12, nlat_obs)

lats = model_ds['latitude']
obs_clim_interp = obs_clim.interp(latitude=lats)

bias = model_clim - obs_clim_interp

vmin = np.floor(model_clim.min().item())
vmax = np.ceil(model_clim.max().item())
levels = np.linspace(vmin, vmax, 30)

diff_levels = np.linspace(-150, 200, 30)
  

months = np.arange(1, 13)

# --- Debug checks ---

print("Model clim min/max:", model_clim.min().item(), model_clim.max().item())
print("Obs clim (interp) min/max:", obs_clim_interp.min().item(), obs_clim_interp.max().item())
print("Bias min/max:", bias.min().item(), bias.max().item())
print("Number of NaNs in bias:", np.isnan(bias).sum().item())

fig, axs = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# Panel (a): Model total ozone climatology
cf1 = axs[0].contourf(
    months, lats, model_clim.T,
    levels=levels,
    cmap='Reds',
    extend='both'
)
axs[0].contour(months, lats, model_clim.T, levels=levels, colors='white', linewidths=0.6)
axs[0].set_title('UKESM1.3 Total Ozone O3')
axs[0].set_ylabel('Latitude (°)')
axs[0].set_xlabel('Month')
axs[0].set_xticks(months)
axs[0].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
cbar1 = fig.colorbar(cf1, ax=axs[0], pad=0.02)
cbar1.set_label('(DU)')

# Panel (b): Bias (Model - Obs)
cf2 = axs[1].contourf(
    months, lats, bias.T,
    levels=diff_levels,
    cmap='RdBu_r',
    extend='both'
)
axs[1].contour(months, lats, bias.T, levels=diff_levels, colors='white', linewidths=0.6)
axs[1].set_title('UKESM1.1 and UKESM1.3 Difference')
axs[1].set_xlabel('Month')
axs[1].set_xticks(months)
axs[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
cbar2 = fig.colorbar(cf2, ax=axs[1], pad=0.02)
cbar2.set_label('(DU)')

plt.tight_layout()
plt.show()
