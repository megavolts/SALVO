# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
Inputs:
    RAW_FP: Raw data from the magnaprobe
    ESPG_LOCAL: ESPG projection number for local projection, optional
    CONFIG:

Outputs:
    Preprocessed snow depth data with initial quality and calibration check. Output file will need to
    be post processed
"""

import logging

import magnaprobe_toolbox as mt

__author__ = "Marc Oggier"

RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240420.00.dat"

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
config["filename"] = RAW_FP.rsplit("/", maxsplit=1)[-1].split(".")[0]
config["espg"] = ESPG_LOCAL
config["transect type"] = RAW_FP.rsplit("/", maxsplit=1)[-1].split("_")[2]
config["timezone"] = "UTC-8"

# Read raw magnaprobe data
raw_df = mt.load.raw_data(RAW_FP, local_EPSG=ESPG_LOCAL)

# Compute distance:
raw_df = mt.analysis.distance.compute(raw_df)

# Perform quality and calibration check
raw_df = mt.tools.all_check(raw_df, display=False)

# Export to filename for manual analysis
mt.export.data(raw_df, output_fp, display=True)

# Export a duplicate filename with a `.a2.csv` extension to be edited.
mt.export.data(
    raw_df, output_fp.split(".")[0] + ".a2.csv", display=True, drop_header=True
)

# Export config to config file
config_fp = mt.io.config.save(config, output_fp)
