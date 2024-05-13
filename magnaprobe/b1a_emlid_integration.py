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

import pandas as pd
from matplotlib import gridspec
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
import yaml
from salvo.analysis import distance

# Filepath to data
MAGNA_FP = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240420.a3.csv"
EMLID_FP = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/emlid/salvo_BEO_line-longline_emlid-location_20240420.a2.pos"

# Perform GPS comparison analysis, and display figure
DISPLAY = True

# b-grade products are generated in 'working_b' directory
output_dir = os.path.dirname(MAGNA_FP).replace("working_a", "working_b")

# load config file
config = {}
for file in os.listdir(os.path.dirname(MAGNA_FP)):
    if file.endswith("yaml"):
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

utc_starttime = pd.to_datetime(config["magna"]["starttime"]) - timedelta(0, 60)
utc_endtime = pd.to_datetime(config["magna"]["endtime"]) + timedelta(0, 60)

# Load position file
print("Loading: ", EMLID_FP)
pos_df = pd.read_csv(EMLID_FP, header=0)
pos_df["Timestamp"] = pd.to_datetime(pos_df["Timestamp"], format="ISO8601")
pos_freq = pos_df["Timestamp"].diff().median()

pos_df["Timestamp"] = pos_df["Timestamp"].apply(lambda x: x.round(pos_freq))

# Append '_el' to all columns headers from position file, but Timestamp
columns_dict = {col: col + "_el" for col in pos_df.columns if col not in ["Timestamp"]}
pos_df.rename(columns=columns_dict, inplace=True)

# Load data file
print("Loading: ", MAGNA_FP)
magna_df = pd.read_csv(MAGNA_FP, header=0)
# Convert magna to UTC
timezone = float(config["magna"]["timezone"].split("UTC")[-1])
magna_df["Timestamp"] = pd.to_datetime(
    magna_df["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f"
) - timedelta(hours=timezone)
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
ax = np.array(ax)

AX_V, AX_H = 0, 0
ax[AX_V, AX_H].set_title("GPS location")
# ax[ax_v, ax_h].scatter(out_df['Latitude_mg'], out_df['Longitude_mg'], color='k', marker='x', label='Magnaprobe')
# ax[ax_v, ax_h].scatter(out_df.loc[out_df['FixQuality_el']==1, 'Latitude_el'], out_df.loc[out_df['FixQuality_el'] == 1, 'Longitude_el'],
#                        color='green', marker='+', label='PPK reachm2 (Fix)')
# ax[ax_v, ax_h].scatter(out_df.loc[out_df['FixQuality_el']==2, 'Latitude_el'], out_df.loc[out_df['FixQuality_el'] == 2, 'Longitude_el'],
#                        color='orange', marker='+', label='PPK reachm2 (Float)')
# ax[ax_v, ax_h].scatter(out_df.loc[out_df['FixQuality_el']==5, 'Latitude_el'], out_df.loc[out_df['FixQuality_el'] == 5, 'Longitude_el'],
#                        color='red', marker='+', label='PPK reachm2 (Single)')

ax[AX_V, AX_H].scatter(
    out_df["X_mg"], out_df["Y_mg"], color="k", marker="x", label="Magnaprobe"
)
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 1, "X_el"],
    out_df.loc[out_df["FixQuality_el"] == 1, "Y_el"],
    color="green",
    marker="+",
    label="PPK reachm2 (Fix)",
)
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 2, "X_el"],
    out_df.loc[out_df["FixQuality_el"] == 2, "Y_el"],
    color="orange",
    marker="+",
    label="PPK reachm2 (Float)",
)
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 5, "X_el"],
    out_df.loc[out_df["FixQuality_el"] == 5, "Y_el"],
    color="red",
    marker="+",
    label="PPK reachm2 (Single)",
)
ax[AX_V, AX_H].legend(fancybox=False)
ax[AX_V, AX_H].set_xlabel("UTM N (m)")
ax[AX_V, AX_H].set_ylabel("UTM E (m)")

