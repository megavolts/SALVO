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
- TYPE is `rinex1Hz`, `ubx`, `raw`
- DATE in format `YYYYMMDD`
- TIME in format `HHMMSS`
- EXT is the original file extension

Third, we recreate a zip archive following the SALVO-2024 naming convention, prepending *.00* to the *.zip* file extension to denote the raw data before. Upon successful archiving, the temporary directory is deleted.
- reachm2: salvo_SITE_reachm2-LOGTYPE_DATE-TIME.00.zip
- RS2: salvo_SITE_rs2-LOGTYPE_DATE-TIME.00.zip

## 2 PPK Kinematic processing
Using kinematic processing (PPK), we corrected the rover (reachm2) data to get a precise track of measurements with respect to the base station (RS2). We used the free application EmlidStudio to perform this step following the online guide ([Emlid website, access on 20240507](https://blog.emlid.com/emlid-studio-ppk-in-a-few-steps/`)).

PPK processing could be performed either from the raw location UBX file (preferred) or from the RINEX export from the rover.

In both case, we use the following configurations in EmlidStudio:
- filtering: combined
- time export: UTC

### 2.1 PPK postprocessign with UBX
The inputs are:
- UBX *.ubx* raw GPS location file from a rover (reachm2)
- RINEX *.24O* observation file from base (rs2)
- height of the base (rs2)
- height of the rover (reachm2)

The outputs are:
- RINEX navigation *.24P* file
- RINEX observation *.24O* file,
- SBAS correction data *.sbs* file.
- PPK corrected position files: *\*.pos*
- PPK corrected event position files: *\*_events.pos*

### 2.2 PPK postprocessing with RINEX
The inputs are:
- RINEX *.24O* observation file from a rover (reachm2)
- RINEX *.24P* navigation file from the rover (reachm2) from config file
- RINEX *.24O* observation file from base (rs2)
- height of the base (rs2)
- height of the rover (reachm2)

The outputs are:
- PPK corrected position files: *\*.pos*
- PPK corrected event position files: *\*_events.pos*

### 2.3 Renaming
EmlidStudio outputs two  *\*.pos*  files that are renamed according to the SALVO-2024 naming convention:
- PPK corrected position files: *\*.pos* to `salvo_SITE_LOCATION_emlid-positionFFHz_DATE.a1.pos`
- PPK corrected event position files: *\*_events.pos* to `salvo_SITE_LOCATION_emlid-eventsFFHz_DATE.a1.pos`

If the PPK corrected were processed with the UBX file. The generated RINEX files are moved within the `rinex` subdirectory, and rename according to the SALVO-2024 naming convention, including sampling frequency.

### 2.4 Position file formatting
Position files are reformatted into a comma-separated files with formatted headers, and the UTM location are computed.

## 3. Scripts
The script `a0_file_renaming.py` was written to rename automatically the raw files according to the workflow describe under [File renaming](#1---file-renaming)

The python script `a1a_ppk_preprocessing.py` extract automatically the required reachm2 UBX files, and RS2 RINEX files to a working director.

The python script `a1b_ppk_postprocessing.py` reorganized the EmlidStudio file outputs:
- Rename UBX files converted to RINEX, and move them to the root directory, include the sampling frequency in the name.
- Rename the PPK corrected *.pos* file processed from the previously converted RINEX file
- Reformat *\*.pos* file, and compute UTM projection.
