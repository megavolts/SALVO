# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
Rename files and directories within RS2/reachm2 archive according to SALVO-2024 naming convention.

Inputs:
    EMILD_DIR: Directory containing
        - the emlid archive file as downloaded from the emlid instrument
        - a yaml configuration file containing information about site and location

Outpus:
    Archive file containing updated file and directory names.
    History of file changes is kept as a dictionary entry within the yaml configuration file
"""

import os
import zipfile
import logging

import yaml

logger = logging.getLogger(__name__)

__author__ = "Marc Oggier"

# -- USER VARIABLE
RAW_DIR = "/mnt/data/UAF-data/raw/SALVO/20240522-ARM/emlid/"
FILE_LIST = {"reachm2": ["24O", "24P"], "RS2": ["24O"]}
DISPLAY = True

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
        CONFIG_FP = os.path.join(RAW_DIR, file)
        break

# Extract ROVER rinex
for dir_file in os.listdir(RAW_DIR):
    if "reachm2" in dir_file and "rinex" in dir_file:
        zip_fp = os.path.join(RAW_DIR, dir_file)  # zip filepath
        with zipfile.ZipFile(zip_fp) as archive:
            for (
                zip_file
            ) in archive.namelist():  # loop through the list of files to extracts
                zip_ext = zip_file.split(".")[-1]
                if zip_ext in FILE_LIST["reachm2"]:
                    target_fp = os.path.join(OUT_DIR, zip_file)
                    # open ouput path, and write contents of file in it
                    with open(target_fp, "wb") as f:
                        f.write(archive.read(zip_file))
                    if DISPLAY:
                        print("Rover reachm2: " + zip_ext + ":" + zip_file)
            # TODO: add rinex/rover to config file
    if "rs2" in dir_file:
        zip_fp = os.path.join(RAW_DIR, dir_file)  # zip filepath
        with zipfile.ZipFile(zip_fp) as archive:
            for (
                zip_file
            ) in archive.namelist():  # loop through the list of files to extracts
                if zip_file.split(".")[-1] in FILE_LIST["RS2"]:
                    if "/" in zip_file:
                        target_fp = os.path.join(OUT_DIR, zip_file.split("/")[-1])
                    else:
                        target_fp = os.path.join(OUT_DIR, zip_file)
                    with open(target_fp, "wb") as f:  # open the output path for writing
                        f.write(
                            archive.read(zip_file)
                        )  # save the contents of the file in it
                    if DISPLAY:
                        print(
                            "B Station RS2: " + zip_ext + ":" + target_fp.split("/")[-1]
                        )
            # TODO: add rinex/base station to config file

if CONFIG_FP is not None:
    target_fp = CONFIG_FP.replace("/raw/", "/working_a/")
    with open(target_fp, "w", encoding="UTF-8") as f:
        yaml.dump(config, f)
else:
    logger.warning("TODO: define CONFIG_FP when not define")
