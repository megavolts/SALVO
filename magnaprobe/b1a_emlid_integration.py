# -*- coding: utf-8 -*-
"""
Integrate PPK position from corrected .pos file from EmlidStudio with the MangaProbe qc-ed data

Inputs:
    QC-ed MagnaProbe data in a comma-separated variable (csv) file
    Corrected PPK position (.pos) file

Outputs:
    b-grade product incorporated data from 2 instruments:
    Comma-separated variable (csv) file with
    - timestamp
    - lat/lon and XYZ coordinate from MagnaProbe embedded GPS, denoted with _mg tag
    - quality fix for MagnaProbe embedded GPS
    - lat/lon and XYZ coordinate from reachm2 rover, denoted with _emlid tag
    - quality fix for reachm2 rover
    Config file containing origin filename use to generate the new b-grade product

Notes:
    User only needs to change input files on lines 27-29 and uncomment line 69 to write the corrected csv file
    If it seems off it could be due to the time-offset (line 41) between MagnaProbe Timestamp and GPST


@author: Marc Oggier
University of Alaska, Fairbanks
Based on work from Thomas Van Der Weide, Boise State University

4/29/2024
"""

import os
from datetime import timedelta

from matplotlib import gridspec
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
import pandas as pd
from scipy.stats import linregress
import yaml

from salvo.analysis import distance

# Filepath to data
MAGNA_FP = "/mnt/data/UAF-data/working_a/SALVO/20240530-ICE/magnaprobe/salvo_ice_line_magnaprobe-geodel_20240530.a1.dat"
EMLID_FP = "/mnt/data/media/photography/SALVO/working_a/20240530-ICE/emlid/ubx/rinex_salvo_ice_ice_reachm2-salvo-raw_20240530-194700/salvo_ice_ice_reachm2-salvo-raw_20240530-194700_events.pos"

# Perform GPS comparison analysis, and display figure
DISPLAY = True

# Timeoffset between emlid and magnaprobe
OFFSET = timedelta(hours=0, seconds=0)
# b-grade products are generated in 'working_b' directory
output_dir = os.path.dirname(MAGNA_FP).replace("working_a", "working_b")

# load config file
config = {}
for file in os.listdir(os.path.dirname(MAGNA_FP)):
    if file.endswith("yaml") and file.startswith(
        os.path.basename(MAGNA_FP).split(".")[0]
    ):
        file_fp = os.path.join(os.path.dirname(MAGNA_FP), file)
        with open(file_fp, "r", encoding="utf-8") as f:
            config["magna"] = yaml.safe_load(f)
        break
for file in os.listdir(os.path.dirname(EMLID_FP)):
    if file.endswith("yaml"):
        file_fp = os.path.join(os.path.dirname(EMLID_FP), file)
        with open(file_fp, "r", encoding="utf-8") as f:
            config["emlid"] = yaml.safe_load(f)
        break
timezone = float(config["magna"]["timezone"].split("UTC")[-1])

utc_starttime = (
    pd.to_datetime(config["magna"]["starttime"])
    - timedelta(0, 60)
    - timedelta(hours=timezone)
)
utc_endtime = (
    pd.to_datetime(config["magna"]["endtime"])
    + timedelta(0, 60)
    - timedelta(hours=timezone)
)

# Load position file
print("Loading: ", EMLID_FP)
pos_df = pd.read_csv(EMLID_FP, header=9)
pos_df["Timestamp"] = pd.to_datetime(pos_df["timestamp"], format="ISO8601")
pos_freq = pos_df["Timestamp"].diff().median()

pos_df["Timestamp"] = pos_df["Timestamp"].apply(lambda x: x.round(pos_freq))

# Append '_el' to all columns headers from position file, but Timestamp
columns_dict = {col: col + "_el" for col in pos_df.columns if col not in ["Timestamp"]}
pos_df.rename(columns=columns_dict, inplace=True)

