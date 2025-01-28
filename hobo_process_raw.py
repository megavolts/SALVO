from datetime import timedelta as td
from datetime import datetime as dt
import os
import matplotlib.pyplot as plt
from matplotlib import gridspec
import logging
import pint_pandas
import hobo_toolbox as hbt
from salvo import file

# loger
logger = logging.getLogger(__name__)

data_dir = '/mnt/data/UAF-data/raw/SALVO/'
hobo_subdir = '01-HOBO/'

input_dir = os.path.join(data_dir, hobo_subdir)

# Create output directory
output_dir = input_dir.replace('raw', 'working_a')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

filelists = file.list_folder_recursive(input_dir)  # list all files recursively
files = file.select_extension(filelists, 'csv')  # select csv files

# Look for hobo logger name of shape X_Y (like ICE_1, BEO_TRH), exception for ICE6:
sensor_fp_d = {}
for f in files:
    # exception for ICE6:
    if 'ICE6' in f:
        sensor_name = 'ICE6'
    else:
        sensor_name = '_'.join(f.split('/')[-1].split('_')[:2]).split('.csv')[0]
    if sensor_name not in sensor_fp_d:
        sensor_fp_d[sensor_name] = [f]
    else:
        sensor_fp_d[sensor_name].append(f)

hobo_data = {}
for sensor_name in sensor_fp_d:
    filepaths = sensor_fp_d[sensor_name]

    # Process raw data
    data_df = hbt.file.concatenate_files(filepaths)
    if 'TRH' in sensor_name:
        col_start = 1
        col_end = 5
    else:
        col_start = 1
        col_end = 4
    data_df = data_df.iloc[:, col_start:col_end]
    tz_offset = hbt.data.read_timezone(data_df)  # read timezone
    data_df = hbt.data.parse_header(data_df)  # Parsing column header
    data_df = hbt.data.parse_date(data_df)  # Parsing date

    # look for missing data point
    if any(data_df['Date Time'].diff() > td(seconds=60*60)):
        logger.warning(f"{sensor_name} has missing data")
        for ii in data_df[data_df['Date Time'].diff() > td(seconds=60*60)].index:
            print(data_df.iloc[ii-1:ii+2, :]['Date Time'])

    # export
    if sensor_name == 'ICE6':
        sensor_name = 'ICE_6'

    # Basic plot
    w_fig, h_fig = 11, 8
    nrows, ncols = 1, 1
    fig = plt.figure(figsize=[w_fig, h_fig])
    gs1 = gridspec.GridSpec(
        nrows, ncols, height_ratios=[1] * nrows, width_ratios=[1] * ncols
    )
    ax = [[fig.add_subplot(gs1[0, 0])]]

    AX_X, AX_Y = 0, 0

    ax[AX_X][AX_Y].set_title(sensor_name)
    ax[AX_X][AX_Y].set_xlabel("Date of year (day)")
    ax[AX_X][AX_Y].set_ylabel("Temperature (°C)")

    data = data_df.pint.quantify(level=-1)
    for col in data.columns:
        print(col)

        if 'Temp' in col:
            X = data['Date Time'].astype('datetime64[ns]')
            Y = data[col].astype(float)
            ax[AX_X][AX_Y].plot(X, Y, label=col.split('(')[-1].split(')')[0])
        elif 'RH' in col:
            X = data['Date Time'].astype('datetime64[ns]')
            Y = data[col].astype(float)
            ax_twin = ax[AX_X][AX_Y].twinx()  # instantiate a second Axes that shares the same x-axis
            ax_twin.plot(X, Y, label=col.split('(')[-1].split(')')[0], color='orange')
            ax_twin.set_ylabel("Relative humidity (%)")
            ax_twin.legend(loc="lower right")
        else:
            pass

    ax[AX_X][AX_Y].legend(loc="lower left")

    # ax[AX_X][AX_Y].xaxis.set_label_position("top")
    # ax[AX_X][AX_Y].xaxis.set_ticks_position("top")
    # ax[AX_X][AX_Y].yaxis.set_label_position("left")
    # ax[AX_X][AX_Y].yaxis.set_ticks_position("left")
    # ax[AX_X][AX_Y].yaxis.set_ticks_position("left")
    # ax[AX_X][AX_Y].spines["top"].set_visible(False)
    # ax[AX_X][AX_Y].spines["right"].set_visible(False)

    ax[AX_X][AX_Y].set_xlim([dt(year=2024, month=4, day=22, hour=12), dt(year=2024, month=6, day=19, hour=12)])
    ax[AX_X][AX_Y].set_ylim([-20, 5])
    ax_twin.set_ylim([0, 100])
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # Export figure
    plt.savefig(os.path.join(output_dir, f'{sensor_name}.pdf'))
    plt.show()

    # Export data
    data_df.to_csv(os.path.join(output_dir, f'{sensor_name}.01-20241121.csv'), index=False)


