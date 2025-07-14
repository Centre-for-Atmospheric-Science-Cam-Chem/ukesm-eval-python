echo "Excuse the hard-coded paths here"
./ozone_to_dobson_units.py -i /mnt/c/data/hackathon/model_output/u-dr226/2005_2014_O3/u-dr226_upm.nc -o u-dr226_O3_total_DU.nc
./ozone_to_dobson_units.py -t -i /mnt/c/data/hackathon/model_output/u-dr226/2005_2014_O3/u-dr226_upm.nc -o u-dr226_O3_tropo_DU.nc
