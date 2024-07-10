"""
Inputs:
    QC_FP: Sanitized quality-checked snow depth data
    CONFIG:
    PLOT_ORIGIN_FLAG: optional, plot with respect to transect origin point.
    MODE: 'line', 'longline', 'library, if None try to detect automatically
Outputs:
    Formatted snow depth data; a-grade product
"""
import logging

import os

import matplotlib.pyplot as plt

import magnaprobe_toolbox as mt

import numpy as np

logger = logging.getLogger(__name__)

# -- USER VARIABLES
# Enable plotting with relative coordinate to the transect origin x0=0, y0=0
PLOT_ORIGIN_FLAG = True
NPOINTS = 201
TARGET_DIST = 1
MODE = None


# Data filename
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240417-ICE/magnaprobe/salvo_ice_line_magnaprobe-geo1_20240417.a4.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240522-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240522.a4.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240526-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240526-133258.a4.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240530.a3.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240529.a4.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240613-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240613.a3.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240615-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240615.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240615-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240615.a3.csv"


# Load qc-ed data
qc_data = mt.load.qc_data(QC_FP)

# Load config:
config = mt.io.config.load(QC_FP)

# Compute distance after file sanitation
qc_data = mt.analysis.distance.compute(qc_data)
qc_data = mt.tools.all_check(qc_data, direction="EW")

# Record start and end time of the transect line
starttime = qc_data.Timestamp.min().isoformat()
endtime = qc_data.Timestamp.max().isoformat()
config["starttime"] = starttime
config["endtime"] = endtime

# Move origin points to x0, y0
plt.style.use("ggplot")
# Generate output_filename
output_fp = mt.io.output_filename(QC_FP)


fig_fp = output_fp.split(".")[0] + ".pdf"
# Plot basic figures:
site = output_fp.split("_")[2].upper()
date = output_fp.split(".")[0][-8:]
if "_longline" in output_fp:
    NAME = "Long transect"
elif "_line" in output_fp:
    NAME = "200m transect"
elif "library" in output_fp:
    NAME = "Library site"
else:
    NAME = None

FIG_TITLE = " - ".join([site.upper(), NAME, date])


# Data status plot
if "line" in QC_FP:
    if qc_data["LineLocation"].isna().all():
        plot_df = qc_data.set_index("TrackDistCum", drop=True)
        FIG_TITLE += " Garbage Line Location"
    else:
        plot_df = qc_data.set_index("LineLocation", drop=True)
    plot_df = mt.io.plot.set_origin(plot_df, plot_from_origin=PLOT_ORIGIN_FLAG)

    fig = mt.io.plot.summary(plot_df, library=False)

elif "library" in os.path.basename(QC_FP):
    # TODO: implement better figure for library
    logger.error("implement better figure")
    plot_df = qc_data.set_index("TrackDistCum", drop=True)
    plot_df = mt.io.plot.set_origin(plot_df, plot_from_origin=PLOT_ORIGIN_FLAG)
    fig = mt.io.plot.summary(plot_df, library=True)
elif "longline" in os.path.basename(QC_FP):
    logger.error("other mode are not implemented")

fig.suptitle(FIG_TITLE)
plt.savefig(fig_fp)
plt.show()

# Export config to config file
config_fp = mt.io.config.save(config, QC_FP)

qc_data.loc[qc_data["SnowDepth"] <= 0].__len__() / 2.01
