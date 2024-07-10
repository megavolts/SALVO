import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
import cmcrameri as cm

data_fp = (
    "/mnt/data/UAF-data/raw/SALVO/20240530-ICE/icecore/20240526-quick_salinity.csv"
)
# data_fp = '/mnt/data/UAF-data/raw/SALVO/20240607-ICE/icecore/20240607-quick_salinity.csv'

data_df = pd.read_csv(data_fp)


colors = {"D": "b", "T": "g", "S": "r"}


w_fig, h_fig = 11, 8
nrows, ncols = 1, 2
fig = plt.figure(figsize=[w_fig, h_fig])
gs1 = gridspec.GridSpec(
    nrows, ncols, height_ratios=[1] * nrows, width_ratios=[1] * ncols
)
ax = [[fig.add_subplot(gs1[0, 0]), fig.add_subplot(gs1[0, 1])]]

AX_X, AX_Y = 0, 0
ax[AX_X][AX_Y].set_xlabel("Salinity (°C)")
ax[AX_X][AX_Y].set_ylabel("Ice thickness (m)")
for core in data_df.core.unique():
    if "S_" in core[:2]:
        print(core)
        X = data_df.loc[data_df.core == core, "salinity"]
        X = np.repeat(X, 2)
        Y1 = data_df.loc[data_df.core == core, "d1"]
        Y2 = data_df.loc[data_df.core == core, "d2"]
        Y = pd.concat([Y1, Y2]).sort_values()

        # create step:
        ax[AX_X][AX_Y].plot(X, Y, label=core, color=colors[core[2]])
        #        ax[AX_X][AX_Y].plot(X, Y, label=core)

ax[AX_X][AX_Y].legend(loc="lower left")
ax[AX_X][AX_Y].invert_yaxis()
ax[AX_X][AX_Y].xaxis.set_label_position("top")
ax[AX_X][AX_Y].xaxis.set_ticks_position("top")
ax[AX_X][AX_Y].yaxis.set_label_position("left")
ax[AX_X][AX_Y].yaxis.set_ticks_position("left")
ax[AX_X][AX_Y].yaxis.set_ticks_position("left")
ax[AX_X][AX_Y].spines["bottom"].set_visible(False)
ax[AX_X][AX_Y].spines["right"].set_visible(False)

ax[AX_X][AX_Y].set_xlim([0, 9])
ax[AX_X][AX_Y].set_ylim([1.5, -0.5])

AX_X, AX_Y = 0, 1
xlim = [-4, 1]
ylim = [1.5, -0.6]
ax[AX_X][AX_Y].set_xlabel("Temperature (°C)")
ax[AX_X][AX_Y].set_ylabel("Ice thickness (m)")
for core in data_df.core.unique():
    if "T_" in core[:2]:
        print(core)
        XY = data_df.loc[data_df.core == core, ["dm", "temperature", "comment"]]
        p = ax[AX_X][AX_Y].plot(
            XY.loc[XY.dm >= 0, "temperature"][:-1],
            XY.loc[XY.dm >= 0, "dm"][:-1],
            label=core,
        )
        c = p[0].get_color()

        # snow temperature
        ax[AX_X][AX_Y].plot(
            XY.loc[(XY.comment.str.contains("snow")) | (XY.dm == 0), "temperature"],
            XY.loc[(XY.comment.str.contains("snow")) | (XY.dm == 0), "dm"],
            color=c,
            linestyle="--",
        )

        # snow temperature
        ax[AX_X][AX_Y].plot(
            XY.loc[
                (XY.comment.str.contains("snow")) | (XY.comment.str.contains("air")),
                "temperature",
            ],
            XY.loc[
                (XY.comment.str.contains("snow")) | (XY.comment.str.contains("air")),
                "dm",
            ],
            color=c,
            linestyle=":",
        )

        h_snow = [-XY.loc[XY.comment == "snow surface"]["dm"].values]


ax[AX_X][AX_Y].plot(
    xlim, [0] * 2, label="snow surface, " + core, color="grey", linestyle="--"
)


ax[AX_X][AX_Y].legend(loc="lower right")
ax[AX_X][AX_Y].xaxis.set_label_position("top")
ax[AX_X][AX_Y].xaxis.set_ticks_position("top")
ax[AX_X][AX_Y].yaxis.set_label_position("right")
ax[AX_X][AX_Y].yaxis.set_ticks_position("right")
ax[AX_X][AX_Y].spines["bottom"].set_visible(False)
ax[AX_X][AX_Y].spines["left"].set_visible(False)

ax[AX_X][AX_Y].set_xlim(xlim)
ax[AX_X][AX_Y].set_ylim(ylim)
plt.savefig(data_fp.replace(".csv", ".pdf"))
plt.show()
