# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
This script performed tasks,

- Move and renamed UBX files which were converted to RINEX from `ubx` directory to `rinex` directory
- Move and rename all the POS position in the emlid directory and subdirectory
- Add location and event files with the highest sampling rate to config file
- Apply a RC-like filter to remove mechanical bouncing that triggered multiple event signals on a short
time (Dt < 0.1 s)


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
from salvo.naming.folder import list_files_walk

__author__ = "Marc Oggier"

# -- USER VARIABLE
EMLID_DIR = "/mnt/data/UAF-data/working_a/SALVO/20240420-BEO/emlid"
EMLID_DIR = "/mnt/data/UAF-data/working_a/SALVO/20240525-ARM/emlid"

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

event_fn = config["position"]["event"]
event_fp = os.path.join(EMLID_DIR, event_fn)
