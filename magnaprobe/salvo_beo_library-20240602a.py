import pandas as pd

import os
import numpy as np

import magnaprobe_toolbox as mt
import matplotlib.pyplot as plt

import matplotlib.tri as tri

# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240606-ARM/magnaprobe/salvo_arm_sg27_magnaprobe-geodel_20240606.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_library-20240602b_magnaprobe-geodel_20240602.a2.csv"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_library-20240602a_magnaprobe-geodel_20240602.a2.csv"
POS_FP = "/mnt/data/UAF-data/raw/SALVO/20240602-BEO/emlid/salvo_beo_library-20240602a_emlid-r2_20240602.csv"

out_fn = os.path.basename(QC_FP).split(".")[0]
out_fp = os.path.dirname(QC_FP)

# Load qc-ed data
qc_data = mt.load.qc_data(QC_FP)

# Load config:
config = mt.io.config.load(QC_FP)

# Compute distance after file sanitation
qc_data = mt.analysis.distance.compute(qc_data)

pos_df = pd.read_csv(POS_FP)

LOCAL_EPSG = 3338
import pyproj

xform = pyproj.Transformer.from_crs("4326", LOCAL_EPSG)
pos_df[["X", "Y"]] = pd.DataFrame(
    xform.transform(pos_df["Latitude"], pos_df["Longitude"])
).transpose()
pos_df["Z"] = pos_df["Elevation"]


# SG27
if "sg27" in QC_FP:
    xLon = 85.5
    xLat = 60
else:
    xLon = 0
    xLat = 0

# Zero to origin
qc_data["X0"] = qc_data["X"] - qc_data["X"].min() - xLon
qc_data["Y0"] = qc_data["Y"] - qc_data["Y"].min() - xLat

pos_df["X0"] = pos_df["X"] - qc_data["X"].min()
pos_df["Y0"] = pos_df["Y"] - qc_data["Y"].min()

xmin, xmax = qc_data["X0"].min(), qc_data["X0"].max()
ymin, ymax = qc_data["Y0"].min(), qc_data["Y0"].max()

x = qc_data["X0"]
y = qc_data["Y0"]
z = qc_data["SnowDepth"]
z.loc[z < 0] = 0
# Create grid values
dx = 0.25
dy = 0.25

xi = np.arange(xmin, xmax + dx / 2, dx)
yi = np.arange(ymin, ymax + dy / 2, dy)

npts = len(z)
ngridx = len(xi)
ngridy = len(yi)
# Linearly interpolate the data (x, y) on a grid defined by (xi, yi).
triang = tri.Triangulation(x, y)
interpolator = tri.LinearTriInterpolator(triang, z)
Xi, Yi = np.meshgrid(xi, yi)
zi = interpolator(Xi, Yi)

fig, (ax1) = plt.subplots(nrows=1)
ax1.contour(
    xi, yi, zi, levels=np.arange(0, 1.3, 0.1), linewidths=0.5, colors="k", alpha=0.5
)
cntr1 = ax1.contourf(xi, yi, zi, levels=30, cmap="Blues")


fig.colorbar(cntr1, ax=ax1)
ax1.plot(x, y, "k+", ms=1, alpha=0.5)
ax1.axis("equal")
ax1.plot(pos_df["X0"], pos_df["Y0"], "ro", ms=3)
plt.savefig(os.path.join(out_fp, out_fn + ".pdf"))
plt.show()
#
# qc_data.loc[(qc_data.X0 > 0) & (qc_data.Y0 < 0), 'SnowDepth'].mean()
# qc_data.loc[(qc_data.X0 > 0) & (qc_data.Y0 < 0), 'SnowDepth'].std()
