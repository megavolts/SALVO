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
    Extract following file types from raw archives:
    - Basestation: 24O
    - Rover: 24O, 24P and UBX
    History of file changes is kept as a dictionary entry within the yaml configuration file
"""

import os
import zipfile
import logging
import shutil
import yaml

__author__ = "Marc Oggier"

# -- USER VARIABLE
RAW_DIR = "/mnt/data/UAF-data/raw/SALVO/20240525-ARM/emlid/"
RAW_DIR = "/mnt/data/UAF-data/raw/SALVO/20240526-ICE/emlid/"
RAW_DIR = "/mnt/data/UAF-data/raw/SALVO/20240527-ARM/emlid/"
RAW_DIR = "/mnt/data/UAF-data/raw/SALVO/20240529-BEO/emlid/"
# RAW_DIR = "/mnt/data/UAF-data/raw/SALVO/20240530-ICE/emlid/"

LTYPE = {
    "rover": {"ubx": ["ubx"], "rinex": ["24O", "24P"]},
    "basestation": {"24O": ["24O"], "rinex": ["24O", "24P"]},
}

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
for item in os.scandir(RAW_DIR):
    if not item.name.startswith("salvo"):
        continue
    elif item.name.endswith(".yaml"):
        continue
    elif item.name.endswith(".csv"):
        target_fp = item.path.replace("/raw/", "/working_a/")
        if "00.csv" not in target_fp:
            target_fp = target_fp.replace(".csv", ".00.csv")
        if not os.path.exists(target_fp):
            os.makedirs(os.path.dirname(target_fp))
        shutil.copy(item.path, target_fp)
        continue
    print(item.name)

    RINEX_FLAG = True
    RATE_FLAG = None
    if "rinex" in item.path:
        for ubx_f in [_f for _f in os.listdir(RAW_DIR) if "ubx" in _f]:
            if item.path.startswith(ubx_f.split("ubx")[0]) and item.path.endswith(
                ubx_f.split("ubx")[-1]
            ):
                RINEX_FLAG = False
        if "Hz" in item.path.split("rinex")[-1].split("_")[0]:
            RATE_FLAG = item.path.split("rinex")[-1].split("_")[0][:4]
    if PROCESS_ALL_RAW:
        RINEX_FLAG = True
    INSTRUMENT = "-".join(item.path.split("_")[3].split("-")[:2])
    INSTRUMENT_TYPE = [
        key
        for key in ["rover", "basestation"]
        if INSTRUMENT in config["instrument"][key]
    ][0]

    # Rover
    if (
        INSTRUMENT in config["instrument"][INSTRUMENT_TYPE] and RINEX_FLAG
    ):  # and any(type in dir_file for type in LTYPE["reachm2"])
        # By default archive contains rinex files
        try:
            ltype = [_t for _t in LTYPE[INSTRUMENT_TYPE] if _t in item.path][0]
        except IndexError:
            ltype = "rinex"
        else:
            pass

        zip_fp = item.path
        with zipfile.ZipFile(zip_fp) as archive:
            # Travel through the zip-archive
            for zip_file in archive.namelist():
                zip_ext = zip_file.split(".")[-1]
                print(zip_file)
                if zip_ext in LTYPE[INSTRUMENT_TYPE][ltype]:
                    target_fp = os.path.join(OUT_DIR, ltype, zip_file)
                    os.makedirs(os.path.dirname(target_fp), exist_ok=True)
                    # Open output path, and write contents of file in it
                    with open(target_fp, "wb") as f:
                        f.write(archive.read(zip_file))
                    if DISPLAY:
                        print(
                            INSTRUMENT_TYPE.capitalize()
                            + " "
                            + INSTRUMENT
                            + ": "
                            + zip_ext
                            + ":"
                            + zip_file.split("/")[-1]
                        )

                    # Add file to PPK processing in config
                    if INSTRUMENT_TYPE not in config["PPK processing"]:
                        config["PPK processing"][INSTRUMENT_TYPE] = {}
                    if INSTRUMENT in config["PPK processing"][INSTRUMENT_TYPE]:
                        config["PPK processing"][INSTRUMENT_TYPE][INSTRUMENT].append(
                            [zip_ext, zip_file.split("/")[-1]]
                        )
                    else:
                        config["PPK processing"][INSTRUMENT_TYPE][INSTRUMENT] = [
                            [zip_ext, zip_file.split("/")[-1]]
                        ]
        if INSTRUMENT not in config["instrument"][INSTRUMENT_TYPE] or not isinstance(
            config["instrument"][INSTRUMENT_TYPE][INSTRUMENT], float
        ):
            logger.warning("Missing height for rover: " + INSTRUMENT)

if CONFIG_FP is not None:
    target_fp = CONFIG_FP.replace("/raw/", "/working_a/")
    with open(target_fp, "w", encoding="UTF-8") as f:
        yaml.dump(config, f)
else:
    logger.warning("TODO: define CONFIG_FP when not define")
