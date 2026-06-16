SedHydro Installation and Setup Guide

Overview
SedHydro is a hydrology-model-agnostic erosion and sediment transport modelling framework that integrates hillslope erosion, sediment routing, and multi-fraction river transport within a flexible Python-based workflow.
This guide explains how to install all required dependencies and run SedHydro on a new Windows or macOS computer.

1. Prerequisites
Before starting, install one of the following:
• Miniconda
• Anaconda

2. Obtain the SedHydro Repository

Option A — Clone from GitHub

```
git clone https://github.com/Armanhd/sedhydro.git
cd sedhydro
```

Option B — Download ZIP

1. Download the repository ZIP file from GitHub.
2. Extract the ZIP archive.
3. Open a terminal inside the extracted SedHydro folder.

3. Create the Conda Environment

The repository already contains:

environment.yml

Navigate to the SedHydro directory:

cd path/to/SedHydro

Create the environment:

conda env create -f environment.yml

This may take several minutes.

4. Activate the Environment

conda activate sedhydro

If a different environment name is specified in environment.yml, use that name instead.

Verify the environment:

conda info --envs

The active environment will be marked with *.

5. Verify Installation

python -c "import numpy, pandas, geopandas, rasterio, tomllib; from netCDF4 import Dataset, num2date; import matplotlib.pyplot as plt; print('SedHydro environment is ready')"

If no errors occur, the environment is correctly configured.

6. Repository Structure

SedHydro/
│
├── SedHydro.py
├── SedHydro_mp.py
├── optimisation_updated.py
├── utils.py
├── mapMaker.py
├── directory_settings_*.toml
├── environment.yml
│
├── TempSedRout/
│   ├── TempSedRout_function.py
│   ├── TempSedRout_storage_function.py
│   └── constants.toml
│
├── outputs/
├── settings/
├── shapefiles/
├── attributes/
└── data/

7. Configure SedHydro

SedHydro uses TOML configuration files to define:
• Model settings
• Working directories
• Catchment inputs
• Hydrological model outputs
• Sediment parameters
• Calibration settings
• Output locations

Example:

toml_file = "directory_settings_Athabasca.toml"

Before running:
1. Open the selected TOML file.
2. Update paths for your local computer.
3. Verify all referenced files exist.

8. Running SedHydro

Standard Version

python SedHydro.py

Multiprocessing Version

python SedHydro_mp.py

The multiprocessing version is recommended for large catchments and calibration runs.

9. Optional pip Installation

Conda is recommended because it handles geospatial dependencies more reliably on both Windows and macOS.

requirements.txt

numpy
pandas
geopandas
rasterio
netCDF4
matplotlib
scipy
deap
pyproj
shapely

Then install:

pip install -r requirements.txt

10. Notes

The following modules are included with Python and do not require separate installation:
• os
• sys
• re
• random
• multiprocessing
• copy
• datetime
• pickle
• math
• time
• platform
• glob
• pathlib

SedHydro uses Python 3.11.

Main third-party packages include:
• numpy
• pandas
• geopandas
• rasterio
• netCDF4
• matplotlib
• scipy
• deap
• pyproj
• shapely

11. Troubleshooting

Environment Creation Fails

conda update -n base -c defaults conda

Then retry:

conda env create -f environment.yml

Geopandas or Rasterio Import Errors

Use the Conda environment supplied by environment.yml.
Avoid mixing Conda and pip installations.

Wrong Python Version

python --version

SedHydro is designed for Python 3.11.

12. Quick Summary

git clone https://github.com/<organization>/SedHydro.git

cd SedHydro

conda env create -f environment.yml

conda activate sedhydro

python SedHydro_mp.py

This workflow provides a complete and reproducible installation of SedHydro on Windows and macOS systems.
