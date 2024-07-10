import logging

import os

import matplotlib.pyplot as plt
from matplotlib import gridspec

import magnaprobe_toolbox as mt

import numpy as np


QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-ARM/salvo_arm_line-ice_magnaprobe-geodel_20240529.a3.csv"

ARM_FP = "/mnt/data/UAF-data/working_a/SALVO/20240529-ARM/salvo_arm_line_magnaprobe-geodel_20240529.a3.csv"

# Load qc-ed data
qc_data = mt.load.qc_data(QC_FP)
qc_arm = mt.load.qc_data(ARM_FP)
qc_data = qc_data.sort_values(["LineLocation", "DepthType"])
qc_ice = (
    qc_data.loc[qc_data.DepthType == "ice"]
    .set_index("LineLocation", drop=True)
    .sort_index()
)
qc_snow = (
    qc_data.loc[qc_data.DepthType == "bot"]
    .set_index("LineLocation", drop=True)
    .sort_index()
)
qc_ice = qc_ice.reindex(range(qc_ice.index[0], 200), fill_value=np.nan)
qc_snow = qc_snow.reindex(range(qc_snow.index[0], 200), fill_value=np.nan)

# Define figure subplots
FIG_TITLE = NCOLS = 1
NROWS = 3

# colors = cm.davos(np.linspace(0, 1, len(fn_dict.keys())+1))
# colort = colors.copy()
# for ii in range(len(colors)):
#     colort[ii][3] = 0.25
w_fig, h_fig = 7, 11
fig = plt.figure(figsize=[w_fig, h_fig])
gs1 = gridspec.GridSpec(
    NROWS, NCOLS, height_ratios=[1] * NROWS, width_ratios=[1] * NCOLS
)
ax = [
    [fig.add_subplot(gs1[0, 0]), fig.add_subplot(gs1[1, 0]), fig.add_subplot(gs1[2, 0])]
]

AX_X, AX_Y = 0, 0
ax[AX_X][AX_Y].scatter(
    qc_snow.index,
    qc_snow.SnowDepth,
    color="steelblue",
    label="Snow Depth",
    linewidth=1,
    marker="x",
)
ax[AX_X][AX_Y].scatter(
    qc_ice.index,
    qc_ice.SnowDepth,
    color="red",
    label="Ice Depth",
    linewidth=1,
    marker="x",
)
ax[AX_X][AX_Y].set_xlabel("Distance along the transect (m)")
ax[AX_X][AX_Y].set_ylabel("Snow Depth (m)")
ax[AX_X][AX_Y].legend(loc="upper right")
ax[AX_X][AX_Y].plot(qc_arm.LineLocation, qc_arm.SnowDepth, color="k")
ax[AX_X][AX_Y].set_xlim([0, 200])

AX_X, AX_Y = 0, 1
ax[AX_X][AX_Y].scatter(
    qc_data.loc[qc_data.DepthType == "bot"].SnowDepth,
    qc_data.loc[qc_data.DepthType == "ice"].SnowDepth,
    color="steelblue",
    label="Snow Depth",
    linewidth=1,
    marker="x",
)
ax[AX_X][AX_Y].plot(
    [0, 0], [0.6, 0.6], color="steelblue", label="Snow Depth", linewidth=1, marker="x"
)

ax[AX_X][AX_Y].set_xlim([0, 0.6])
ax[AX_X][AX_Y].set_ylim([0, 0.3])

AX_X, AX_Y = 0, 2
ax[AX_X][AX_Y].plot(
    qc_snow.index,
    qc_snow.SnowDepth - qc_ice.SnowDepth,
    color="steelblue",
    label="Snow Depth",
    linewidth=1,
    marker="x",
)

plt.show()
