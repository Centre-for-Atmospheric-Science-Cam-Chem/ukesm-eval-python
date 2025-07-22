import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

model_path = r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr226_O3_tropo_DU.nc"
obs_path   = r"C:\Users\Aliya-LOCAL\Code\ukca_evaluation\data\u-dr061_O3_tropo_DU.nc"

model_var = 'troposphere_only_ozone_column'
obs_var   = 'troposphere_only_ozone_column'
model_lat  = 'latitude'
obs_lat    = 'latitude'        
model_time = 'time'
obs_time   = 'time'               

model_ds = xr.open_dataset(model_path)
obs_ds   = xr.open_dataset(obs_path)

model_ozone = model_ds[model_var]
obs_ozone   = obs_ds[obs_var]

model_zonal = model_ozone.mean(dim='longitude')
obs_zonal   = obs_ozone.mean(dim='longitude')

model_month = model_ds[model_time + '.month']
obs_month   = obs_ds[obs_time + '.month']

model_clim = model_zonal.groupby(model_month).mean(model_time)
obs_clim   = obs_zonal.groupby(obs_month).mean(obs_time)

if not np.allclose(model_ds[model_lat], obs_ds[obs_lat]):
    obs_clim = obs_clim.interp({obs_lat: model_ds[model_lat]})


diff = model_clim - obs_clim

print("Model clim shape:", model_clim.shape)
print("Obs clim shape:", obs_clim.shape)
print("Diff shape:", diff.shape)
print("Any NaN in model_clim?", np.isnan(model_clim).any().item())
print("Any NaN in obs_clim?", np.isnan(obs_clim).any().item())
print("Any NaN in diff?", np.isnan(diff).any().item())
print("Min/max of diff:", np.nanmin(diff), np.nanmax(diff))


vmin = np.floor(model_clim.min().item())
vmax = np.ceil(model_clim.max().item())
levels = np.linspace(vmin, vmax, 30)

pad = 0.05
diff_min = diff.min().item()   
diff_max = diff.max().item()   
diff_levels = np.linspace(diff_min-pad, diff_max+pad, 31)

months = np.arange(1, 13)
lats   = model_ds[model_lat]

fig, axs = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# Panel (a): Model
cf1 = axs[0].contourf(
    months, lats, model_clim.T,
    levels=levels, cmap='Reds', extend='both'
)
axs[0].contour(months, lats, model_clim.T, levels=levels, colors='white', linewidths=0.6)
axs[0].set_title('Model Total Ozone O3')
axs[0].set_ylabel('Latitude (°)')
axs[0].set_xlabel('Month')
axs[0].set_xticks(months)
axs[0].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
cbar1 = fig.colorbar(cf1, ax=axs[0], pad=0.02)
cbar1.set_label('(DU)')

# Panel (b): 1.3 - 1.1
cf2 = axs[1].contourf(
    months, lats, diff.T,
    levels=diff_levels, cmap='RdBu_r', extend='both'
)
axs[1].contour(months, lats, diff.T, levels=diff_levels, colors='white', linewidths=0.6)
axs[1].set_title('UKESM1.1 and UKESM1.3 Difference - Tropospheric Ozone')
axs[1].set_xlabel('Month')
axs[1].set_xticks(months)
axs[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
cbar2 = fig.colorbar(cf2, ax=axs[1], pad=0.02)
cbar2.set_label('(DU)')

plt.tight_layout()
plt.show()