AX_V, AX_H = 1, 0
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 1, "X_el"],
    out_df.loc[out_df["FixQuality_el"] == 1, "Y_el"],
    color="green",
    marker="+",
    label="PPK reachm2 (Fix)",
)
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 2, "X_el"],
    out_df.loc[out_df["FixQuality_el"] == 2, "Y_el"],
    color="orange",
    marker="+",
    label="PPK reachm2 (Float)",
)
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 5, "X_el"],
    out_df.loc[out_df["FixQuality_el"] == 5, "Y_el"],
    color="red",
    marker="+",
    label="PPK reachm2 (Single)",
)
ax[AX_V, AX_H].scatter(out_df["X_mg"], out_df["Y_mg"], color="k", marker="x")
S_EL = 100  # scale factor for the emlid sigmaNE ellipse
S_MG = 10  # scale factor for the magnaprobe HDOP ellipse
for ii in out_df.index:
    ellipse1 = Ellipse(
        xy=([out_df.loc[ii, "X_mg"], out_df.loc[ii, "Y_mg"]]),
        width=out_df.loc[ii, "HDOP_mg"] * S_MG,
        height=out_df.loc[ii, "HDOP_mg"] * S_MG,
        facecolor="k",
        alpha=0.1,
    )
    ax[AX_V, AX_H].add_artist(ellipse1)
    ellipse2 = Ellipse(
        xy=(out_df.loc[ii, "X_el"], out_df.loc[ii, "Y_el"]),
        width=abs(out_df.loc[ii, "StdNE_el"]) * S_EL,
        height=abs(out_df.loc[ii, "StdNE_el"]) * S_EL,
        facecolor="r",
        alpha=0.3,
    )
    ax[AX_V, AX_H].add_artist(ellipse2)

ax[AX_V, AX_H].set_xlim(np.nanmean(out_df["X_el"]) - 5, np.nanmean(out_df["X_el"]) + 5)
ax[AX_V, AX_H].set_ylim(np.nanmean(out_df["Y_el"]) - 7, np.nanmean(out_df["Y_el"]) + 3)
ax[AX_V, AX_H].text(
    0.1, 0.93, str("MG ellipse ", S_MG, "x"), transform=ax[AX_V, AX_H].transAxes
)
ax[AX_V, AX_H].text(
    0.1, 0.83, str("PPK ellipse ", S_EL, "x"), transform=ax[AX_V, AX_H].transAxes
)
ax[AX_V, AX_H].set_xlabel("UTM N (m)")
ax[AX_V, AX_H].set_ylabel("UTM E (m)")

AX_V, AX_H = 1, 1
ax[AX_V, AX_H].set_title("HDOP / StdNE")
ax[AX_V, AX_H].plot(out_df["DistOrigin_mg"], out_df["HDOP_mg"], color="k")
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 1, "DistOrigin_el"],
    out_df.loc[out_df["FixQuality_el"] == 1, "StdNE_el"].abs(),
    color="green",
    marker="+",
    label="PPK reachm2 (Fix)",
)
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 2, "DistOrigin_el"],
    out_df.loc[out_df["FixQuality_el"] == 2, "StdNE_el"].abs(),
    color="orange",
    marker="+",
    label="PPK reachm2 (Float)",
)
ax[AX_V, AX_H].scatter(
    out_df.loc[out_df["FixQuality_el"] == 5, "DistOrigin_el"],
    out_df.loc[out_df["FixQuality_el"] == 5, "StdNE_el"].abs(),
    color="red",
    marker="+",
    label="PPK reachm2 (Single)",
)
ax[AX_V, AX_H].set_xlabel("Distance from origin (m)")
ax[AX_V, AX_H].set_ylabel("Error (m)")
ax[AX_V, AX_H].set_ylim(-0.1, 1)

AX_V, AX_H = 1, 2
ax[AX_V, AX_H].set_title("Location Error")
ax[AX_V, AX_H].plot(
    out_df["DistOrigin_el"], out_df["DistOrigin_mg"], color="k", marker="+"
)
ax[AX_V, AX_H].set_title("Distance from origin")
ax[AX_V, AX_H].set_xlabel("PPK reachm2")
ax[AX_V, AX_H].set_ylabel("MagnaProbe")

