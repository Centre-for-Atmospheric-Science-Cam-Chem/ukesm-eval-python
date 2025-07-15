module purge
module load jaspy
./ozone_to_dobson_units.py -i /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr061/2005_2014_O3/u-dr061_upm.nc -o /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr061/2005_2014_O3/u-dr061_O3_total_DU.nc
./ozone_to_dobson_units.py -t -i /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr061/2005_2014_O3/u-dr061_upm.nc -o /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr061/2005_2014_O3/u-dr061_O3_tropo_DU.nc
./ozone_to_dobson_units.py -i /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr226/2005_2014_O3/u-dr226_upm.nc -o /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr061/2005_2014_O3/u-dr226_O3_total_DU.nc
./ozone_to_dobson_units.py -t -i /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr226/2005_2014_O3/u-dr226_upm.nc -o /gws/nopw/j04/ukca_vol2/2025-07-ukesm-eval/model_output/u-dr061/2005_2014_O3/u-dr226_O3_tropo_DU.nc
