__name__ = "00_preprocessing_qc"

import magnaprobe_toolbox as mt
import os
import logging
import yaml

# RAW_FP = '/mnt/data/UAF-data/raw/SALVO/20240416-ARM/magnaprobe/salvo_arm_longline_magnaprobe-geo1_20240416.00.dat'
# RAW_FP = '/mnt/data/UAF-data/raw/SALVO/20240417-ICE/magnaprobe/salvo_ice_line_magnaprobe-geo1_20240417.00.dat'
# RAW_FP = '/mnt/data/UAF-data/raw/SALVO/20240418-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240418.00.dat'
# RAW_FP = '/mnt/data/UAF-data/working_a/SALVO/20240418-BEO/magnaprobe/salvo_beo_longline_magnaprobe-geo2_20240418.00.dat'
# RAW_FP = '/mnt/data/UAF-data/working_a/SALVO/20240418-BEO/magnaprobe/salvo_beo_line_magnaprobe-geo2_20240418.00.dat'
# RAW_FP = '/mnt/data/UAF-data/raw/SALVO/20240419-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240419.00.dat'
# RAW_FP = '/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240420.00.dat'
# RAW_FP = '/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/magnaprobe/salvo_beo_longline_magnaprobe-geodel_20240420.00.dat'
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240421-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240421.00.dat"
# RAW_FP = '/mnt/data/UAF-data/working_a/SALVO/20240421-ICE/magnaprobe/salvo_ice_library_magnaprobe-geodel_20240421.00.dat'

# -- USER VARIABLES
# Enable plotting with relative coordinate to the transect origin x0=0, y0=0
# ESPG code for local projection
ESPG_LOCAL = 3338  # for Alaska

# When True, if a config file exists for the raw file, the raw file is sanitized and trimmed to remove any unnecessary
# entries. This allows to skip the manual sanitizing process.
CONFIG = True

# -- SCRIPTS
# Logger:
logger = logging.getLogger(__name__)

# Define output filename
output_fp = mt.load.output_filename(RAW_FP)

# Load config, if not create
config = mt.io.config.load(RAW_FP)
config["filename"] = os.path.basename(RAW_FP).split(".")[0]
config["espg"] = ESPG_LOCAL

# Read raw magnaprobe data
raw_df = mt.load.raw_data(RAW_FP, local_EPSG=ESPG_LOCAL)

# Compute distance:
raw_df = mt.analysis.distance.compute(raw_df)

# Perform quality and calibration check
raw_df = mt.tools.all_check(raw_df, display=False)

# Export to filename for manual analysis
mt.export.data(raw_df, output_fp)
print("File exported to " + output_fp)

# Export config to config file
config_fp = mt.io.config.save(config, output_fp)
