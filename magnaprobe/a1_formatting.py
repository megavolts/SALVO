"""
Inputs:
    QC_FP: Sanitized quality-checked snow depth data
    CONFIG:
    PLOT_ORIGIN_FLAG: optional, plot with respect to transect origin point.
    MODE: 'line', 'longline', 'library
Outputs:
    Formatted snow depth data; a-grade product
"""
import logging

import matplotlib.pyplot as plt

import magnaprobe_toolbox as mt

import numpy as np

logger = logging.getLogger(__name__)

# -- USER VARIABLES
# Enable plotting with relative coordinate to the transect origin x0=0, y0=0
PLOT_ORIGIN_FLAG = True
NPOINTS = 201
TARGET_DIST = 1
MODE = "line"

# Data filename
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240420.a2.csv"

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

# Insert LineLocation
if MODE == "Line:":
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

        if len(qc_data[qc_data["Quality"] > 6]) > 0:
            print("Cleaning is still needed")

    else:
        # Populate 'LineLocation' with 0, 1, 2, ... 200 distance array
        qc_data["LineLocation"] = np.arange(0, 201, 1)
else:
    # TODO: implement longline and library
    # Since the longline transect and the library is measured without a fixed distance, we don't check for the distance
    qc_data.loc[qc_data["Quality"] == 8, "Quality"] = 0
    if len(qc_data[qc_data["Quality"] > 6]) > 0:
        print("Cleaning is still needed")
    logger.error("other mode are not implemented")


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

FIG_TITLE = " - ".join([site.upper(), NAME, date])

# Data status plot
if MODE == "line":
    if qc_data["LineLocation"].isna().all():
        plot_df = qc_data.set_index("TrackDistCum", drop=True)
        FIG_TITLE += " Garbage Line Location"
    else:
        plot_df = qc_data.set_index("LineLocation", drop=True)
else:
    # TODO: implement longline and library
    logger.error("other mode are not implemented")
    plot_df = qc_data.set_index("TrackDistCum", drop=True)

input_df = plot_df
# Move origin points to x0, y0

plot_df = mt.io.plot.set_origin(plot_df, plot_from_origin=PLOT_ORIGIN_FLAG)

plt.style.use("ggplot")
fig = mt.io.plot.summary(plot_df)
fig.suptitle(FIG_TITLE)
plt.savefig(fig_fp)
plt.show()

# Export config to config file
config_fp = mt.io.config.save(config, QC_FP)
