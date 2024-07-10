import os
import numpy as np

import magnaprobe_toolbox as mt
import matplotlib.pyplot as plt

import matplotlib.tri as tri

# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240606-ARM/magnaprobe/salvo_arm_sg27_magnaprobe-geodel_20240606.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_library-20240602b_magnaprobe-geodel_20240602.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240602-BEO/magnaprobe/salvo_beo_library-20240602a_magnaprobe-geodel_20240602.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240604-ARM/magnaprobe/salvo_arm_library-20240604a_magnaprobe-geodel_20240604.a2.csv"
# QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240607-ICE/magnaprobe/salvo_ice_library_magnaprobe-geodel_20240607.a2.dat"
QC_FP = "/mnt/data/UAF-data/working_a/SALVO/20240607-ICE/magnaprobe/salvo_ice_library_magnaprobe-geodel_20240607.a2.csv"
out_fn = os.path.basename(QC_FP).split(".")[0]
out_fp = os.path.dirname(QC_FP)

# Load qc-ed data
qc_data = mt.load.qc_data(QC_FP)

# Load config:
config = mt.io.config.load(QC_FP)

# Compute distance after file sanitation
qc_data = mt.analysis.distance.compute(qc_data)

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
cntr1 = ax1.contour(
    xi, yi, zi, levels=np.arange(0, 1.3, 0.1), linewidths=0.5, colors="k", alpha=0.5
)
cntr1 = ax1.contourf(xi, yi, zi, levels=np.arange(0, 0.5, 0.05), cmap="Blues")

cbar = fig.colorbar(cntr1, ax=ax1)
cbar.set_label("Snow Depth (m)")

ax1.plot(x, y, "k+", ms=1, alpha=0.5)
ax1.axis("equal")
ax1.set_xlabel("Easting (m)")
ax1.set_ylabel("Northing (m)")
plt.savefig(os.path.join(out_fp, out_fn + ".pdf"))
plt.show()
#
# qc_data.loc[(qc_data.X0 > 0) & (qc_data.Y0 < 0), 'SnowDepth'].mean()
# qc_data.loc[(qc_data.X0 > 0) & (qc_data.Y0 < 0), 'SnowDepth'].std()
