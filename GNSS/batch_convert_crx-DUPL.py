# /usr/bin/env python
"""
batch_convert_crx.py: Script to batch convert compressed RINEX (crx) files to YYo format, will also unzip gz files.
Author: Tim Whiteside
Requires: crx2rnx.exe (https://terras.gsi.go.jp/ja/crx2rnx.html) application on your C drive somwhere
Requires: glob, os, easygui, shutil, gzip
"""

import glob, os
import easygui as gu
import shutil
import gzip
from os.path import splitext as spext

# set working directory
#root_dir = gu.diropenbox("Select folder location", "Choose folder", "C:\\")
root_dir = '/mnt/data/UAF-data/raw_0/SALVO/00-DUPL base station/CEEbase/'
os.chdir(root_dir)

# select location of crx2rnx executable
#crx2rnx = gu.fileopenbox("Locate the crx2rnx executable", "Find CRX2RNX", default=os.path.join(root_dir, "*.exe"))
crx2rnx = '/usr/bin/crx2rnx'
gfzrnx = '/usr/bin/gfzrnx'
rnx2crx = '/usr/bin/rnx2crx'
file_discard = ['20240527203820', '20240527233728']
smp = 30
print(root_dir, crx2rnx)

wkg_dir = root_dir
fileList = os.listdir(wkg_dir)

def batch_crx_to_rnx(wkg_dir,crx2rnx):
    """
    Function to batch decompress Hatanaka compressed RINEX files (.crx) to RINEX (.rnx)
    Uses crx2rnx executable: https://terras.gsi.go.jp/ja/crx2rnx.html
    :param wkg_dir: Location of crx files
    :param crx2rnx: Location of crx2rnx executable
    :return: rnx files
    """
    os.chdir(wkg_dir)
    # Get list of .crx files
    fileList = os.listdir(wkg_dir)
    # Loop through files and convert to RINEX
    for file in glob.glob("*.24d"):
        # Build shell string for each file
        ShellString = ''.join([crx2rnx, " ", file])
        # Run shell command
        os.system(ShellString)

# def change_file_extension(wkg_dir, new_extension):
#     """
#     Function to change rnx extension to YYo
#     where YYo is two digit year observation
#     :param wkg_dir: Location of RNx files
#     :param new_extension: e.g 23o for 2023
#     :return YYo files
#     """
#     os.chdir(wkg_dir)
#     for file in glob.glob("*.24o"):
#         file_path = file
#         base_name, _ = os.path.splitext(file)
#         new_filename = base_name + '.' + new_extension
#         # Rename the file to the path with the new extension and report the result.
#         os.rename(file_path, new_filename)

### Run function
batch_crx_to_rnx(root_dir,crx2rnx)

def batch_decim(wkg_dir, smp=smp, glob_pattern="*.24O"):
    """
    Function to batch decompress Hatanaka compressed RINEX files (.crx) to RINEX (.rnx)
    Uses crx2rnx executable: https://terras.gsi.go.jp/ja/crx2rnx.html
    :param wkg_dir: Location of crx files
    :param smp: sample rate in seconds
    :return: rnx files
    """
    os.chdir(wkg_dir)
    subdir = 'decim' + str("%ss" %smp)
    outdir = os.path.join(wkg_dir, subdir)
    os.makedirs(os.path.join(wkg_dir, subdir), exist_ok=True)
    # Loop through files and convert to RINEX
    for file in glob.glob("*.24O"):
        print(file)
        # Build shell string for each file
#        ShellString = " ".join(["teqc -O.dec", str("%s" %smp), file, ">", subdir+'/'+file.split('.')[0]+'_decim' + str("%ss" %smp) +'.24O'])
        ShellString = " ".join([gfzrnx, " -smp ", str("%s" %smp), "-finp", file, "-fout \"", os.path.join(outdir, file.split('.')[0]+'_decim' + str("%ss" %smp) +'.24O') + "\""])
        # Run shell command
        os.system(ShellString)
    return subdir
root_dir = os.path.join(root_dir, batch_decim(root_dir, smp, "*.24O"))

wkg_dir = root_dir
wkg_dir = os.path.join(root_dir, 'decim' + str("%ss" %smp))
def batch_concat(wkg_dir, smp=smp, periodLength=7):
    import numpy as np
    import datetime as dt
    os.chdir(wkg_dir)
    # Get list of .crx files
    fileList = os.listdir(wkg_dir)
    fileList = sorted(fileList)

    file_discard.append('-full_output.zip')
    # Filter function and a lambda function
    fileList = list(filter(lambda x: all(y not in x for y in file_discard), fileList))

    # Create dictionary file:days
    fileDict = {file.split('_')[2]:file for file in fileList if '_decim'+str('%ss.24O' %smp) in file}
    doyDict = {int(dt.datetime.strptime(date, '%Y%m%d%H%M%S').strftime('%j')):date for date in fileDict.keys()}
    doyDict[148] = '20240528000301'
    # Create 7 consecutive days bracket
    periods = []
    doy = np.array(sorted(doyDict.keys()))
    doy_start = doy[0]
    while doy_start < max(doy):
        ii_day = 0
        while ii_day < periodLength:
            if doy_start + ii_day in doy:
                if ii_day == 0:
                    consecutiveDays = [doy_start]
                else:
                    consecutiveDays.extend([doy_start + ii_day])
            ii_day += 1
        periods.append(np.array(consecutiveDays))
        if doy_start + ii_day < max(doy):
            doy = doy[doy_start+ii_day <= doy]
            doy_start = doy[0]
        else:
            break

    for period in periods:
        # Build shell string containing each daily files
        files = []
        for doy in period:
            files += [fileDict[doyDict[int(doy)]]]

        files = " ".join(files)
        outfile = 'CEEbase_raw' + str("_%s_%s_decim%ss.24o" %(doyDict[period[0]], doyDict[period[-1]], smp))

        ShellString = " ".join([gfzrnx, "-finp", files, "-fout", outfile, "-kv"])
        # Run shell command
        os.system(ShellString)

        # Build shell string for each file
        ShellString = ''.join([rnx2crx, " ", outfile])
        # Run shell command
        os.system(ShellString)
        print(outfile)

batch_concat(root_dir)
