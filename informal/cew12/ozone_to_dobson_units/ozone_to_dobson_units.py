#!/bin/env python

"""Utility to convert ozone units in NetCDF file to allow comparison with another
file. Specifically mass mixing ratio to Dobson Units, intended it to be more
general but not as yet.

Created as part of ICCS 2025 summer school hackathon so modified a bit from:
https://github.com/Centre-for-Atmospheric-Science-Cam-Chem/2025-iccs-hackathon-ukesm
(which may get deleted before long).

Charlie Wartnaby cew12@cam.ac.uk

WARNING: Sophie Turner pointed out the model already has this STASH item:
   50219 Ozone column in Dobson Units
   So summing that would have been a lot simpler. This seems to work fine though.
"""

import argparse
import iris


def main(args):
    """Main entry point"""

    print(f"Attempting to load file: {args.input_file}")
    cubelist = iris.load(args.input_file)

    air_mass_cube_kg_cell = get_cube_by_longname_fragment(cubelist, "AIR MASS DIAGNOSTIC (WHOLE")

    O3_MMR_cube_proportion = get_cube_by_longname_fragment(cubelist, "O3 MASS MIXING RATIO")
        
    # Build up version of data in new units. Doesn't seem to work using
    # arithmetic operators directly with cube objects, so going for underlying
    # data arrays instead. Starting with an alias (so will trash original)
    O3_mass_cube_kg_cell = O3_MMR_cube_proportion

    if args.tropo_only:
        # Mask out stratosphere as we have been asked to do so
        tropo_mask_cube = get_cube_by_longname_fragment(cubelist, "TROPOSPHERIC MASK")
        O3_mass_cube_kg_cell.data *= tropo_mask_cube.data

    # Convert from mass mixing ratio (unitless) to mass per model cell (kg)
    O3_mass_cube_kg_cell.data *= air_mass_cube_kg_cell.data
    
    # Sum all of the model cells vertically in each longitude/latitude patch
    collapse_coords=['atmosphere_hybrid_height_coordinate']
    O3_mass_cube_kg_column = O3_mass_cube_kg_cell.collapsed(collapse_coords,
                                                            iris.analysis.SUM)
    
    # Convert from total mass in cell (which may be of order 100km * 100km)
    # to mass per unit area
    cell_areas_m2 = iris.analysis.cartography.area_weights(O3_mass_cube_kg_column)
    O3_mass_cube_kg_m2 = O3_mass_cube_kg_column / cell_areas_m2

    # Convert from mass to a volume at standard temperature and pressure.
    # Now on the one hand https://en.wikipedia.org/wiki/Dobson_unit links to:
    # https://en.wikipedia.org/wiki/Standard_temperature_and_pressure
    # "Since 1982, STP has been defined as a temperature of 273.15 K 
    #  (0 °C, 32 °F) and an absolute pressure of exactly 1 bar (100 kPa, 10^5 Pa)."
    # However, further down the page, and in other places including this NERC
    # definition, 1 atm == 101.325 kPa is used:
    # https://vocab.nerc.ac.uk/collection/P07/current/CFSN0619/
    # ""stp" means standard temperature (0 degC) and pressure (101325 Pa)"
    standard_T_K = 273.15
    standard_p_Pa = 101325.0
    molar_gas_const_J_K_mol = 8.314
    molar_mass_O3_g_mol = 47.997 # From https://en.wikipedia.org/wiki/Ozone
    molar_mass_O3_kg_mol = molar_mass_O3_g_mol * 1e-3

    # pV = nRT           where n = num mols
    #  n = m / M         where m = atual mass, M = relative molar mass
    # --> V = ((m/M) RT) / p   
    num_mols_column_per_m2 = O3_mass_cube_kg_m2 / molar_mass_O3_kg_mol
    volume_column_m3_per_m2 = ((num_mols_column_per_m2 * molar_gas_const_J_K_mol * standard_T_K)
                                  / standard_p_Pa)
    
    # So we have the 'volume per unit area' which has dimensions of length,
    # i.e. the equivalent thickness of pure O3 in the column compressed to standard T & p
    # Dobson Units are just that expressed in units of 10 um (or 1e5 metres).
    # We should get values of about 300 (i.e. 3 mm or 0.003 m) according to:
    # https://en.wikipedia.org/wiki/Dobson_unit
    volume_column_DU = volume_column_m3_per_m2 * 1e5
    volume_column_DU.units = "DU"
    volume_column_DU.long_name = "Troposphere-only ozone column" if args.tropo_only else "Total ozone column"
    

    print(f"Writing output to {args.output_file}")
    iris.save(volume_column_DU, args.output_file)

    print("All done")


def get_cube_by_longname_fragment(cubelist, name_fragment):
    """Find the one and only cube in the list whose long name contains the provided
    fragment, else error"""

    matching_cubes = []
    for cube in cubelist:
        if cube.long_name and name_fragment in cube.long_name:
            matching_cubes.append(cube)
    if len(matching_cubes) == 0:
        raise ValueError(f"No cubes match '{name_fragment}'")
    elif len(matching_cubes) > 1:
        matching_names = [cube.long_name for cube in matching_cubes]
        raise ValueError(f"All of these cubes match '{name_fragment}': {matching_names}")
    else:
        return matching_cubes[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog="ozone_to_dobson_units.py",
                    description="Converts O3 mass mixing ratio to facilitate comparisons, optionally tropo only")
    
    parser.add_argument("-i", "--input-file",
                        required=True,
                        help="Input file to process")
    parser.add_argument("-o", "--output-file",
                        required=True,
                        help="Transformed output file")
    parser.add_argument("-t", "--tropo-only",
                        action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Apply troposphere-only mask")
    # No other units yet implemented but:
    parser.add_argument("-f", "--format",
                        default="DU",
                        help="Units to convert to")
    
    args = parser.parse_args()

    main(args)
