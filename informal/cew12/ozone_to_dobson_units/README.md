# 2025-iccs-hackathon-ukesm
For hackathon effort 11 Jul 2025 ICCS summer school, relevant to UKESM evaluation next week

## Overall aim

The UK Met Office earth system model (UKESM) will be one of many
models used to predict future Earth behaviour for the IPCC
Assessment Report 7.

There is a hackathon at Reading to evaluate the UKESM 1.3 output
to discuss its output quality currently and what variant should
be taken forward for this purpose. To decide that, we need to compare
the model predictions against past observations of the real
atmosphere.

Today we have some model output from UKESM 1.3 (model run
`u-dp226`) in NetCDF format, gridded as a function of
(time, latitude, longitude, model level). This data is supplied
separately as it is too large for GitHub.

We also have some observational datasets which some more detailed
notes about will be added below.

By the end of the ICCS hackathon, we only got to the point of a script
that would convert ozone mass mixing ratio to Dobson Units.



## Observational datasets

### BodekerScientific_Vertical_Ozone

From `ncdump -h` this dataset has:
```
dimensions:
        time = 456 ;
        latitude = 36 ;
        level = 70 ;
...
o3_mean:units = "mole mole^-1" ;
```
The UKESM output is in _mass_ mixing ratio, so a conversion is neeeded to
_molar_ mixing ratio to compare to this.
Also the levels will not be the same -- we could average or sum over levels
initially to get something comparable.

### BodekerScientific_Total_Column_Ozone

From `ncdump -h` this has:
```
dimensions:
        latitude = 180 ;
        longitude = 288 ;
        time = UNLIMITED ; // (12 currently)
...
    tco:units = "DU" ;
    tco:long_name = "Total column ozone" ;
```
DU means Dobson Units, an absolute measure of the total quantity in the
column per unit area (from ground level to space).

### OMI_MLS_Tropospheric_Ozone_Column

This has: 
```
dimensions:
        longitude = 288 ;
        latitude = 120 ;
        t = 183 ;
    ...
    ozone_column:units = "DU" ;
```
So again we will have to convert from mass mixing ratio in the model
output to compare with this dataset.
