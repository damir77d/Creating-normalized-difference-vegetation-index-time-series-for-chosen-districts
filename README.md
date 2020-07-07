**NDVI analysis of different districts of Moscow at different points in time**


Images from Landsat 8 were used.

LIDAR-FWF-data-processing-NEON
This repository contains functions for processing of NEON LIDAR FWF data.

Codes
1) LIDAR-FWF processing Cookbook.ipynb
The jupyter notebook called LIDAR-FWF processing Cookbook contains functions for processing (data extraction, georeferencing, Gaussian fitting etc).

2) neon_fwf.py
'neon_fwf.py' is a little python module for creating hdf files from pulsewave files. All signals in hdf file will be georeferenced. About the file structure, it contains 'Amplitude', 'Index' and 'XYZ' coordinates. Each amplitude value has corresponding 0 or 1 where 0 - is standing for outgoing and 1 is standing for returning signal.
