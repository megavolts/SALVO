"""
    File containing helpers
"""
import datetime as dt
import os
import logging

logger = logging.getLogger(__name__)


def get_site(directory):
    """
    Return the site name based on the directory tree

    :param directory: string
        Input directory tree
    :return site: string
        Site name
    """
    site = None
    date_pattern = "%Y%m%d"
    for subdir in directory.split("/"):
        try:
            dt.datetime.strptime(subdir.split("-")[0], date_pattern)
        except ValueError:
            pass
        else:
            site = subdir.split("-")[1]
    return site


def get_date(directory):
    """
    Return the date name based on the directory tree

    :param directory: string
        Input directory tree
    :return site: string
        Date in format YYYYMMDD
    """
    date = None
    date_pattern = "%Y%m%d"
    for subdir in directory.split("/"):
        try:
            date = dt.datetime.strptime(subdir.split("-")[0], date_pattern)
        except ValueError:
            pass
        else:
            date = date.strftime("%Y%m%d")
    return date


def output_filename(in_fn, level="a"):
    """
    Generate output filepath base on the input raw filepath. If the file directory does not exist it is created.
    :param in_fp: str
    :param level: str
    :return: str
        A string containing the filename in which the output data is writtent
    """
    base_dir = os.path.dirname(in_fn)
    out_dir = base_dir.replace("/raw/", "/working_" + level + "/")

    # Input filename
    input_fn = os.path.basename(in_fn)
    if ".00." in input_fn:
        output_fn = input_fn.replace(".00.", ".a1.")
    elif ".a" in input_fn:
        _increment_number = int(input_fn.split(".")[-2][1:])
        _next_number = _increment_number + 1
        if _next_number == 0:
            # According to ARM guideline a0 is only for raw data exported to NetCDF
            # https://www.arm.gov/guidance/datause/formatting-and-file-naming-protocols
            _next_number = 1
        output_fn = input_fn.replace(
            f"a{_increment_number:.0f}", f"a{_next_number:.0f}"
        )
    out_file = os.path.join(out_dir, output_fn)
    out_dir = ("/").join(out_file.split("/")[:-1])
    if not os.path.exists(out_dir):
        logger.info(str("Creating output file directory: " + out_dir))
        os.makedirs(out_dir)
    return out_file
