# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
Extract files required for PPK processing via EmlidStudio for the raw data located in RAW_DIR to a workign direcotory
Rename files and directories within RS2/reachm2 archive according to SALVO-2024 naming convention.


Inputs:
    RAW_DIR: Directory containing
        - the emlid archive file as downloaded from the emlid instrument
        - a yaml configuration file containing information about site and location

Outputs:
    Extract from raw archives, when avai
    History of file changes is kept as a dictionary entry within the yaml configuration file
"""

import os
import zipfile
import logging

import yaml

__author__ = "Marc Oggier"

# -- USER VARIABLE
RAW_DIR = "/mnt/data/UAF-data/raw/SALVO/20240420-BEO/emlid"
LTYPE = {"reachm2": {"ubx": ["ubx"], "rinex": ["24O", "24P"]}, "RS2": ["24O"]}

DISPLAY = True
PROCESS_ALL_RAW = True
# -- LOGGER
logger = logging.getLogger(__name__)

# -- PROCESS
# Create working direcotry if not existing
OUT_DIR = RAW_DIR.replace("/raw/", "/working_a/")

# Load config file
config = {}
CONFIG_FP = None
for file in os.listdir(RAW_DIR):
    if file.endswith("yaml"):
        with open(os.path.join(RAW_DIR, file), "r", encoding="UTF-8") as f:
            config = yaml.safe_load(f)
            if "PPK processing" not in config:
                config["PPK processing"] = {}
        CONFIG_FP = os.path.join(RAW_DIR, file)
        break

# Look for file in the RAW_DIR directory
# We reverse the file order so that 'ubx' file comes before 'rinex'
for dir_file in os.listdir(RAW_DIR):
    # Skip RINEX if UBX exists for the same filename
    RINEX_FLAG = True
    RATE_FLAG = None
    if "rinex" in dir_file:
        for ubx_f in [_f for _f in os.listdir(RAW_DIR) if "ubx" in _f]:
            if dir_file.startswith(ubx_f.split("ubx")[0]) and dir_file.endswith(
                ubx_f.split("ubx")[-1]
            ):
                RINEX_FLAG = False
        if "Hz" in dir_file.split("rinex")[-1].split("_")[0]:
            RATE_FLAG = dir_file.split("rinex")[-1].split("_")[0][:4]
    if PROCESS_ALL_RAW:
        RINEX_FLAG = True

    # Rover
    if (
        "reachm2" in dir_file
        and RINEX_FLAG
        and any(type in dir_file for type in LTYPE["reachm2"])
    ):
        ltype = [type for type in LTYPE["reachm2"] if type in dir_file][0]
        zip_fp = os.path.join(RAW_DIR, dir_file)
        with zipfile.ZipFile(zip_fp) as archive:
            # Travel through the zip-archive
            for zip_file in archive.namelist():
                zip_ext = zip_file.split(".")[-1]
                if zip_ext in LTYPE["reachm2"][ltype]:
                    target_fp = os.path.join(OUT_DIR, ltype, zip_file)
                    os.makedirs(os.path.dirname(target_fp), exist_ok=True)
                    # Open output path, and write contents of file in it
                    with open(target_fp, "wb") as f:
                        f.write(archive.read(zip_file))
                    if DISPLAY:
                        print(
                            "Rover reachm2: " + zip_ext + ":" + zip_file.split("/")[-1]
                        )
                    # Add file to PPK processing in config
                    if "reachm2" in config["PPK processing"]:
                        config["PPK processing"]["reachm2"].append(
                            [zip_ext, zip_file.split("/")[-1]]
                        )
                    else:
                        config["PPK processing"]["reachm2"] = [
                            [zip_ext, zip_file.split("/")[-1]]
                        ]
        if "reachm2_height" not in config or not isinstance(
            config["reachm2_height"], float
        ):
            logger.warning("Missing height for reachm2 rover")

    if "rs2" in dir_file:
        zip_fp = os.path.join(RAW_DIR, dir_file)  # zip filepath
        # Loop through the list of files to extracts
        with zipfile.ZipFile(zip_fp) as archive:
            # Travel through the zip-archive
            for zip_file in archive.namelist():
                zip_ext = zip_file.split(".")[-1]
                if zip_file.split(".")[-1] in LTYPE["RS2"]:
                    if "/" in zip_file:
                        target_fp = os.path.join(
                            OUT_DIR, "rinex", zip_file.split("/")[-1]
                        )
                    else:
                        target_fp = os.path.join(OUT_DIR, "rinex", zip_file)
                    os.makedirs(os.path.dirname(target_fp), exist_ok=True)
                    # Open output path to save content to file
                    with open(target_fp, "wb") as f:
                        f.write(archive.read(zip_file))
                    if DISPLAY:
                        print(
                            "Base Station RS2: "
                            + zip_ext
                            + ":"
                            + zip_file.split("/")[-1]
                        )
                    # Add file to PPK processing in config
                    if "rs2" in config["PPK processing"]:
                        config["PPK processing"]["rs2"].append(
                            [zip_ext, zip_file.split("/")[-1]]
                        )
                    else:
                        config["PPK processing"]["rs2"] = [
                            [zip_ext, zip_file.split("/")[-1]]
                        ]
        # Check if config file has height for RS2
        if "rs2_height" not in config or not isinstance(config["rs2_height"], float):
            logger.warning("Missing height for RS2 base station")

if CONFIG_FP is not None:
    target_fp = CONFIG_FP.replace("/raw/", "/working_a/")
    with open(target_fp, "w", encoding="UTF-8") as f:
        yaml.dump(config, f)
else:
    logger.warning("TODO: define CONFIG_FP when not define")
