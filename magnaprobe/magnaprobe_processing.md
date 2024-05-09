# Magnaprobe Processing
Here we describe how we process magnaprobe data file for the SALVO-2024 field campaign

## 0 - Data download
Magnaprobe data is either download directly in the field at time of TAKING down the instrument, or upon return to the staging area

Raw data filename is renamed according to SALVO-2024 data convention. File extension is *\*.00.dat*

### 0.1 - Multiple transects in one file
We manually split the original raw file (*\*.00.dat*) into several files containing the raw data for each transect. In that case, filename for raw data for each transect is updated to *\*\*.00.dat*, with ** reflecting the transect name.

## 1 - Preprocessing and quality check
At first, raw data file is preprocessing. This operation include:
- Loading raw data in which row 2 contains the header
- Formatting column headers to lower case with capitalize first letter
- Removing junk raws (1, 3 and 4)
- Formatting timestamp to ISO8601 format. If timestamp is invalid, an artificial timestamp is generated starting at midnight local time, with 1 minute increment for consecutive points.
- Decimal degree coordinate are compute from the integer and minute coordinate field:
  -  Latitude = Latitude_a + Latitude_b / 60
  -  Longitude = Longitude_a + Longitude_b / 60
- Projection of decimal degree on a metric coordinate system. We transform from WGS84 to Alaska local ESPG 3338
- Conversion of snow depth values given in cm to m

Second, we compute several distance metric:
- `TrackDist`: Euclidian distance between two consecutive points
- `DistOrigin`: Euclidian distance between a point, and the first point of the file
- `TrackDistCum`: Cumulative addition of `TrackDist`

Third, we perform a quality check with the following flag stored in the `QC_flag` column:
- `NaN`: no quality check performed
- 0: an initial quality check has been performed to remove calibration values, split the file
- 1: good point
- 4: bad point,
- 7: snow depth is negative
- 8: entries may be duplicate as the distance between two consecutive points is small (less than 1/3 of the median TrackDist) or not be part of the transect as the distance between them is large (3 times the median TrackDist)
- 9: entries may be duplicate as the time between two consecutive points is small (less than 1 seconds

Flag, 7, 8 and 9 return a warning, and file needs to be corrected manually

At the same time, we mark potential calibration point in the column `CalPoint` with:
- `None`: not a calibration point,
- `L`: lower calibration point, as snow depth is less than lower calibration bound (default value 0.02 m) ,
- `U`: upper calibration point, as snow depth is less than lower calibration bound (default value 1.18 m)

The preprocessed and quality check (*pqc*) data , is an a-grade data product. The filename is conserved, and the file extension is updated to *.aX.dat* with *X* the smaller integer larger than 0, often *.a1.dat*

This workflow is integrated within the `maganprobe/a1_preprocessing_qc.py` script

## 2 Manual sanitizing
During the next step, we performed a manual sanitation of the file, in which the file is open in a spreadsheet editor.

We checked each entry flagged previously during the data check, and take the following steps:
- Remove duplicate entries
- Remove entries marked as problematic during the transect by the use of a pair of upper and lower calibration marks
- Remove calibration points at the start and the end of the file

The sanitized file is an a-grade product, saved as a comma-separated-file. The filename is conserved. The file extension is updated from *.aX.dat* to *.a(X+1).csv*

Each removed entry is recorded in a separated *yaml* file, stored in the same directory as the pqc-file. The filename is **TO BE DETERMINED, for the moment we keep the original *\** file name, with the extension *.00.yaml**. The removed entry are stored in an array under `deleted record`, with the following entry header row `- [Record Number, Counter, Comment]`

The config file can then be used when the data is reprocessed to skip the manual sanitizing operation.

## 3 Formatting
The workflow to format magnaprobe data for the line, longline and library site is implemented in python in the following script `magnaprobe/a1a_formatting-.py`.

### 3.1 Formatting *line* transect
This operation is specific to format the data output of the 200m transect line. As we are probing the line every meter from 0 to 200m, the file should contain 201 entries. The output file will contain an additional `LineLocation ` columns in which the location of the point along the line is set to the exact integer distance: 0, 1, 2, ..., 200.

If the file contains exactly 201 entries, then the `LineLocation` columns is automatically filled with the set distance.

If the file contains strictly less than 201 entries, then the corrector has to fill the missing row(s) to the best of his knowledge, based on difference in `TrackDist`. When possible, we used the additional geospatial information `TrackDist_emlid` provided by the emlid reachm2 portable device. Each added entry is recorded in the config *yaml* file, stored in the same directory as the pqc-file. The filename is **TO BE DETERMINED, for the moment we keep the original *\** file name, with the extension *.00.yaml**. The added entry are stored in an array under `added record`, with the following entry header row `- [Record Number, Counter, LineLocation, Comment]`.

If the file contains strictly more than 201 entries, then the corrector has to delete the additional row(s) to the best of his knowledge, based on difference in `TrackDist_emlid` . When possible, we used additional geospatial information provided by the emlid reachm2 portable device. Each removed entry is recorded in a separated *yaml* file, stored in the same directory as the pqc-file. The filename is **TO BE DETERMINED, for the moment we keep the original *\** file name, with the extension *.00.yaml**. The removed entry are stored in an array under `deleted location`, with the following entry header row `- [Record Number, Counter, Comment]`

The config file can then be used when the data is reprocessed to automate the addition or deletion of row(s).

### 3.2 Formatting *longline* transect

### 3.3 Formatting *library* site

## 4 Additional EMLID geospatial information
The workflow to integrate EMLID position in the magnaprobe data is implemented in python in the following script `magnaprobe/a1b_emlid_integration.py`.

The integration of geospatial information from the Emlid rover with the MagnaProbe data generate a b-grade data product. The filename extension will be chagne to *\*.bX*

As of April 2024, the time offset ($\Deltat$) between GPST and UTC is about 18 seconds. The GEODEL MagnaProbe datalogger was set to UTC-8 time with an estimated maximum positive lag of 1 second on April 15. **CHECK THE LAG WHEN RETURNING TO UTQ IN MAY**






## A Config File
The configuration file could contain:
- timezone: during SALVO, MagnaProbe datalogger time was set to AKDT (UTC-8)
  - `UTC-8`
- site: generic site location
  - `arm`: site with heterogeneous tundra subtract at the Barrow Environmental Observatory
  - `beo`: site with homogeneous tundra subtract at the Barrow Environmental Observatory
  - `ice`: site with sea ice subtract at Elson Lagoon
- location:
  - `line`; 200m E-W transect line
  - `longline`: ~1500 m E-W transect line
  - `library`: single point site
