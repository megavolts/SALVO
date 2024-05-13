# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
Inputs:
    EMLID_DIR: Directory containing
        - the emlid archive file as downloaded from the emlid instrument
        - a yaml configuration file containing information about site and location

Outpus:
    Archive file containing updated file and directory names.
    History of file changes is kept as a dictionary entry within the yaml configuration file
"""

import os
import logging
from shutil import move
from datetime import timedelta

import pandas as pd
import pyproj
import yaml

from salvo.naming import get_date

__author__ = "Marc Oggier"

# -- USER VARIABLE
EMLID_DIR = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/emlid"
DISPLAY = True
LOCAL_EPSG = 3338
# GPST-UTC Offset
DELTA_T = timedelta(seconds=18)
logger = logging.getLogger(__name__)

# Load the configuration file
CONFIG_FP = None
for file in os.listdir(EMLID_DIR):
    if file.endswith("yaml"):
        CONFIG_FP = os.path.join(EMLID_DIR, file)
        with open(CONFIG_FP, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        break
if len(config) == 0:
    logger.error("No config file available")

# A. PPK correction from raw location UBX
# Move and renamed UBX files which were converted to RINEX from `ubx` directory to `rinex` directory
SUBDIR = "ubx"
for item in os.scandir(os.path.join(EMLID_DIR, SUBDIR)):
    if item.is_dir() and item.path.split("/")[-1].startswith("rinex_"):
        # Check for the sampling rate in the RINEX observation file
        obs_files = [file for file in os.listdir(item.path) if file.endswith("24O")]
        spl_rates = {}
        for file in obs_files:
            with open(os.path.join(EMLID_DIR, item, file), "r", encoding="UTF-8") as f:
                content = f.read()
            # parse text file, looking for date row entry starting with '>'
            lines = [line for line in content.split("\n") if line.startswith(">")]
            data = [list(filter(None, line[1:].split(" ")))[0:6] for line in lines]
            data = pd.DataFrame(
                data, columns=["year", "month", "day", "hour", "minute", "second"]
            )
            date = pd.to_datetime(data, format="%Y%m%d%H%M%S.%f")
            # compute sampling frequency
            spl_interval = date.diff().median().microseconds / 1e6
            spl_rates[file.split(".")[0]] = 1 / spl_interval
        # Move file from subdirectory to root directory, adding sampling frequency
        for file in os.listdir(item.path):
            source_fp = os.path.join(item.path, file)
            spl_rate = spl_rates[file.split(".")[0]]
            target_fn = file.replace("raw", f"raw{spl_rate:02.0f}Hz")
            target_fp = os.path.join(EMLID_DIR, "rinex", target_fn)
            move(source_fp, target_fp)
        # Delete subdirecotry
        os.rmdir(item.path)

# B Move and rename the POS position rom subdir to root directory
# The pos files are located in a subdirectory
for item in os.scandir(EMLID_DIR):
    if item.is_dir() and any(file.endswith(".pos") for file in os.listdir(item.path)):
        spl_rates = {}
        for file in sorted(os.listdir(item.path)):
            common_name = file.replace("_events", "").split(".")[0]
            DATE = get_date(EMLID_DIR)
            LOCATION = "-".join(config["location"])
            SITE = config["site"]
            filename = "salvo_" + SITE + "_" + LOCATION + "_emlid-"
            if "event" in file:
                filename += "event"
            else:
                filename += "location"
            # Add sampling frequency in file name
            if common_name in spl_rates:
                filename += f"{spl_rates[common_name]:02.0f}Hz"
            # - Look for XXHz in filename
            elif "Hz" in file.split("_")[3].split("-")[-1]:
                spl_rate = file.split("_")[-2][-4:]
                filename += spl_rate
                spl_rates[common_name] = float(spl_rate[:2])
            # - Detect
            else:
                with open(
                    os.path.join(EMLID_DIR, item, file), "r", encoding="UTF=8"
                ) as f:
                    content = f.read()
                # parse text file, looking for date row entry starting with '>'
                lines = [
                    line for line in content.split("\n") if not line.startswith("%")
                ]
                data = [list(filter(None, line[:23].split(" ")))[0:6] for line in lines]
                data = pd.DataFrame(data, columns=["date", "time"])
                data = pd.to_datetime(
                    data["date"] + " " + data["time"], format="%Y/%m/%d %H:%M:%S.%f"
                )
                data = data.loc[data.notna()]
                # compute sampling frequency
                spl_interval = (
                    data.diff().median().seconds
                    + data.diff().median().microseconds / 1e6
                )
                spl_rate = 1 / spl_interval
                filename += f"{spl_rate:02.0f}Hz"
                spl_rates[common_name] = spl_rate
            filename += "_" + DATE + ".a1.pos"

            # move and rename file
            source_fp = os.path.join(EMLID_DIR, item.path, file)
            target_fp = os.path.join(EMLID_DIR, filename)
            move(source_fp, target_fp)


for file in os.listdir(EMLID_DIR):
    if file.endswith("a1.pos") and len(file.split(".")) == 3:
        ppk_fp = os.path.join(EMLID_DIR, file)
        ppk_df = pd.read_csv(ppk_fp, sep=r"\s+", header=[9])
        ppk_df.rename(columns={"%": "Date"}, inplace=True)

        # Compute Timestamp from date (Date) and time (GPST or UTC).
        if "GPST" in ppk_df.columns:
            ppk_df["Time"] = ppk_df["GPST"] + DELTA_T
            logger.info(
                str(file + ": dropping GPST columns, after converting GPST time to UTC")
            )
        else:
            ppk_df["Time"] = ppk_df["UTC"]
            ppk_df.drop(columns=["UTC"], inplace=True)
            logger.info(str(file + ": dropping UTC columns"))
        ppk_df["Timestamp"] = pd.to_datetime(
            ppk_df["Date"] + " " + ppk_df["Time"], format="%Y/%m/%d %H:%M:%S.%f"
        )
        # Convert Timestamp to ISO8601
        ppk_df["Timestamp"] = pd.to_datetime(ppk_df["Timestamp"], format="ISO8601")
        # Remove unnecessary date and time columns (Date, GPST)
        ppk_df.drop(["Date", "Time"], axis=1, inplace=True)

        # Rename columns to match magnaprobe:
        columns_name = {
            "latitude(deg)": "Latitude",
            "longitude(deg)": "Longitude",
            "height(m)": "Altitude",
            "Q": "QualityFix",
            "ns": "NSatellite",
            "sdn(m)": "SdN",
            "sde(m)": "SdE",
            "sdu(m)": "SdU",
            "sdne(m)": "SdNE",
            "sdeu(m)": "SdEU",
            "sdun(m)": "SdUN",
            "age(s)": "Age",
            "ratio": "Ratio",
        }
        columns_name = {
            key: val for key, val in columns_name.items() if key in ppk_df.columns
        }
        ppk_df.rename(columns=columns_name, inplace=True)

        # Convert lat/lon toward X, Y and Z
        xform = pyproj.Transformer.from_crs("4326", LOCAL_EPSG)
        ppk_df[["X", "Y"]] = pd.DataFrame(
            xform.transform(ppk_df["Latitude"], ppk_df["Longitude"])
        ).transpose()
        ppk_df["Z"] = ppk_df["Altitude"]

        # Write PPK position
        ppk_fp = os.path.join(EMLID_DIR, file.replace(".a1.", ".a2."))
        ppk_df.to_csv(ppk_fp, index=False)

# C Add POS file with the highest sampling rate to config file
spl_rates = {}
for file in sorted(os.listdir(EMLID_DIR)):
    if file.endswith(".pos"):
        common_name = (
            file.split("Hz")[0][:-2] + "Hz" + file.split("Hz")[1].split(".a")[0]
        )
        a_number = int(file.split(".a")[-1].split(".")[0])
        spl_rate = float(file.split("Hz")[0][-2:])
        if common_name not in spl_rates:
            spl_rates[common_name] = {spl_rate: a_number}
        elif spl_rate not in spl_rates[common_name]:
            spl_rates[common_name][spl_rate] = a_number
        elif spl_rates[common_name][spl_rate] < a_number:
            spl_rates[common_name][spl_rate] = a_number
for common_name, spl_rates in spl_rates.items():
    spl_rate = f"{max(spl_rates):02.0f}Hz"
    ext = f".a{spl_rates[max(spl_rates)]:.0f}.pos"
    spl_name = common_name.split("Hz")[0] + spl_rate + common_name.split("Hz")[1] + ext
    TYPE = spl_name.split("emlid-")[-1].split("Hz")[0][:-2]
    if "position" not in config:
        config["position"] = {TYPE: spl_name}
    else:
        config["position"][TYPE] = spl_name
# Save config file
with (open(CONFIG_FP, "w", encoding="utf-8")) as f:
    yaml.dump(config, f)
