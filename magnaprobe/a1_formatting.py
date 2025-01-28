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
from matplotlib import gridspec

import magnaprobe_toolbox as mt

import numpy as np

from cmcrameri import cm


logger = logging.getLogger(__name__)

# -- USER VARIABLES
# Enable plotting with relative coordinate to the transect origin x0=0, y0=0
PLOT_ORIGIN_FLAG = True
NPOINTS = 201
TARGET_DIST = 1
MODE = None

# Data filename
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240419-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240419.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240421-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240421.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240421-ICE/magnaprobe/salvo_ice_library_magnaprobe-geodel_20240421.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240420.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240418-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240418.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240417-ICE/magnaprobe/salvo_ice_line_magnaprobe-geo1_20240417.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240417-ICE/magnaprobe/salvo_ice_line_magnaprobe-geo1_20240417.a4.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240522-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240522.a4.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240526-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240526-133258.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240526-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240526-140039.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240527-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240527.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240527-ARM/magnaprobe/salvo_arm_longline_magnaprobe-geodel_20240527.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240528-ARM/magnaprobe/salvo_arm_longline_magnaprobe-geodel_20240528.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240525-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240525.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240529.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240529.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-BEO/salvo_beo_longline_magnaprobe-geodel_20240529.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-BEO/salvo_beo_snowpit_magnaprobe-geodel_20240529.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240601-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240601.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240601-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240601.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240602.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_arm-connector_magnaprobe-geodel_20240602.a2.dat"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20260603-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240603.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240604-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240604.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240604-ICE/magnaprobe/salvo_ice_longline_magnaprobe-geodel_20240604.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240605.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-ARM/magnaprobe/salvo_arm_longline_magnaprobe-geodel_20240605.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240605.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240605-BEO/magnaprobe/salvo_beo_longline_magnaprobe-geodel_20240605.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240530.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240607-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240607.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240608-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240608.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240608-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240608.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240609-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240609.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240610-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240610.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240610-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240610.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240611-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240611.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240612-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240612.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240613-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240613.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240614-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240614.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240615-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240614.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240614-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240614.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240615-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240615.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240616-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240616.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240616-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240616.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240617-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240617.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240617-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240617-142332.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240617-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240617-144749.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240618-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240617-130204.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240618-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240617-130204b.a2.csv"

# Longline
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240609-arm/magnaprobe/salvo_arm_longline_magnaprobe-geodel_20240609.a2.csv"

# Load qc-ed data
qc_data = mt.load.qc_data(QC_FP)

# Load config:
config = mt.io.config.load(QC_FP)

# Compute distance after file sanitation
qc_data = mt.analysis.distance.compute(qc_data)
if "longline" in QC_FP:
    qc_data = mt.tools.all_check(qc_data, direction="EW", distance_type="DistOrigin")
elif "library" in QC_FP:
    qc_data = mt.tools.all_check(qc_data, direction=None, distance_type=None)
else:
    qc_data = mt.tools.all_check(qc_data, direction="EW", distance_type=None)
    qc_data = mt.analysis.distance.compute(qc_data)

# Record start and end time of the transect line
starttime = qc_data.Timestamp.min().isoformat()
endtime = qc_data.Timestamp.max().isoformat()
config["starttime"] = starttime
config["endtime"] = endtime

# MODE DETECTION:

# Insert LineLocation
if "longline" in os.path.basename(QC_FP):
    # TODO: implement longline
    # Since the longline transect and the library is measured without a fixed distance, we don't check for the distance
    qc_data.loc[qc_data["QC_flag"] == 8, "QC_flag"] = 1
    logger.error("other mode are not implemented")
    if "LineLocation" not in qc_data.columns:
        qc_data["LineLocation"] = [np.nan] * len(qc_data)
    else:
        qc_data = qc_data.sort_values(by=["LineLocation"])

    qc_data.loc[qc_data["SnowDepth"] < 0, "SnowDepth"] = 0


