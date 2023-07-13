"""
# ////////////////////////////
# DOD PROCESSING ONE BY ONE //
# ////////////////////////////

This scripts automatize the creation of a DOD.

It takes as input a folder containing DEM (PlaceName_YYYYMM_DEM.tif) in subdirs named by place :
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

A mask is used to get only the area of interest.

The results are:
- two clip DEM under a given directory
- The generated DOD under a given directory

Each time the directory is automatically generated if it has not been created before, resulting in such directory pattern :
1. For the clipped DEM:

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

2. For the DODs:

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

"""

from qgis.PyQt.QtCore import (QCoreApplication, QVariant)
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import *
import processing

import time
import os
import re

# ========================================
# PARAMETERS
# ========================================

# INPUT
## Dossier des MNE
dir_mne = 'C:/Users/antoi/Documents/Savoir/Stages/M2_ISLANDE/TRAITEMENTS/MORPHO/DIFFERENTIEL/SRC/RAS/DEM'
## Dossier des masques
dir_mask = "C:/Users/antoi/Documents/Savoir/Stages/M2_ISLANDE/TRAITEMENTS/MORPHO/DIFFERENTIEL/RES/SHP/MASK_CORDON"
# Définir les années qui vont être utilisées pour créer les DODs (on fera current_year - last_year)
current_year = "2022"
last_year = "2021"

# OUTPUT
## Dossier de destination des MNE coupés par les masques
dir_mne_cut = "C:/Users/antoi/Documents/Savoir/Stages/M2_ISLANDE/TRAITEMENTS/MORPHO/DIFFERENTIEL/RES/RAS/MNE_CUT"
## Dossier de destination des DODs
dir_dod = "C:/Users/antoi/Documents/Savoir/Stages/M2_ISLANDE/TRAITEMENTS/MORPHO/DIFFERENTIEL/RES/RAS/DOD"

# ========================================
# PROCESS
# ========================================

# Initialize time counter
start_time = time.time()

# Find DEM 
mne_list = []
for root, dirs, files in os.walk(dir_mne):
    for subdir in dirs:
        for file in os.listdir(f"{dir_mne}/{subdir}"):
            if (re.search(rf'{last_year}', file) and re.search(r'.tif$', file)):
                mne_last = f"{dir_mne}/{subdir}/{file}"
                mne_list.append(mne_last)
            elif (re.search(rf'{current_year}', file) and re.search(r'.tif$', file)):
                mne_current = f"{dir_mne}/{subdir}/{file}"
                mne_list.append(mne_current)

# Dictionnaire pour les sites
files_by_place = {}
# Loop through all the files in the directory
for filename in mne_list:
    # Match the file name against the pattern
    match = re.match(r".*(?=\/)\/(.*(?=_\d))", filename)
    if match:
        # Get the place from the matched group
        place = match.group(1)
        # Add the file to the dictionary under the place key
        files_by_place.setdefault(place, []).append(filename)

# Print the files grouped by place
for place, files in files_by_place.items():
    print(f"Files in {place}:")
    for filename in files:
        print(filename)
        
for place, files in files_by_place.items():
    print(f"{place}")
    
    # Trouver les années
    for file in files:
        if re.search(rf'{last_year}', file):
            match_last = file
        elif re.search(rf'{current_year}', file):
            match_current = file
    
    # Définir le nom de la couche
    name_last = re.search(r'.*(?=\/)\/(.*(?=\.))', match_last).group(1)
    name_current = re.search(r'.*(?=\/)\/(.*(?=\.))', match_current).group(1)
    
    # Convertir en couche Qgis
    mne_last = QgsRasterLayer(f"{match_last}", f'{name_last}')
    mne_current = QgsRasterLayer(f"{match_current}", f'{name_current}')
    
    # Trouver le fichier masque correspondant au lieu courant
    for root, dirs, files in os.walk(dir_mask):
        for subdir in dirs:
            # Si le sous-dossier correspondant au lieu courant
            if subdir == place:
                subdir_path = f"{dir_mask}/{subdir}"
                for file in os.listdir(subdir_path):
                    # trouver le fichier
                    if re.search(rf'{place}.*\.shp', file):
                        mask = QgsVectorLayer(f"{subdir_path}/{file}", f"{place}_{last_year}_{current_year}_mask")
                            
                        # Mask last
                        mne_last_path = f"{dir_mne_cut}/{place}/{name_last}_Mask.tif"
                        print("Clip last mne")
                        params = {
                            'INPUT':match_last,
                            'MASK':mask,
                            'SOURCE_CRS':None,
                            'TARGET_CRS':None,
                            'TARGET_EXTENT':None,
                            'NODATA':None,
                            'ALPHA_BAND':False,
                            'CROP_TO_CUTLINE':True,
                            'KEEP_RESOLUTION':False,
                            'SET_RESOLUTION':False,
                            'X_RESOLUTION':None,
                            'Y_RESOLUTION':None,
                            'MULTITHREADING':False,
                            'OPTIONS':'',
                            'DATA_TYPE':0,
                            'EXTRA':'',
                            'OUTPUT':mne_last_path
                        }
                        
                        processing.run("gdal:cliprasterbymasklayer", params)
                        
                        # Mask current
                        mne_current_path = f"{dir_mne_cut}/{place}/{name_current}_Mask.tif"
                        print("Clip current mne")
                        params = {
                            'INPUT':match_current,
                            'MASK':mask,
                            'SOURCE_CRS':None,
                            'TARGET_CRS':None,
                            'TARGET_EXTENT':None,
                            'NODATA':None,
                            'ALPHA_BAND':False,
                            'CROP_TO_CUTLINE':True,
                            'KEEP_RESOLUTION':False,
                            'SET_RESOLUTION':False,
                            'X_RESOLUTION':None,
                            'Y_RESOLUTION':None,
                            'MULTITHREADING':False,
                            'OPTIONS':'',
                            'DATA_TYPE':0,
                            'EXTRA':'',
                            'OUTPUT':mne_current_path
                        }
                        
                        processing.run("gdal:cliprasterbymasklayer", params)
                        
                        # Définir le nom du fichier en sorti
                        mne_diff_name = f'{dir_dod}/{place}/{place}_{last_year}_{current_year}_DOD.tif'
                        lyr1 = QgsRasterLayer(mne_last_path)
                        lyr2 = QgsRasterLayer(mne_current_path)
                        
                        # Paramètre de la calculatrice raster
                        entries = []
                        ras = QgsRasterCalculatorEntry()
                        ras.ref = 'mne_last@1'
                        ras.raster = lyr1
                        ras.bandNumber = 1
                        entries.append(ras)
                        
                        ras_2 = QgsRasterCalculatorEntry()
                        ras_2.ref = 'mne_current@1'
                        ras_2.raster = lyr2
                        ras_2.bandNumber = 1
                        entries.append(ras_2)
                        
                        # Process
                        print("DOD processing")
                        calc = QgsRasterCalculator(
                            '(mne_current@1 - mne_last@1)', # Expression
                            mne_diff_name , # Output
                            'GTiff', # Format
                            lyr2.extent(), lyr2.width(), lyr2.height(), # Extents
                            entries # Les rasters en entrées
                        )
                        calc.processCalculation()
                        
                        print("Done")
                    
                    else:
                        continue
                    
end_time = time.time()
execution_time = end_time - start_time

print(f"Execution time: {execution_time} seconds")
