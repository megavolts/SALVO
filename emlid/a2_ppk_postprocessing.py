# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
Inputs:
    EMILD_DIR: Directory containing
        - the emlid archive file as downloaded from the emlid instrument
        - a yaml configuration file containing information about site and location

Outpus:
    Archive file containing updated file and directory names.
    History of file changes is kept as a dictionary entry within the yaml configuration file
"""

import os
from shutil import move
import pandas as pd
import pyproj
import yaml
from salvo.naming import get_site
from salvo.naming import get_date

__author__ = "Marc Oggier"

# -- USER VARIABLE
EMLID_DIR = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/emlid"
DISPLAY = True
LOCAL_EPSG = 3338

# Load the configuration file
for file in os.listdir(EMLID_DIR):
    if file.endswith("yaml"):
        with (open(os.path.join(EMLID_DIR, file), "r", encoding="utf-8")) as f:
            config = yaml.safe_load(f)
        break

# Rename the output file according to SALVO
for file in os.listdir(EMLID_DIR):
    if file.endswith(".pos") and len(file.split(".")) < 3:
        site = get_site(EMLID_DIR)
        date = get_date(EMLID_DIR)
        LOCATION = "-".join(config["location"])
        filename = "salvo_" + site + "_" + LOCATION
        if "event" in file:
            filename += "_emlid-event_"
        else:
            filename += "_emlid-location_"
        filename += date + ".a1.pos"
        ppk_fp = os.path.join(EMLID_DIR, filename)
        move(os.path.join(EMLID_DIR, file), ppk_fp)
        break

for file in os.listdir(EMLID_DIR):
    if file.endswith("a1.pos") and len(file.split(".")) == 3:
        print(file)
        ppk_fp = os.path.join(EMLID_DIR, file)

        # Formatting files
        HEADER = "Date GPST Latitude Longitude Altitude FixQuality NSatellite StdN StdE StdU StdNE StdEU StdUN Age Ratio"
        ppk_df = pd.read_csv(ppk_fp, comment="%", sep=r"\s+", names=HEADER.split())

        # Compute Timestamp from date (Date) and time (GPST)
        ppk_df["Timestamp"] = pd.to_datetime(
            ppk_df["Date"] + " " + ppk_df["GPST"], format="%Y/%m/%d %H:%M:%S.%f"
        )
        # Convert Timestamp to ISO8601
        ppk_df["Timestamp"] = pd.to_datetime(ppk_df["Timestamp"], format="ISO8601")
        # Remove unnecessary date and time columns (Date, GPST)
        ppk_df.drop(["Date", "GPST"], axis=1, inplace=True)

        # Convert lat/lon toward X, Y and Z
        xform = pyproj.Transformer.from_crs("4326", LOCAL_EPSG)
        ppk_df[["X", "Y"]] = pd.DataFrame(
            xform.transform(ppk_df["Latitude"], ppk_df["Longitude"])
        ).transpose()
        ppk_df["Z"] = ppk_df["Altitude"]

        # Write PPK position
        ppk_fp = os.path.join(EMLID_DIR, file.replace(".a1.", ".a2.pos"))
        ppk_df.to_csv(ppk_fp, drop_index=True)