elif "line" in QC_FP:
    if "line50cm" in QC_FP:
        NPOINTS = 401
    if "LineLocation" not in qc_data.columns:
        qc_data["LineLocation"] = [np.nan] * len(qc_data)
    else:
        qc_data = qc_data.sort_values(by=["LineLocation"])



    if len(qc_data) < NPOINTS:
        # Add information in comment columns
        qc_data.loc[qc_data["TrackDist"] > 1.9, "Comment"] = "MISSING PREVIOUS POINT"

        # Generate output_filename
        output_fp = mt.io.output_filename(QC_FP)
        mt.export.data(qc_data, output_fp, display=False)
        n_missing = NPOINTS - len(qc_data)
        if n_missing > 2:
            logger.warning(
                str(
                    f"{n_missing} point is missing. Examine exported file "
                    + output_fp.split("/")[-1]
                    + ", and insert nan-filled missing row"
                )
            )
        else:
            logger.warning(
                f"{n_missing} point is missing. Examine exported file %s, and insert nan-filled missing row"
                + output_fp.split("/")[-1]
            )
        # Show information
        print(
            "Point before which distance is larger than expected"
            + f"{TARGET_DIST * 2 * 0.9}"
        )
        print(
            qc_data.loc[
                qc_data["TrackDist"] > TARGET_DIST * 2 * 0.9,
                ["Record", "Counter", "Timestamp", "TrackDist", "QC_flag"],
            ]
        )

    elif len(qc_data) > NPOINTS:
        # TODO: when one have to deal with this kind of file
        logger.error("Fix case when len(qc_data) > NPOINTS in line formatting")
        # Generate output_filename
        output_fp = mt.io.output_filename(QC_FP)
        mt.export.data(qc_data, output_fp)
        n_added = len(qc_data) - NPOINTS
        logger.warning(
            str(
                f"{n_added} point is missing. Examine exported file "
                + output_fp.split("/")[-1]
                + ", and removed extra row"
            )
        )

        if len(qc_data[qc_data["QC_flag"] > 6]) > 0:
            print("Cleaning is still needed")

    else:
        # Populate 'LineLocation' with 0, 1, 2, ... 200 distance array
        if "line50cm" in QC_FP:
            qc_data["LineLocation"] = np.linspace(0, 200, NPOINTS)
        else:
            qc_data["LineLocation"] = np.arange(0, 201, 1)

        qc_data["LineLocation"] = np.arange(0, 201, 1)
        qc_data["QC_flag"] = 1
        print("Populating LineLocation with 0, 1, 2, ... 200 m")

elif "library" in os.path.basename(QC_FP):
    # Since the library is measured without a fixed distance, the distance between point is not checked anymore.
    qc_data.loc[qc_data["QC_flag"] == 8, "QC_flag"] = 1
    if len(qc_data[qc_data["QC_flag"] > 6]) > 0:
        print("Cleaning is still needed")
    else:
        qc_data["QC_flag"] = 1
    qc_data.loc[qc_data["SnowDepth"] < 0, "SnowDepth"] = 0
elif "snowpit" in os.path.basename(QC_FP):
    # Since the library is measured without a fixed distance, the distance between point is not checked anymore.
    qc_data.loc[qc_data["QC_flag"] == 8, "QC_flag"] = 1

else:
    logging.error("Transect type is not defined")

# Generate output_filename
output_fp = mt.io.output_filename(QC_FP)
mt.export.data(qc_data, output_fp)

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

if "snowpit" not in os.path.basename(QC_FP):
    FIG_TITLE = " - ".join([site.upper(), NAME, date])

    # Move origin points to x0, y0
    plt.style.use("ggplot")

    # Data status plot
    if "longline" in os.path.basename(QC_FP):
        plot_df = qc_data.set_index("TrackDistCum", drop=True)
        plot_df = mt.io.plot.set_origin(plot_df, plot_from_origin=PLOT_ORIGIN_FLAG)
        fig = mt.io.plot.summary(plot_df, library=False)
    elif "line" in QC_FP:
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

    fig.suptitle(FIG_TITLE)
    plt.savefig(fig_fp)
    plt.show()

else:
    # Plot
    qc_data["x0"] = qc_data["X"] - qc_data["X"].min()
    qc_data["y0"] = qc_data["Y"] - qc_data["Y"].min()

    qc_data.loc[qc_data["SnowDepth"] < 0.005, "SnowDepth"] = 0

    snow_depth_scale = qc_data["SnowDepth"].max() - qc_data["SnowDepth"].min()
    hs0 = cm.davos(
        qc_data.loc[qc_data["SnowDepth"].notnull(), ["SnowDepth"]] / snow_depth_scale
    )
    x0 = qc_data.loc[qc_data["SnowDepth"].notnull(), ["x0"]]
    y0 = qc_data.loc[qc_data["SnowDepth"].notnull(), ["y0"]]

    w_fig, h_fig = 8, 11
    NROWS = 1
    NCOLS = 1
    fig = plt.figure(figsize=[w_fig, h_fig])
    gs1 = gridspec.GridSpec(
        NROWS, NCOLS, height_ratios=[1] * NROWS, width_ratios=[1] * NCOLS
    )
    ax = [[fig.add_subplot(gs1[0, 0])]]
    ax[0][0].scatter(x0, y0, c=hs0, s=100)

    plt.savefig("/home/megavolts/Desktop/snowpitmap.pdf")
    plt.show()

# Export config to config file
config_fp = mt.io.config.save(config, QC_FP)


qc_data.loc[qc_data["SnowDepth"] <= 0].__len__() / 2.01
