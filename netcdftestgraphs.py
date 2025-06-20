import xarray as xr
import matplotlib.pyplot as plt

# Load dataset
file_path = r"C:\Users\Ifon\Downloads\co_AERmon_UKESM1-0-LL_historical_r1i1p1f2_gn_195001-199912.nc"
ds = xr.open_dataset(file_path)
co = ds['co']

# Make sure data is loaded into memory for faster calculations, otherwise slow processing time as witnessed
co.load()

# 1.Global mean CO over time (mean across lat, lon, not lev apparently - threw error)
global_mean = co.mean(dim=['lat', 'lon'])

plt.figure(figsize=(10, 5))
global_mean.plot()
plt.title("Global Mean CO Concentration Over Time")
plt.xlabel("Time")
plt.ylabel("CO Concentration")
plt.grid(True)
plt.show()

# 2. Vertical profile of CO at the first time step (mean across lat and lon)
vertical_profile = co.isel(time=0).mean(dim=['lat', 'lon'])

plt.figure(figsize=(6, 5))
vertical_profile.plot(marker='o')
plt.title("Vertical Profile of CO Concentration at First Time Step")
plt.xlabel("CO Concentration")
plt.ylabel("Vertical Level (lev)")
plt.grid(True)
plt.show()

# 3.Mean CO concentration averaged over entire time period and vertical levels
mean_spatial = co.mean(dim=['time', 'lev'])

plt.figure(figsize=(10, 5))
mean_spatial.plot()
plt.title("Mean Spatial CO Concentration (averaged over time and vertical levels)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()

#  4. Time series of CO concentration at a single location
# Pick a lat/lon index (e.g., near the middle)
lat_idx = len(co.lat) // 2
lon_idx = len(co.lon) // 2
co_point = co.isel(lat=lat_idx, lon=lon_idx, lev=0)

plt.figure(figsize=(10, 5))
co_point.plot()
plt.title(f"Time Series of CO at lat={float(co.lat[lat_idx])}, lon={float(co.lon[lon_idx])}, surface level")
plt.xlabel("Time")
plt.ylabel("CO Concentration")
plt.grid(True)
plt.show()

