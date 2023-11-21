"""
# TODO: Add header
# TODO: All in english
"""

from qgis.PyQt.QtCore import (QCoreApplication, QVariant)
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import *
import processing

import time
import os
import re

# ==============================================================================
# PARAMETERS
# ==============================================================================

# ----------------------------------------
# INPUT
# ----------------------------------------
# Dossier du project
dir_proj = "path"

# Dossier des MNE
dir_mne = f"{dir_proj}/SRC/RAS/DEM"

# Dossier des masques
dir_mask = f"{dir_proj}/RES/SHP/MASK_CORDON"

# Définir la gamme d'année
begin_year = 2015
end_year = 2023

# Compute gap if temporal discontinuity
gap = True  # True or False

# ----------------------------------------
# OUTPUT
# ----------------------------------------
# Dossier de destination des MNE coupés par les masques
dir_mne_cut = f"{dir_proj}/RES/RAS/MNE_CUT"

# Dossier de destination des DODs
dir_dod = f"{dir_proj}/RES/RAS/DOD"

# ==============================================================================
# PROCESS
# ==============================================================================

# Initialize time counter
start_time = time.time()

# Find DEM
for year in range(begin_year, end_year):
    current_year = year + 1
    last_year = year

    print(f"\nProcessing years: {last_year} and {current_year}")

    # Find files for last year and current year
    for root, dirs, files in os.walk(dir_mne):
        # For each subdir (i.e. for each site)
        for subdir in dirs:
            print(f"Trying for {subdir}")

            place = subdir
            mne_last = ''
            mne_current = ''
            mne_dict = {}

            # --------------------------------------------------
            # DEMs
            # --------------------------------------------------
            # Find last DEM
            find_last = False
            for file in os.listdir(f"{dir_mne}/{subdir}"):
                if re.search(rf'{last_year}', file) and re.search(r'.tif$', file):
                    mne_last = f"{dir_mne}/{subdir}/{file}"
                    print(mne_last)
                    mne_last_name = os.path.splitext(os.path.basename(file))[0]
                    mne_dict[mne_last_name] = mne_last
                    find_last = True

            if not find_last:
                print(f"Can't find DEM for {last_year} at {subdir}, skipping")

            # Find current DEM if last found
            if not find_last:
                print(f"Can't find DEM for {last_year} at {subdir}")
                continue
            else:
                find_current = False
                iter_year = current_year

                if gap:
                    while find_current != True and iter_year <= end_year:
                        for file in os.listdir(f"{dir_mne}/{subdir}"):
                            if re.search(rf'.*{iter_year}.*\.tif$', file):
                                find_current = True
                                mne_current = f"{dir_mne}/{subdir}/{file}"
                                print(mne_current)
                                mne_current_name = os.path.splitext(os.path.basename(file))[0]
                                mne_dict[mne_current_name] = mne_current

                        iter_year += 1

                    iter_year = iter_year - 1

                else:
                    for file in os.listdir(f"{dir_mne}/{subdir}"):
                        if re.search(rf'.*{current_year}.*\.tif$', file):
                            find_current = True
                            mne_current = f"{dir_mne}/{subdir}/{file}"
                            print(mne_current)
                            mne_current_name = os.path.splitext(os.path.basename(file))[0]
                            mne_dict[mne_current_name] = mne_current

            # Add control. The dictionary has to be of length 2
            if len(mne_dict) != 2:
                print("Can't process just one year, skipping")
                continue

            # Retrieve files for current and last DEM
            match_last = mne_dict[mne_last_name]
            match_current = mne_dict[mne_current_name]

            # Define layer name
            name_last = re.search(r'.*(?=/)/(.*(?=\.))', match_last).group(1)
            print(name_last)
            name_current = re.search(r'.*(?=/)/(.*(?=\.))', match_current).group(1)
            print(name_current)

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
                            if re.search(rf'{place}_mask_cordon\.shp', file):
                                mask = QgsVectorLayer(f"{subdir_path}/{file}", f"{place}_{last_year}_{iter_year}_mask")

                                # Mask last
                                mne_last_path = f"{dir_mne_cut}/{place}/{name_last}_mask_cordon.tif"

                                # TODO: Handle resolution : DEMs doesn't always share the same planimetric resolution
                                last_exists = False
                                if os.path.exists(mne_last_path):
                                    print(f"{name_last}_mask_cordon.tif already exists, skipping...")
                                    last_exists = True
                                else:
                                    print("Clip last mne")
                                    params = {
                                        'INPUT': match_last,
                                        'MASK': mask,
                                        'SOURCE_CRS': None,
                                        'TARGET_CRS': None,
                                        'TARGET_EXTENT': None,
                                        'NODATA': None,
                                        'ALPHA_BAND': False,
                                        'CROP_TO_CUTLINE': True,
                                        'KEEP_RESOLUTION': False,
                                        'SET_RESOLUTION': False,
                                        'X_RESOLUTION': None,
                                        'Y_RESOLUTION': None,
                                        'MULTITHREADING': False,
                                        'OPTIONS': '',
                                        'DATA_TYPE': 0,
                                        'EXTRA': '',
                                        'OUTPUT': mne_last_path
                                    }

                                    processing.run("gdal:cliprasterbymasklayer", params)

                                # Mask current
                                mne_current_path = f"{dir_mne_cut}/{place}/{name_current}_mask_cordon.tif"
                                current_exists = False
                                if os.path.exists(mne_current_path):
                                    print(f"{name_current}_mask_cordon.tif already exists, skipping...")
                                    current_exists = True
                                else:
                                    print("Clip current mne")
                                    params = {
                                        'INPUT': match_current,
                                        'MASK': mask,
                                        'SOURCE_CRS': None,
                                        'TARGET_CRS': None,
                                        'TARGET_EXTENT': None,
                                        'NODATA': None,
                                        'ALPHA_BAND': False,
                                        'CROP_TO_CUTLINE': True,
                                        'KEEP_RESOLUTION': False,
                                        'SET_RESOLUTION': False,
                                        'X_RESOLUTION': None,
                                        'Y_RESOLUTION': None,
                                        'MULTITHREADING': False,
                                        'OPTIONS': '',
                                        'DATA_TYPE': 0,
                                        'EXTRA': '',
                                        'OUTPUT': mne_current_path
                                    }

                                    processing.run("gdal:cliprasterbymasklayer", params)

                                # Définir le nom du fichier en sorti
                                mne_diff_name = f'{dir_dod}/{place}/{place}_{last_year}_{iter_year}_DOD_mask_cordon.tif'

                                # If last DEM or current DEM not exists, process DOD or if file doesn't exist
                                if not last_exists or not current_exists or not os.path.exists(mne_diff_name):
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
                                        '(mne_current@1 - mne_last@1)',  # Expression
                                        mne_diff_name,  # Output
                                        'GTiff',  # Format
                                        lyr2.extent(), lyr2.width(), lyr2.height(),  # Extents
                                        entries  # Les rasters en entrées
                                    )
                                    calc.processCalculation()
                                else:
                                    print(f"DOD already exists for {last_year} and {iter_year} at {place}")

                            else:
                                continue

end_time = time.time()
execution_time = end_time - start_time

print(f"Done in {execution_time} seconds")
