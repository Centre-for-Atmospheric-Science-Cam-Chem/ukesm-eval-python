#!/bin/env python

"""This does some plotting of model output versus observational
data for ozone.

See repo:
https://github.com/Centre-for-Atmospheric-Science-Cam-Chem/ukesm-eval-python

Charlie Wartnaby cew12@cam.ac.uk

"""

import datetime
import iris
import iris.quickplot
import matplotlib.pyplot as plt
import os


model_output_root = "/gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output"
path_model_total_O3_DU = os.path.join(model_output_root, "u-dr226_O3_total_DU.nc")
models_total_O3_DU = {"UKESM-1.1": "u-dr061/2005_2014_O3/u-dr061_O3_total_DU.nc",
                      "UKESM-1.3": "u-dr226/2005_2014_O3/u-dr226_O3_total_DU.nc" }

bodeker_total_O3_folder = "/gws/nopw/j04/ukca_vol2/Observational_datasets/Other/BodekerScientific_Total_Column_Ozone"
bodeker_total_O3_wildcard = "BSFilledTCO_V3.4.1_*_Monthly.nc"
bodeker_total_O3_wildpath = os.path.join(bodeker_total_O3_folder, bodeker_total_O3_wildcard)

def main():
    model_total_O3_cube = {}
    earliest_overall_time = None
    latest_overall_time   = None
    for model, subpath in models_total_O3_DU.items():
        model_cube = load_model_O3_cube(subpath)
        model_total_O3_cube[model] = model_cube

        # Get time bounds for model cubes loaded so far    
        earliest_model_time_cell = model_cube.coord("time").cell(0)
        earliest_model_bounds = earliest_model_time_cell[1] # Seem to get mid value in el 0, bounds here
        earliest_model_time = earliest_model_bounds[0] # tuple of (lower, upper) bounds
        latest_model_time_cell = model_cube.coord("time").cell(-1)
        latest_model_bounds = latest_model_time_cell[1]
        latest_model_time = latest_model_bounds[1]
        if not earliest_overall_time or earliest_model_time < earliest_overall_time:
            earliest_overall_time = earliest_model_time
        if not latest_overall_time or latest_model_time > latest_overall_time:
            latest_overall_time = latest_model_time

    # Only load observation data that falls within model time bounds
    # (we know observation data is wider in time)
    model_time_constraint = iris.Constraint(time=lambda cell: earliest_overall_time <= cell.point < latest_overall_time)
    observation_total_O3_dataset = iris.load(bodeker_total_O3_wildpath, model_time_constraint)

    # End up with series of n cubes uncertainty (could be good for error bars)
    # then n for data, so need to coalesce. This is a bit of a nasty hack because
    # I'm using prior knowledge of that layout and depending on it
    num_ozone_cubes = int(len(observation_total_O3_dataset) / 2)
    # Iris seems unnecessarily strict but won't merge/concat cubes with different
    # 'created' timestamp strings, so getting rid of those:
    for cube in observation_total_O3_dataset:
        del cube.attributes["created"]
    observation_total_O3_cube = observation_total_O3_dataset[num_ozone_cubes : ].concatenate_cube()
    observation_sigma_cube    = observation_total_O3_dataset[ : num_ozone_cubes].concatenate_cube()

    latitude_ranges = [(-90,  90),
                       (-90, -60),
                       (-60,   0),
                       (  0,  60),
                       ( 60,  90)]

    y_range=(200,475)
    for lat_min, lat_max in latitude_ranges:
        # Compare global means over the time we have
        # Observations first
        observation_total_by_time = global_average_over_time(observation_total_O3_cube, lat_min, lat_max)
        iris.quickplot.plot(observation_total_by_time, label="Bodeker observation", color="blue")

        # Error bars...
        # Iris coord points for time give tuples, el[0]=value, el[1]=bounds...
        iris_time_points = observation_total_by_time.coord("time").cells()
        standard_time_points = [datetime.datetime(point[0].year, point[0].month, point[0].day) for point in iris_time_points]
        sigma_average_over_time = global_average_over_time(observation_sigma_cube, lat_min, lat_max)
        plt.errorbar(standard_time_points, observation_total_by_time.data, yerr=sigma_average_over_time.data)

        for model, model_cube in model_total_O3_cube.items():
            model_total_by_time = global_average_over_time(model_cube, lat_min, lat_max)
            iris.quickplot.plot(model_total_by_time, label=model,
                                color="red" if model == "UKESM-1.1" else "green")
        plt.title(f"Model vs BodekerScientific_Total_Column_Ozone, latitude: [{lat_min}, {lat_max}] deg")
        plt.legend()
        plt.ylim(y_range)
        # Save before plot or get blank
        plt.savefig(f"model_vs_bodeker_total_ozone_lat_{lat_min}_{lat_max}.png")
        plt.show()

    pass

def load_model_O3_cube(subpath):
    path = os.path.join(model_output_root, subpath)
    print(f"Attempting to open {path}")
    model_total_O3_dataset = iris.load(path)
    if len(model_total_O3_dataset) != 1:
        raise ValueError(f"Expected exactly one cube in {path}")
    model_total_O3_cube = model_total_O3_dataset[0]
    return model_total_O3_cube


def global_average_over_time(whole_cube, lat_min, lat_max):

    model_lat_constraint = iris.Constraint(latitude=lambda cell: lat_min <= cell.point <= lat_max)
    cube = whole_cube.extract(model_lat_constraint)

    # Weighting by cell areas so that small polar cells don't have undue
    # influence on average
    # Need bounds to do area weights
    if not cube.coord('latitude').has_bounds():
        cube.coord('latitude').guess_bounds()
    if not cube.coord('longitude').has_bounds():
        cube.coord('longitude').guess_bounds()
    collapse_coords = ['latitude', 'longitude']
    cell_areas_m2 = iris.analysis.cartography.area_weights(cube)

    collapsed = cube.collapsed(collapse_coords,
                                iris.analysis.MEAN,
                                weights=cell_areas_m2)
    return collapsed


if __name__ == "__main__":
    main()