# Load data file
print("Loading: ", MAGNA_FP)
magna_df = pd.read_csv(MAGNA_FP, header=0)
# Convert magna to UTC
magna_df["Timestamp"] = (
    pd.to_datetime(magna_df["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
    - timedelta(hours=timezone)
    - OFFSET
)
# Round magna probe time to pose_freq
magna_df["Timestamp"] = magna_df["Timestamp"].apply(lambda x: x.round(pos_freq))
# Append '_mg' to all columns headers from position file, but Timestamp
columns_dict = {
    col: col + "_mg" for col in magna_df.columns if col not in ["Timestamp"]
}
magna_df.rename(columns=columns_dict, inplace=True)

# Merge data frame
out_df = pd.merge(magna_df, pos_df, on="Timestamp", how="left")

# Compute Distace for emlid data


out_df[
    ["TrackDist_el", "TrackDistCum_el", "DistOrigin_el"]
] = distance.compute_distance(out_df[["X_el", "Y_el", "Z_el"]])

if DISPLAY:
    print("Performing geospatial differences analysis")

# Create figure framework
w_fig, h_fig = 8, 11
ncols, nrows = 3, 3
fig = plt.figure(figsize=[w_fig, h_fig])
gs1 = gridspec.GridSpec(
    nrows, ncols, height_ratios=[1] * nrows, width_ratios=[1] * ncols
)
ax = [
    [fig.add_subplot(gs1[0, :]), None, None],
    [
        fig.add_subplot(gs1[1, 0]),
        fig.add_subplot(gs1[1, 1]),
        fig.add_subplot(gs1[1, 2]),
    ],
    [
        fig.add_subplot(gs1[2, 0]),
        fig.add_subplot(gs1[2, 1]),
        fig.add_subplot(gs1[2, 2]),
    ],
]


AX_V, AX_H = 0, 0
ax[AX_V][AX_H].set_title("GPS location")
ax[AX_V][AX_H].scatter(
    out_df["X_mg"], out_df["Y_mg"], color="k", marker="x", label="Magnaprobe"
)
qf_label = {1: "Fix", 2: "Float", 5: "Single"}
qf_color = {1: "green", 2: "orange", 5: "red"}

for QF in out_df.QualityFix_el.unique():
    ax[AX_V][AX_H].scatter(
        out_df.loc[out_df["QualityFix_el"] == QF, "X_el"],
        out_df.loc[out_df["QualityFix_el"] == QF, "Y_el"],
        color=qf_color[QF],
        marker="+",
        label="PPK reachm2 (" + qf_label[QF] + ")",
    )

ax[AX_V][AX_H].legend(fancybox=False)
ax[AX_V][AX_H].set_xlabel("UTM N (m)")
ax[AX_V][AX_H].set_ylabel("UTM E (m)")

AX_V, AX_H = 1, 0
for QF in out_df.QualityFix_el.unique():
    ax[AX_V][AX_H].scatter(
        out_df.loc[out_df["QualityFix_el"] == QF, "X_el"],
        out_df.loc[out_df["QualityFix_el"] == QF, "Y_el"],
        color=qf_color[QF],
        marker="+",
        label="PPK reachm2 (" + qf_label[QF] + ")",
    )

ax[AX_V][AX_H].scatter(out_df["X_mg"], out_df["Y_mg"], color="k", marker="x")
S_EL = 1000  # scale factor for the emlid sigmaNE ellipse
S_MG = 10  # scale factor for the magnaprobe HDOP ellipse
for ii in out_df.index:
    ellipse1 = Ellipse(
        xy=(out_df.loc[ii, "X_mg"], out_df.loc[ii, "Y_mg"]),
        width=out_df.loc[ii, "HDOP_mg"] * S_MG,
        height=out_df.loc[ii, "HDOP_mg"] * S_MG,
        facecolor="k",
        alpha=0.1,
    )
    ax[AX_V][AX_H].add_artist(ellipse1)
    ellipse2 = Ellipse(
        xy=(out_df.loc[ii, "X_el"], out_df.loc[ii, "Y_el"]),
        width=abs(out_df.loc[ii, "SdNE_el"]) * S_EL,
        height=abs(out_df.loc[ii, "SdNE_el"]) * S_EL,
        facecolor="k",
        alpha=0.3,
    )
    ax[AX_V][AX_H].add_artist(ellipse2)

ax[AX_V][AX_H].set_xlim(np.nanmean(out_df["X_el"]) - 5, np.nanmean(out_df["X_el"]) + 5)
ax[AX_V][AX_H].set_ylim(np.nanmean(out_df["Y_el"]) - 7, np.nanmean(out_df["Y_el"]) + 3)
ax[AX_V][AX_H].text(
    0.1, 0.93, f'MG ellipse {S_MG:.0f}x"', transform=ax[AX_V][AX_H].transAxes
)
ax[AX_V][AX_H].text(
    0.1, 0.83, f'MG ellipse {S_EL:.0f}x"', transform=ax[AX_V][AX_H].transAxes
)
ax[AX_V][AX_H].set_xlabel("UTM N (m)")
ax[AX_V][AX_H].set_ylabel("UTM E (m)")

AX_V, AX_H = 1, 1
ax[AX_V][AX_H].set_title("HDOP / SdNE")

ax[AX_V][AX_H].plot(out_df["DistOrigin_mg"], out_df["HDOP_mg"], color="k")
for QF in out_df.QualityFix_el.unique():
    ax[AX_V][AX_H].scatter(
        out_df.loc[out_df["QualityFix_el"] == QF, "DistOrigin_el"],
        out_df.loc[out_df["QualityFix_el"] == QF, "SdNE_el"].abs(),
        color=qf_color[QF],
        marker="+",
        label="PPK reachm2 (" + qf_label[QF] + ")",
    )

lr = linregress(out_df["DistOrigin_el"], out_df["DistOrigin_mg"])

ax[AX_V][AX_H].set_xlabel("Distance from origin (m)")
ax[AX_V][AX_H].set_ylabel("Error (m)")
ax[AX_V][AX_H].set_ylim(-0.1, 1)

AX_V, AX_H = 1, 2
ax[AX_V][AX_H].set_title("Location Error")
ax[AX_V][AX_H].plot(
    out_df["DistOrigin_el"], out_df["DistOrigin_mg"], color="k", marker="+"
)
ax[AX_V][AX_H].text(
    0.1, 0.9, str("$R^2=%.2f$" % lr[2]), transform=ax[AX_V][AX_H].transAxes
)
ax[AX_V][AX_H].set_title("Distance from origin")
ax[AX_V][AX_H].set_xlabel("PPK reachm2")
ax[AX_V][AX_H].set_ylabel("MagnaProbe")

# create boxplot with a different y scale for different rows
labels = ["Fix", "Float", "Single"]
var = ["SdNE_el", "SdU_el"]
groups = out_df.groupby("QualityFix_el")
AX_V = 2
AX_H = 0
for ID, group in groups:
    bplot = ax[AX_V][AX_H].boxplot(
        group[var].abs(), labels=[v[:-3] for v in var], patch_artist=True
    )
    ax[AX_V][AX_H].set_xlabel(labels[AX_H])
    scale = [5, 4, 3, 2, 1.25, 1]
    for ii, n in enumerate(scale):
        df = group[var].abs() > group[var].abs().median().max() * n
        if any(df.sum() > 0):
            if ii == 0:
                n = scale[ii]
            else:
                n = scale[ii - 1]
            print(ID, n)
            break
    ax[AX_V][AX_H].set_ylim(
        group[var].abs().min().min() * 0.85, group[var].abs().median().max() * n
    )

    df = group[var].abs() > group[var].abs().median().max() * n

    P = len(group[var]) / len(out_df) * 100
    ax[AX_V][AX_H].text(0.1, 0.8, f"P: {P:.1f}%", transform=ax[AX_V][AX_H].transAxes)

    group[var]
    for ii, _var in enumerate(var):
        if df.sum()[_var] > 0:
            ax[AX_V][AX_H].text(
                (1 + ii) * 0.33, 0.95, "^", transform=ax[AX_V][AX_H].transAxes
            )
            ax[AX_V][AX_H].text(
                (1 + ii) * 0.33,
                0.925,
                df.sum()[_var],
                transform=ax[AX_V][AX_H].transAxes,
            )

    # fill with colors
    colors = ["lightgreen", "bisque", "lightcoral"]
    for patch, color in zip(bplot["boxes"], colors):
        patch.set_facecolor(color)

    if AX_H == 0:
        ax[AX_V][AX_H].set_ylabel("Location Uncertainty (m)")
    elif AX_H == 1:
        ax[AX_V][AX_H].set_title("Emlid GPS Location Precision")
    else:
        ax[AX_V][AX_H].set_ylabel("")
    AX_H += 1
fig.suptitle("Emlid/Magnaprobe GPS comparison", fontweight="bold")
plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.05, wspace=0.4, hspace=0.3)
plt.show()

# save fig
fig_fn = os.path.basename(MAGNA_FP).split(".")[0] + "-gps.pdf"
fig_fp = os.path.join(output_dir, fig_fn)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
out_df.to_csv(fig_fp, index=False)
fig.savefig(fig_fp)

# Write out new file

output_fn = os.path.basename(MAGNA_FP).split(".")[0] + ".b0.csv"
output_fp = os.path.join(output_dir, output_fn)
print("Writing out: ", output_fp)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
out_df.to_csv(output_fp, index=False)


## Data

# Create figure framework
w_fig, h_fig = 8, 11
ncols, nrows = 3, 3
fig = plt.figure(figsize=[w_fig, h_fig])
gs1 = gridspec.GridSpec(
    nrows, ncols, height_ratios=[1] * nrows, width_ratios=[1] * ncols
)
ax = [
    [fig.add_subplot(gs1[0, :]), None, None],
    [
        fig.add_subplot(gs1[1, :]),
        None,
        None,
    ],
    [
        fig.add_subplot(gs1[2, :]),
        None,
        None,
    ],
]

AX_V, AX_H = 0, 0

ax[AX_V][AX_H].set_title("GPS location")
# out_df['Smoothed Altitude'] = out_df['Altitude_el'].rolling(window=5, min_periods=1).mean()

ax[AX_V][AX_H].set_title("Elevation")
ax[AX_V][AX_H].set_xlabel("Transect distance (m)")
ax[AX_V][AX_H].set_ylabel("Elevation (m)", color="black")
ax[AX_V][AX_H].plot(
    out_df["LineLocation_mg"], out_df["Altitude_el"], color="black", label="GPS Height"
)
ax[AX_V][AX_H].fill_between(
    out_df["LineLocation_mg"],
    out_df["Altitude_el"] - 3 * out_df["SdU_el"],
    out_df["Altitude_el"] + 3 * out_df["SdU_el"],
    color="grey",
    alpha=0.5,
    label="Uncertainty",
)
ax[AX_V][AX_H].tick_params(axis="y", labelcolor="black")
ax[AX_V][AX_H].legend(loc="upper left")
ax2 = ax[AX_V][AX_H].twinx()
ax2.set_ylabel("Depth (cm)", color="blue")
ax2.plot(
    out_df["LineLocation_mg"],
    out_df["SnowDepth_mg"],
    color="red",
    label="MagnaProbe Depth (cm)",
)
ax2.tick_params(axis="y", labelcolor="blue")
ax2.legend(loc="upper right")

# Plot fix quality at bottom
out_df["diff"] = out_df["LineLocation_mg"].diff() / 2

for ii in range(len(out_df) - 1):
    x_start = out_df["LineLocation_mg"].iloc[ii] - out_df["diff"].iloc[ii + 1]
    x_end = out_df["LineLocation_mg"].iloc[ii] + out_df["diff"].iloc[ii + 1] - 0.1
    ax[AX_V][AX_H].axvspan(
        x_start,
        x_end,
        ymin=0,
        ymax=0.05,
        color=qf_color[out_df["QualityFix_el"].iloc[ii]],
        alpha=0.3,
    )

ax[AX_V][AX_H].grid(True)

# Position comparison
AX_V, AX_H = 1, 0
ax[AX_V][AX_H].set_title("Linear location")
ax[AX_V][AX_H].set_xlabel("Transect distance (m)")
ax[AX_V][AX_H].set_xlabel("Distance from origin (m)")
ax[AX_V][AX_H].plot(
    out_df["LineLocation_mg"],
    out_df["DistOrigin_el"],
    label="Corrected location",
    color="blue",
    marker="+",
    linestyle="",
)
# ax[AX_V][AX_H].plot(out_df['LineLocation_mg'], out_df['DistOrigin_mg'], label='Magnaprobe', color='k', marker='x', linestyle='')

ax2 = ax[AX_V][AX_H].twinx()
ax2.set_ylabel("Distance difference (m)", color="blue")
ax2.plot(
    out_df["LineLocation_mg"],
    out_df["DistOrigin_el"] - out_df["LineLocation_mg"],
    color="red",
    label="Reach",
)
ax2.plot(
    out_df["LineLocation_mg"],
    out_df["DistOrigin_mg"] - out_df["LineLocation_mg"],
    color="black",
    label="MagnaProbe",
)
ax2.tick_params(axis="y", labelcolor="black")
ax2.legend(loc="upper right")

for ii in range(len(out_df) - 1):
    x_start = out_df["LineLocation_mg"].iloc[ii] - out_df["diff"].iloc[ii + 1]
    x_end = out_df["LineLocation_mg"].iloc[ii] + out_df["diff"].iloc[ii + 1] - 0.1
    ax[AX_V][AX_H].axvspan(
        x_start,
        x_end,
        ymin=0,
        ymax=0.05,
        color=qf_color[out_df["QualityFix_el"].iloc[ii]],
        alpha=0.3,
    )
plt.show()
