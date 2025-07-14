#!/bin/env python

"""This does some plotting of model output versus observational
data for ozone.

See repo:
https://github.com/Centre-for-Atmospheric-Science-Cam-Chem/ukesm-eval-python

Charlie Wartnaby cew12@cam.ac.uk

"""

import glob
import iris
import os


model_output_path = "/gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr226/2005_2014_O3"
path_model_total_O3_DU = os.path.join(model_output_path, "u-dr226_O3_total_DU.nc")
path_model_tropo_O3_DU = os.path.join(model_output_path, "u-dr226_O3_tropo_DU.nc")

bodeker_total_O3_folder = "/gws/nopw/j04/ukca_vol2/Observational_datasets/Other/BodekerScientific_Total_Column_Ozone"
bodeker_total_O3_wildcard = "BSFilledTCO_V3.4.1_*_Monthly.nc"
bodeker_total_O3_wildpath = os.path.join(bodeker_total_O3_folder, bodeker_total_O3_wildcard)

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

# TODO end up with series of 10 cubes uncertainty (could be good for error bars)
# then 10 for data, so need to coalesce

pass

