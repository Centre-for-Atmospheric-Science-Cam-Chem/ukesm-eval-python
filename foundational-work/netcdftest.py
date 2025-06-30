import xarray as xr
import matplotlib.pyplot as plt

# Load the NetCDF file
file_path = r"C:\Users\Ifon\Downloads\co_AERmon_UKESM1-0-LL_historical_r1i1p1f2_gn_195001-199912.nc"
ds = xr.open_dataset(file_path)

# Print dataset summary to check dimensions
print(ds)

# Check if 'co' is present
if 'co' in ds.variables:
    co = ds['co']
    print("CO variable dims:", co.dims)

    # Handle 4D data: (time, lev, lat, lon)
    if {'time', 'lev', 'lat', 'lon'}.issubset(co.dims):
        # Extract surface level (lev=0) at first time
        plot_data = co.isel(time=0, lev=0)
    elif {'time', 'lat', 'lon'}.issubset(co.dims):
        # 3D case: time, lat, lon
        plot_data = co.isel(time=0)
    else:
        raise ValueError("Unhandled dimensions for 'co' variable:", co.dims)

    # Ensure plot_data is 2D before plotting
    if len(plot_data.dims) == 2:
        plot_data.plot(cmap='viridis')
        plt.title('CO Concentration at Surface Level, First Timestep')
        plt.show()
    else:
        print("plot_data is not 2D. Its dims are:", plot_data.dims)

else:
    print("No variable named 'co'. Available variables:", list(ds.variables))
