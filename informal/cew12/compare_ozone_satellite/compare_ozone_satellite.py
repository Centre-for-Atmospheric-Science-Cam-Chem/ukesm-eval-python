#!/bin/env python

"""This does some plotting of model output versus observational
data for ozone.

See repo:
https://github.com/Centre-for-Atmospheric-Science-Cam-Chem/ukesm-eval-python

Charlie Wartnaby cew12@cam.ac.uk

"""

import iris
import iris.quickplot
import matplotlib.pyplot as plt
import os


model_output_path = "/gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr226/2005_2014_O3"
path_model_total_O3_DU = os.path.join(model_output_path, "u-dr226_O3_total_DU.nc")
path_model_tropo_O3_DU = os.path.join(model_output_path, "u-dr226_O3_tropo_DU.nc")

bodeker_total_O3_folder = "/gws/nopw/j04/ukca_vol2/Observational_datasets/Other/BodekerScientific_Total_Column_Ozone"
bodeker_total_O3_wildcard = "BSFilledTCO_V3.4.1_*_Monthly.nc"
bodeker_total_O3_wildpath = os.path.join(bodeker_total_O3_folder, bodeker_total_O3_wildcard)

def main():
    print(f"Attempting to open {path_model_total_O3_DU}")
    model_total_O3_dataset = iris.load(path_model_total_O3_DU)
    if len(model_total_O3_dataset) != 1:
        raise ValueError(f"Expected exactly one cube in {path_model_total_O3_DU}")
    model_total_O3_cube = model_total_O3_dataset[0]

    # Find limits/bounds of model time [inclusive_limit, exclusive_limit)
    earliest_model_time_cell = model_total_O3_cube.coord("time").cell(0)
    earliest_model_bounds = earliest_model_time_cell[1] # Seem to get mid value in el 0, bounds here
    earliest_model_time = earliest_model_bounds[0] # tuple of (lower, upper) bounds
    latest_model_time_cell = model_total_O3_cube.coord("time").cell(-1)
    latest_model_bounds = latest_model_time_cell[1]
    latest_model_time = latest_model_bounds[1]

    # Only load observation data that falls within model time bounds
    # (we know observation data is wider in time)
    model_time_constraint = iris.Constraint(time=lambda cell: earliest_model_time <= cell.point < latest_model_time)
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

    # Compare global means over the time we have
    model_total_by_time = global_average_over_time(model_total_O3_cube)
    observation_total_by_time = global_average_over_time(observation_total_O3_cube)
    iris.quickplot.plot(model_total_by_time, label="model")
    iris.quickplot.plot(observation_total_by_time, label="observation")
    plt.title("Model vs BodekerScientific_Total_Column_Ozone, global mean")
    plt.legend()
    plt.show()

    pass


def global_average_over_time(cube):

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
