def get_nearest_point(da, lat, lon):
    return da.sel(lat=lat, lon=lon, method="nearest")

def filter_stations(stations, lat_min, lat_max, lon_min, lon_max):
    return stations[
        stations.Latitude.between(lat_min, lat_max) &
        stations.Longitude.between(lon_min, lon_max)
    ]

def mean_bias_error(obs, mod):
    return 100 * ((mod - obs).mean() / obs.mean()).item()

def correlation(obs, mod):
    import numpy as np
    return np.corrcoef(obs, mod)[0, 1]
