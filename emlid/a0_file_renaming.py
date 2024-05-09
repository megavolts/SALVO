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

# -*- coding: utf-8 -*-
# ! /usr/bin/env python
import os
import logging
import shutil
import zipfile

import yaml

import salvo.naming

__author__ = "Marc Oggier"


EMLID_DIR = "/mnt/data/UAF-data/raw/SALVO/20240522-ARM/emlid/"

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
for item in os.listdir(EMLID_DIR):  # loop through items in dir
    if not item.startswith("salvo_") and item.endswith(
        ".zip"
    ):  # check for '.zip' extension
        org_zip_fp = os.path.join(EMLID_DIR, item)  # zip filepath
        bkp_fp = os.path.join(org_dir, item)  # backup filepath
        if not os.path.exists(bkp_fp):  # check if backup file does not exit
            shutil.copy(org_zip_fp, bkp_fp)  # backup a copy of the original filename
        site = config["site"]
        LOCATION = "-".join(config["location"])

        with zipfile.ZipFile(org_zip_fp) as archive:
            BASENAME = salvo.naming.emlid.create_emlid_name(item, site, LOCATION)
            extract_dir = os.path.join(EMLID_DIR, BASENAME)

            # loop through the file in the archive, rename during extraction, while conserving directory structure
            for file in archive.namelist():
                # Check if file is in level-1 subdirectory
                if "/" in file:
                    if len(file.split("/")) > 2:
                        print("TODO: only 1 level subdirectory has been implemented")
                    else:
                        org_subdir = file.split("/")[0]
                        NEW_SUBDIR = salvo.naming.emlid.create_emlid_name(
                            file.split("/")[0], site, LOCATION
                        )
                        org_fn = file.split("/")[-1]
                else:
                    NEW_SUBDIR = None
                    org_fn = file
                target_fn = (
                    salvo.naming.emlid.create_emlid_name(
                        org_fn.split(".")[0], site, LOCATION
                    )
                    + "."
                    + org_fn.split(".")[-1]
                )  # target filename
                target_fp = os.path.join(
                    extract_dir, "/".join(filter(None, [NEW_SUBDIR, target_fn]))
                )  # target filepath
                if not os.path.exists(
                    os.path.dirname(target_fp)
                ):  # check if subdirectory exists
                    os.makedirs(
                        os.path.dirname(target_fp)
                    )  # create subdirectory if not
                with open(target_fp, "wb") as f:  # open the output path for writing
                    f.write(archive.read(file))  # save the contents of the file in it
            print("Extraction complete for ", org_zip_fp)

            # create zip archive with files and subdirectories named according to SALVO-2024 name convention
            new_zip_fn = BASENAME + ".00.zip"
            new_zip_fp = os.path.join(EMLID_DIR, new_zip_fn)
            with zipfile.ZipFile(
                new_zip_fp, "w"
            ) as zip_object:  # open the output path for writing
                # Traverse all files in directory
                rootlen = len(extract_dir) + 1
                for folder_name, sub_folders, file_names in os.walk(extract_dir):
                    for filename in file_names:
                        file_path = os.path.join(
                            folder_name, filename
                        )  # Create filepath of files in directory
                        zip_object.write(
                            file_path, file_path[rootlen:]
                        )  # Add files to zip file

            # Clean the raw directory folder
            if os.path.exists(new_zip_fp):  # check if zip file was created successfully
                os.remove(org_zip_fp)  # then delete old zipfile
                shutil.rmtree(extract_dir)  # then delete the extraction folder
                print(new_zip_fn + " was created successfully. Cleaning raw directory")

            # Add name history record in config file:
            if "name history" not in config:
                config["name history"] = {item: new_zip_fn}
            else:
                if item not in config["name history"]:
                    config["name history"][item] = new_zip_fn
                else:
                    continue
#
with open(os.path.join(EMLID_DIR, config_fp), "w", encoding="UTF-8") as yaml_f:
    yaml.dump(config, yaml_f)
