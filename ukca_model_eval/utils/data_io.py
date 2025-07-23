import xarray as xr
import pandas as pd

def load_model_data(path):
    return xr.open_dataset(path)

def load_station_csv(path):
    return pd.read_csv(path)
