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

import os

import magnaprobe_toolbox as mt

__author__ = "Marc Oggier"

# Files commented are already in semi-final product

RAW_FP = "/mnt/data/UAF-data/raw/SALVO/20240419-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240419.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240421-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240421.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240421-ICE/magnaprobe/salvo_ice_library_magnaprobe-geodel_20240421.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240420.00.dat"
RAW_FP = "/mnt/data/UAF-data/raw/SALVO/20240418-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240418.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240418-BEO/magnaprobe/salvo_beo_line_magnaprobe-geo2_20240418.00.dat"
RAW_FP = "/mnt/data/UAF-data/raw/SALVO/20240417-ICE/magnaprobe/salvo_ice_line_magnaprobe-geo1_20240417.00.dat"

RAW_FP = "/mnt/data/UAF-data/raw/SALVO/20240522-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240522.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240525-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240525.00.dat"

RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240527-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240527.00.dat"

RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240525-ARM/magnaprobe/salvo_arm_line50cm_magnaprobe-geodel_20240526.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240526-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240526-133258.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240526-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240526-140039.00.dat"

#
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240527-ARM/magnaprobe/salvo_arm_longline_magnaprobe-geodel_20240527.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240528-ARM/magnaprobe/salvo_arm_longline_magnaprobe-geodel_20240527.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-ARM/salvo_arm_line-ice_magnaprobe-geodel_20240529.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-ARM/salvo_arm_line_magnaprobe-geodel_20240529.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-BEO/salvo_beo_longline_magnaprobe-geodel_20240529.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-BEO/salvo_beo_snowpit_magnaprobe-geodel_20240529.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240529.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240530.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240601-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240601.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240601-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240601.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/salvo_beo_line_magnaprobe-geodel_20240602.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_arm-connector_magnaprobe-geodel_20240602.00.dat"
# RAW_FP = "/mnt/data/UAF-data/raw/SALVO/20260603-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240603.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240604-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240604.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240604-ICE/magnaprobe/salvo_ice_longline_magnaprobe-geodel_20240604.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-ARM/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240605.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-ARM/magnaprobe/salvo_arm_longline_magnaprobe-geodel_20240605.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240605.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-BEO/magnaprobe/salvo_beo_longline_magnaprobe-geodel_20240605.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240530.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240506-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240606.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240606-ARM/magnaprobe/salvo_arm_sg27_magnaprobe-geodel_20240606.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_library-20240602b_magnaprobe-geodel_20240602.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_library-20240602a_magnaprobe-geodel_20240602.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240604-ARM/magnaprobe/salvo_arm_library-20240604a_magnaprobe-geodel_20240604.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240607-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240607.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240607-ICE/magnaprobe/salvo_ice_library_magnaprobe-geodel_20240607.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240608-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240608.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240608-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240608.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240609-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240609.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240610-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240610.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240610-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240610.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240611-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240611.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240612-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240612.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240613-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240613.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240613-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240613.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-BEO/magnaprobe/salvo_beo_snowpit_magnaprobe-geodel_20240529.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240614-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240614.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240614-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240614.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240615-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240615.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240615-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240615.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240616-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240616.00.dat"
# RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240616-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240616.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240617-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240617.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240617-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240617-142332.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240617-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240617-142332.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240617-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240617-144749.00.dat"
RAW_FP = "/mnt/data/UAF-data/working_a/SALVO/20240618-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240617-130204.00.dat"

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
raw_df = mt.tools.all_check(raw_df, display=False, distance_type=None)

# Export to filename for manual analysis
mt.export.data(raw_df, output_fp, display=True)

# Export a duplicate filename with a `.a2.csv` extension to be edited.
a2csv_fp = output_fp.split(".")[0] + ".a2.csv"
if not os.path.exists(a2csv_fp):
    export_df = mt.export.data(raw_df, a2csv_fp, display=True, drop_header=True)

# Export config to config file
config_fp = mt.io.config.save(config, output_fp)