# create boxplot with a different y scale for different rows
labels = ["Fix", "Float", "Single"]
var = ["StdNE_el", "StdU_el"]
groups = out_df.groupby("FixQuality_el")
AX_V = 2
AX_H = 0
for ID, group in groups:
    bplot = ax[AX_V, AX_H].boxplot(
        group[var].abs(), labels=[v[:-3] for v in var], patch_artist=True
    )
    ax[AX_V, AX_H].set_xlabel(labels[AX_H])
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
    ax[AX_V, AX_H].set_ylim(
        group[var].abs().min().min() * 0.85, group[var].abs().median().max() * n
    )

    df = group[var].abs() > group[var].abs().median().max() * n

    for ii, _var in enumerate(var):
        if df.sum()[_var] > 0:
            ax[AX_V, AX_H].text(
                (1 + ii) * 0.25, 0.95, "^", transform=ax[AX_V, AX_H].transAxes
            )
            ax[AX_V, AX_H].text(
                (1 + ii) * 0.25,
                0.925,
                df.sum()[_var],
                transform=ax[AX_V, AX_H].transAxes,
            )

    # fill with colors
    colors = ["lightgreen", "bisque", "lightcoral"]
    for patch, color in zip(bplot["boxes"], colors):
        patch.set_facecolor(color)

    if AX_H == 0:
        ax[AX_V, AX_H].set_ylabel("Location Uncertainty (m)")
    elif AX_H == 1:
        ax[AX_V, AX_H].set_title("Emlid GPS Location Precision")
    else:
        ax[AX_V, AX_H].set_ylabel("")
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
##Write out new file

output_fn = os.path.basename(MAGNA_FP).split(".")[0] + ".b0.csv"
output_fp = os.path.join(output_dir, output_fn)
print("Writing out: ", output_fp)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
out_df.to_csv(output_fp, index=False)

#
#
#
# ax[0, 0].plot(outDF['DistOrigin_y'], outDF['Z_y'])
#
# ax[0, 0].plot(outDF.loc[outDF.Q == 1, 'DistOrigin_y'], outDF.loc[outDF.Q == 1, 'Z_y'], color='green', marker='o', linestyle='')
# ax[0, 0].plot(outDF.loc[outDF.Q == 5, 'DistOrigin_y'], outDF.loc[outDF.Q == 5, 'Z_y'], color='red', marker='x', linestyle='')
#
# #ax[0, 0].set_ylim([0, 10])
# ax[1, 0].plot(ppk_pos_df.loc[ppk_pos_df.Q < 5, 'DistOrigin'], ppk_pos_df.loc[ppk_pos_df.Q < 5, 'Z'], 'k', alpha=0.6)
# ax[1, 0].plot(ppk_pos_df.loc[ppk_pos_df.Q == 1, 'DistOrigin'], ppk_pos_df.loc[ppk_pos_df.Q == 1, 'Z'], markeredgecolor='green', markerfacecolor=[0,0,0,0], marker='o', linestyle='')
# ax[1, 0].plot(ppk_pos_df.loc[ppk_pos_df.Q == 5, 'DistOrigin'], ppk_pos_df.loc[ppk_pos_df.Q == 5, 'Z'], markeredgecolor='red', marker='x', linestyle='', alpha=0.5)
#
# #ax[1, 0].set_ylim([0, 10])
# ax[0, 0].set_xlabel('Distance (m)')
# ax[0, 0].set_xlabel('Elevation (m)')
# ax[2, 0].plot(outDF['X_y'], outDF['Y_y'], 'ro')
# ax[2, 0].plot(outDF['X_x'], outDF['Y_x'], 'xk')
# ax[3, 0].plot(outDF['DistOrigin_y'], outDF['DistOrigin_x'])
# ax[3, 0].plot(outDF.loc[outDF.Q == 5, 'DistOrigin_y'], outDF.loc[outDF.Q == 5, 'DistOrigin_x'], markeredgecolor='red', marker='x', linestyle='', alpha=0.5)
# ax[3, 0].plot(outDF.loc[outDF.Q == 1, 'DistOrigin_y'], outDF.loc[outDF.Q == 1, 'DistOrigin_x'], markeredgecolor='green', marker='o', linestyle='', alpha=0.5)
#
# ax[3, 0].set_xlabel('Distance (m), emlid')
# ax[3, 0].set_xlabel('Distance (m), magna')
#
# plt.show()
