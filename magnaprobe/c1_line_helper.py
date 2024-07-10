import logging

import matplotlib.pyplot as plt
from matplotlib import gridspec

import numpy as np

import magnaprobe_toolbox as mt


logger = logging.getLogger(__name__)


QC_BASE = "/mnt/data/UAF-data/working_a/SALVO/20240419-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240419.a3.csv"
QC_DATA = "/mnt/data/UAF-data/working_a/SALVO/20240522-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240522.a2.csv"
out_fp = "/mnt/data/UAF-data/working_a/SALVO/20240522-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240522.a3.csv"

# Load qc-ed data
base_df = mt.load.qc_data(QC_BASE)
data_df = mt.load.qc_data(QC_DATA)

# Check
data_df = mt.analysis.distance.compute(data_df)
data_df = mt.tools.all_check(data_df, direction="EW")
data_df = data_df.reset_index(drop=True)

# CHECK
data_df["QC_dist"] = None
data_df["QC_freq"] = None

# Too short spatial difference
d_median = data_df["TrackDist"].median()
data_df.loc[data_df["TrackDist"] < 0.5, "QC_dist"] = 9
data_df.loc[1.8 < data_df["TrackDist"], "QC_dist"] = 8

# Sampling frequency
sampling_interval = data_df.Timestamp.diff().median()
# Thrice time below median sampling frequency
data_df.loc[sampling_interval * 3 < data_df.Timestamp.diff(), "QC_freq"] = 9
# At least twice below median sampling frequency
data_df.loc[data_df.Timestamp.diff() < sampling_interval / 2, "QC_freq"] = 9

data_df.to_csv(out_fp)

w_fig, h_fig = 8, 11
nrows, ncols = 1, 1
fig = plt.figure(figsize=[w_fig, h_fig])
gs1 = gridspec.GridSpec(
    nrows, ncols, height_ratios=[1] * nrows, width_ratios=[1] * ncols
)
ax = [[fig.add_subplot(gs1[0, 0])]]

AX_X, AX_Y = 0, 0

shift = np.sign(len(base_df) - len(data_df))


ax[AX_X][AX_Y].plot(
    base_df["LineLocation"], base_df["SnowDepth"], color="black", label="20240522-ARM"
)
ax[AX_X][AX_Y].plot(
    data_df.index,
    data_df["SnowDepth"],
    color="black",
    label=f"20240522-ARM",
    alpha=0.5,
    linewidth=0.75,
)

for ii in range(1, abs(len(base_df) - len(data_df)) + 1):
    shift = np.sign(len(base_df) - len(data_df)) * ii
    if shift == (len(base_df) - len(data_df)):
        ax[AX_X][AX_Y].plot(
            data_df.index + shift,
            data_df["SnowDepth"],
            color="blue",
            label=f"20240522-ARM + {abs(shift)} m",
            alpha=1,
            linewidth=0.75,
            zorder=3,
        )
    else:
        ax[AX_X][AX_Y].plot(
            data_df.index + shift,
            data_df["SnowDepth"],
            color="blue",
            label=f"20240522-ARM + {abs(shift)} m",
            alpha=0.5,
            linewidth=0.75,
        )

ax[AX_X][AX_Y].scatter(
    data_df.loc[data_df.QC_dist == 8].index + shift,
    data_df.loc[data_df.QC_dist == 8]["SnowDepth"],
    marker="o",
    edgecolors="red",
    facecolors="white",
    alpha=1,
    label="long step",
    zorder=2,
)
ax[AX_X][AX_Y].scatter(
    data_df.loc[data_df.QC_freq == 9].index + shift,
    data_df.loc[data_df.QC_freq == 9]["SnowDepth"],
    marker="x",
    alpha=1,
    color="red",
    label="3 above median frequency",
    zorder=2,
)

plt.legend()
plt.savefig(
    "/mnt/data/UAF-data/working_a/SALVO/20240522-ARM/magnaprobe/salvo_arm_line_magnaprobe-geodel_20240522.a2.pdf"
)
plt.show()
