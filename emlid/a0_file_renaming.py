"""
Rename files and directories within RS2/reachm2 archive according to SALVO-2024 naming convention.

Inputs:
    EMLID_DIR: Directory containing
        - the emlid archive file as downloaded from the emlid instrument
        - A yaml configuration file containing at least information about site, location

Outputs:
    - Copy of the original zip-archives file under ./original/
    - Zip-archives file containing updated file and directory names
    - A yaml configuration file containing information about site, location, and the history of filename change as a
      dictionary entry within the yaml configuration file
"""

# -*- coding: utf-8 -*-
# ! /usr/bin/env python

import os
import logging
import shutil
import zipfile
import yaml
import pandas as pd
from salvo.naming import emlid

__author__ = "Marc Oggier"

EMLID_DIR = "/mnt/data/UAF-data/raw/SALVO/20240525-ARM/emlid/"
EMLID_DIR = "/mnt/data/UAF-data/raw/SALVO/20240526-ICE/emlid/"
EMLID_DIR = "/mnt/data/UAF-data/raw/SALVO/20240527-ARM/emlid/"
EMLID_DIR = "/mnt/data/UAF-data/raw/SALVO/20240528-ARM/emlid/"
EMLID_DIR = "/mnt/data/UAF-data/raw/SALVO/20240529-BEO/emlid/"
EMLID_DIR = "/mnt/data/UAF-data/raw/SALVO/20240530-ICE/emlid/"


# Create `original` directory if it does not exist
org_dir = os.path.join(EMLID_DIR, "original")
if not os.path.exists(org_dir):
    os.makedirs(org_dir)

# -- PROCESS
logger = logging.getLogger(__name__)

# Read configuration file if exists. Return error if not
config = {}
for file in os.listdir(EMLID_DIR):
    if file.endswith("yaml"):
        with open(os.path.join(EMLID_DIR, file), "r", encoding="UTF-8") as yf:
            config = yaml.safe_load(yf)
        config_fp = os.path.join(EMLID_DIR, file)
        break
if len(config) == 0:
    logger.error("No yaml configuration file was found")

# Copy zip-archived to `original` subdirectory if it does not exist
# Loop through all file in directory

for item in os.scandir(EMLID_DIR):
    if (
        item.is_file()
        and not item.name.startswith("salvo_")
        and item.name.endswith(".zip")
    ):
        zip_fp = item.path  # zip filepath
        bkp_fp = os.path.join(org_dir, item.name)  # backup filepath
        if not os.path.exists(bkp_fp):  # check if backup file does not exit
            shutil.copy(zip_fp, bkp_fp)  # backup a copy of the original filename
        SITE = config["site"]
        if isinstance(SITE, list):
            SITE = "-".join(SITE)
        LOC = "-".join(config["location"])
        LOC = config["site"]
        if isinstance(LOC, list):
            LOC = "-".join(LOC)
        with zipfile.ZipFile(zip_fp) as archive:
            # Check for sampling rate for RINEX archive
            if "rinex" in os.path.basename(zip_fp.lower()):
                # check for sampling in observation file:
                obs_file = [
                    file for file in archive.namelist() if file.endswith("24O")
                ][-1]
                # read observation file content
                content = zipfile.Path(archive, at=obs_file).read_text(encoding="UTF-8")
                # look for sampling interval at line 18 [in second]
                if (
                    list(filter(None, content.split("\n")[17].split(" ")))[1]
                    == "INTERVAL"
                ):
                    spl_interval = float(
                        list(filter(None, content.split("\n")[17].split(" ")))[0]
                    )
                    SPL_RATE = f"{1/spl_interval:02.0f}Hz"
                elif (
                    len([line for line in content.split("\n") if line.startswith(">")])
                    > 2
                ):
                    # parse text file, looking for date row entry starting with '>'
                    lines = [
                        line for line in content.split("\n") if line.startswith(">")
                    ]
                    data = [
                        list(filter(None, line[1:].split(" ")))[0:6] for line in lines
                    ]
                    data = pd.DataFrame(
                        data,
                        columns=["year", "month", "day", "hour", "minute", "second"],
                    )
                    data = pd.to_datetime(data)
                    # compute sampling frequency
                    spl_interval = (
                        data.diff().median().seconds
                        + data.diff().median().microseconds / 1e6
                    )
                    SPL_RATE = 1 / spl_interval
                else:
                    SPL_RATE = None
                    logger.warning(str("Sampling interval not define in " + obs_file))
            else:
                SPL_RATE = None

            BASENAME = emlid.create_emlid_name(item.name, SITE, LOC, SPL_RATE)
            extract_dir = os.path.join(EMLID_DIR, BASENAME)

            # loop through the file in the archive, rename during extraction, while conserving directory structure
            for file in archive.namelist():
                # Check if file is in level-1 subdirectory
                if "/" in file[:-1]:
                    if len(list(filter(None, file.split("/")))) > 2:
                        print("TODO: only 1 level subdirectory has been implemented")
                    else:
                        org_subdir = file.split("/")[0]
                        NEW_SUBDIR = emlid.create_emlid_name(
                            file.split("/")[0], SITE, LOC, SPL_RATE
                        )
                        org_fn = file.split("/")[-1]
                # skip directory
                elif "/" in file[-1]:
                    continue
                else:
                    NEW_SUBDIR = None
                    org_fn = file
                target_fn = (
                    emlid.create_emlid_name(org_fn.split(".")[0], SITE, LOC, SPL_RATE)
                    + "."
                    + org_fn.split(".")[-1]
                )
                # target filename
                target_fp = os.path.join(
                    extract_dir, "/".join(filter(None, [NEW_SUBDIR, target_fn]))
                )
                # create subdirectory if it does not exist
                if not os.path.exists(os.path.dirname(target_fp)):
                    os.makedirs(os.path.dirname(target_fp))
                # open the output path and save content to the file
                with open(target_fp, "wb") as f:
                    f.write(archive.read(file))

            # create zip archive with files and subdirectories named according to SALVO-2024 name convention
            new_zip_fn = BASENAME + ".00.zip"
            new_zip_fp = os.path.join(EMLID_DIR, new_zip_fn)

            # open the output path, and save content to files
            with zipfile.ZipFile(new_zip_fp, "w") as zip_object:
                # Traverse all files in directory
                rootlen = len(extract_dir) + 1
                for folder_name, sub_folders, file_names in os.walk(extract_dir):
                    for filename in file_names:
                        # Create filepath of files in directory
                        file_path = os.path.join(folder_name, filename)
                        # Add files to zip file
                        zip_object.write(
                            file_path, file_path[rootlen:]
                        )  # Add files to zip file

            # Clean unneeded file in directory
            if os.path.exists(new_zip_fp):  # check if zip file was created successfully
                os.remove(zip_fp)  # then delete old zipfile
                shutil.rmtree(extract_dir)  # then delete the extraction folder
                print(new_zip_fn + " was created successfully. Cleaning raw directory")

            # Add name history record in config file:
            if "name history" not in config.keys():
                config["name history"] = {item.name: new_zip_fn}
            else:
                if "name history" not in config:
                    config["name history"][item.name] = new_zip_fn
                if config["name history"] is None:
                    config["name history"] = {}
                    config["name history"][item.name] = new_zip_fn
                elif item.name not in config["name history"]:
                    config["name history"][item.name] = new_zip_fn
                else:
                    continue

with open(os.path.join(EMLID_DIR, config_fp), "w", encoding="UTF-8") as yaml_f:
    yaml.dump(config, yaml_f)
