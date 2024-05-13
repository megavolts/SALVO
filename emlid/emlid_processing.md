# EMLID Processing

During the SALVO 2024 campaign we used the following Emlid instruments:
- RS2 as base station.
- Reachm2 as a rover, with the antenna attached to the top of the magnaprobe. The frequency of data acquisisiton is set to 5Hz.

Here we describe how we process the emlid RS2/reachm2 data files associated to the magnaprobe for the SALVO-2024 field campaign

## 0 - Data download
Reachm2 and RS2 data file are downloaded upon returning from the field.

202040510: we suspect that the reachm2 downsamples the data to 1Hz when converting from the raw GPS location UBX file to RINEX file.

### 0.1 Configuration file
Parameters are stored within a configuration yaml-file. Its filename  follows the pattern `salvo_SITE_LOCATION_emlid_DATE.yaml`, with *DATE* as *YYYYMMDD*. The following field are required:
- site: *site* (`arm`, `beo`, or `ice`)
- location; if several, locations are separated with a comma: *location* (`line`, `longline`, `library`)
- height of the reachm2 antenna, in meter: *reachm2_height*
- height of the rs2 base station, in meter: *rs2_height*:
- date: *date* (YYYYMMDD)
- timezone: UTC

## 1 - File renaming
Both RS2 and reachm2 consists of zip-archive, which contain files and directories named after the archive name. Thus, when renaming the archive, one should rename the files and directories within.

First, we copy the original files with their original names to the `original` subdirectory at the root of the daily emlid raw data folder.

Second, we extract each zip archive into a temporary subdirectory following the SALVO-2024 naming convention. As files and directories are extracted, they are renamed accordingly:
- reachm2: salvo_SITE_reachm2-TYPE_DATE-TIME.EXT
- RS2: salvo_SITE_rs2-LOGTYPE_DATE-TIME.EXT

With:
- SITE is `arm`, `beo`, or `ice`
- TYPE is `rinex1Hz`, `ubx5Hz`, `raw`
- DATE in format `YYYYMMDD`
- TIME in format `HHMMSS`
- EXT is the original file extension

Third, we recreate a zip archive following the SALVO-2024 naming convention, prepending *.00* to the *.zip* file extension to denote the raw data before. Upon successful archiving, the temporary directory is deleted.
- reachm2: salvo_SITE_reachm2-LOGTYPE_DATE-TIME.00.zip
- RS2: salvo_SITE_rs2-LOGTYPE_DATE-TIME.00.zip

Script `a0_file_renaming.py` was developed to perform this workflow.

## 2 PPK Kinematic processing
Using kinematic processing (PPK), we corrected the rover (reachm2) data to get a precise track of measurements with respect to the base station (RS2). We used the free application EmlidStudio to perform this step following the online guide ([Emlid website, access on 20240507](https://blog.emlid.com/emlid-studio-ppk-in-a-few-steps/`)).

This process happens in 2 steps:
### 2.1 RINEX conversion
First, reachm2 UBX data are converted to RINEX. In EmlidStudio, we definie the receiver (reachm2+), and its height (default 1.72m above ground on the magnaprobe).

The input is:
- 5Hz raw GPS location UBX file from the rover (reachm2)

The output is:
- RINEX navigation *.24P* file,
- RINEX observation *.24O* file,
- SBAS correction data *.sbs* file.

The UBX to RINEX converted files are renamed accordign to SALVO-2024 nomenclature using 'rinex-5Hz' for the TYPE.

### 2.2 PPK postprocessing
The inputs are:
- 5Hz RINEX *.24O* observation file from a rover (reachm2):
- RINEX *.24P* navigation file from the rover (reachm2) from config file:
- RINEX *.24O* observation file from base (rs2)
- height of the base (rs2):

The height of the rover (reachm2_height) is already included in the RINEX observationf file.

EmlidStudio outputs two  *\*.pos*  files that are renamed according to the SALVO-2024 naming convention:
- PPK corrected position files: *\*.pos* to `salvo_SITE_LOCATION_emlid-position5Hz_DATE.a1.pos`
- PPK corrected event position files: *\*_events.pos* to `salvo_SITE_LOCATION_emlid-events_DATE.a1.pos`

Position files are reformatted into a comma-separated files with formatted headers.

The python script `a1a_ppk_preprocessing.py` extract automatically the required reachm2 UBX files, and RS2 RINEX files to a working directory.

The python script `a1b_ppk_postprocessing.py` reorganized the EmlidStudio file outptus:
- Rename UBX files converted to RINEX, and move them to the root directory, include the sampling frequency in the name.
- Rename the PPK corrected *.pos* file processed from the previously converted RINEX file

[//]: # (The python script `a1b_ppk_postprocessing.py` relocate the *\*.pos* files to the emlid working root folder, and renamed them according to SALVO nomenclature:)

[//]: # (- position:)

[//]: # (- event:)


## A Config File
The configuration file could contain:
- timezone: EMLID devices use GPST (UTC) time by default
  - `UTC`
