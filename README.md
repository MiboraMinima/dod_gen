# DOD generator

This scripts automatize the creation of DODs. You don't need to add exception
for temporal discontinuities in data, the script handles it.

It takes as input a folder containing DEMs (`PlaceName_YYYYMM_DEM.tif`) in
subdirs named by place :

```
.
├── Katlahraun
│   ├── Katlahraun_201505_DEM.tif
│   ├── Katlahraun_201605_DEM.tif
│   ├── Katlahraun_201708_DEM.tif
│   ├── (...)
├── Kerling
│   ├── Kerling_201505_DEM.tif
│   ├── Kerling_201605_DEM.tif
│   ├── (...)
(...)
```

A mask is used to get only the area of interest.

The results are:
- Two cliped DEM under a given directory
- The generated DOD under a given directory

Each time, the directory is automatically generated if it has not been created
before, resulting in such directory pattern:

1. For the clipped DEM:

```
RACINE
├── Place1
│   ├── Place1_YYYYMMDD_Mask.ext
│   ├── Place1_YYYYMMDD_Mask.tif
│   ├── Place1_YYYYMMDD_Mask.tif
│   ├── (...)
├── Place2
│   ├── Place2_YYYYMMDD_Mask.tif
│   ├── Place2_YYYYMMDD_Mask.tif
│   ├── Place2_YYYYMMDD_Mask.tif
│   ├── (...)
├── PlaceX
│   ├── PlaceX_YYYYMMDD_Mask.tif
│   ├── (...)
```

2. For the DODs:

```
RACINE
├── Place1
│   ├── Place1_YYYY_YYYY_DOD.ext
│   ├── Place1_YYYY_YYYY_DOD.tif
│   ├── Place1_YYYY_YYYY_DOD.tif
│   ├── (...)
├── Place2
│   ├── Place2_YYYY_YYYY_DOD.tif
│   ├── Place2_YYYY_YYYY_DOD.tif
│   ├── Place2_YYYY_YYYY_DOD.tif
│   ├── (...)
├── PlaceX
│   ├── PlaceX_YYYY_YYYY_DOD.tif
│   ├── (...)

```

If you already have files, you have to delete them before generating the DOD.
**The QGIS functions prevent overwriting**.

