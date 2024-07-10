# -*- coding: utf-8 -*-
"""
Integrate location from PPK corrected .pos file from EmlidStudio with the Magnapobe qc-ed data.

Inputs:
    QC-ed MagnaProbe data in a comma-separated variable (.csv) file
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
    For some reason despite sometimes the Campbell Scientific's GPS command in the magnaprobe does not update the
    datalogger's clock. For those case, we implemented a best-fix algorithm to compute the time offset between the
    position file timestamp and the magnaprobe timestamp.

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
EMLID_FP = "/mnt/data/media/photography/SALVO/working_a/20240530-ICE/emlid/ubx/rinex_salvo_ice_ice_reachm2-salvo-raw_20240530-194700/salvo_ice_ice_reachm2-salvo-raw_20240530-194700.pos"
MAGNA_FP = "/mnt/data/UAF-data/working_a/SALVO/20240608-BEO/magnaprobe/salvo_beo_line_magnaprobe-geodel_20240608.a2.csv"
EMLID_FP = (
    "/mnt/data/UAF-data/working_a/SALVO/20240608-BEO/emlid/reachm2_raw_202406082214.pos"
)

# Perform GPS comparison analysis, and display figure
DISPLAY = True

# Timeoffset between emlid and magnaprobe
OFFSET = timedelta(hours=0, seconds=0)
OFFSET_CHECK = True

# b-grade products are generated in 'working_b' directory
output_dir = os.path.dirname(MAGNA_FP).replace("working_a", "working_a")

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

# Load ppk position file
print("Loading: ", EMLID_FP)
pos_df = pd.read_csv(EMLID_FP, sep="\\s+", header=9)
pos_df = pos_df.rename(columns={"%": "date"})

# convert time to UTC if in GPST
if "GPST" in pos_df.columns:
    pos_df["UTC"] = pos_df["GPST"] - timedelta(seconds=18)
    pos_df.drop(["GPST"], inplace=True, axis=1)

# aggregate date and time as a timestamp
pos_df["Timestamp"] = pd.to_datetime(
    pos_df["date"] + " " + pos_df["UTC"], format="ISO8601"
)
pos_df.drop(["date", "UTC"], inplace=True, axis=1)

# For location file
if "location" in EMLID_FP or not "events" in EMLID_FP:
    pos_freq = pos_df["Timestamp"].diff().median()

    # Sometimes R2 timestamp are off by a few milliseconds, timestamp is rounded to collection frequency
    pos_df["Timestamp"] = pos_df["Timestamp"].apply(lambda x: x.round(pos_freq))


# Rename columns to match magnaprobe
pos_header_rename = {
    "latitude(deg)": "Latitude",
    "longitude(deg)": "Longitude",
    "height(m)": "Altitude",
    "Q": "Quality",
    "ns": "NSatellite",
    "sdn(m)": "SdN",
    "sde(m)": "SdE",
    "sdu(m)": "SdU",
    "sdne(m)": "SdNE",
    "sdeu(m)": "SdEU",
    "sdun(m)": "SdUN",
    "age(s)": "age",
    "ratio": "ratio",
}
pos_df.rename(columns=pos_header_rename, inplace=True)

# Convert LLH to XYZ
# Convert lat/lon toward X, Y and Z
LOCAL_EPSG = 3338
import pyproj

xform = pyproj.Transformer.from_crs("4326", LOCAL_EPSG)
pos_df[["X", "Y", "Z'"]] = pd.DataFrame(
    xform.transform(pos_df["Latitude"], pos_df["Longitude"], pos_df["Altitude"])
).transpose()
pos_df["Z"] = pos_df["Altitude"]

pos_df[["TrackDist", "TrackDistCum", "DistOrigin"]] = distance.compute_distance(
    pos_df[["X", "Y", "Z"]]
)


# Load data file
print("Loading: ", MAGNA_FP)
magna_df = pd.read_csv(MAGNA_FP, header=0)

# Convert magna to UTC
magna_df["Timestamp"] = (
    pd.to_datetime(magna_df["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
    - timedelta(hours=timezone)
    - OFFSET
)

# Safe original timestamp
magna_df["Timestamp_mg"] = magna_df["Timestamp"]
pos_df["Timestamp_m2"] = pos_df["Timestamp"]

import datetime as dt

OFFSET_CLK = np.linspace(-10, 20, 30 * 10 + 1)

data = np.zeros([len(magna_df["Timestamp_mg"]), len(OFFSET_CLK), 5])
data_d = {1.0: 2, 2.0: 3, 5.0: 4}
for ii_ts, ts in enumerate(magna_df["Timestamp_mg"]):
    ts_round = np.round(ts.timestamp() * 10) / 10
    for ii_offset, offset in enumerate(OFFSET_CLK):
        data[ii_ts][ii_offset][0] = ts_round
        data[ii_ts][ii_offset][1] = offset
        ts_offset = ts_round + offset

        # Round magna probe time to pose_freq
        ts_offset_start = dt.datetime.fromtimestamp(ts_offset) - dt.timedelta(seconds=5)
        ts_offset_end = dt.datetime.fromtimestamp(ts_offset) + dt.timedelta(seconds=20)
        ts_offset = pos_df.loc[
            (pos_df["Timestamp_m2"] >= ts_offset_start)
            & (pos_df["Timestamp_m2"] <= ts_offset_end)
        ]

        # Check fix:
        groups = ts_offset.groupby("Quality")
        var = ["SdNE", "SdU"]
        for ID, group in groups:
            P = len(group[var]) / len(ts_offset) * 100
            data[ii_ts][ii_offset][data_d[ID]] = P

plt.figure()
for row in range(0, len(data)):
    plt.plot(data[row, :, 1], data[row, :, 2], label=row)
# plt.plot(data[:, 0], data[:, 2], label='2')
# plt.plot(data[:, 0], data[:, 3], label='5')
plt.grid()
plt.show()


plt.figure()
for row in np.round(np.linspace(0, 200, 11)).astype(int):
    plt.plot(data[row, :, 1], data[row, :, 2], label=row)
# plt.plot(data[:, 0], data[:, 2], label='2')
# plt.plot(data[:, 0], data[:, 3], label='5')
plt.grid()
plt.show()
