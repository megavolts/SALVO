"""
File naming for emlid
"""
import datetime as dt

INSTRUMENT_DICT = {"reachm2": "reachm2", "UAF_SALVO_R": "rs2", "REACH-BASE-": "rs2"}
DATE_PATTERNS = {12: "%Y%m%d%H%M", 14: "%Y%m%d%H%M%S"}  # potential date pattern


def log_type(item):
    """
    Return the emlid log type according to the file name
    :param item: string
        Input filename
    :return log_type: string
        Type of emlid log (rinex, ubx, raw)
    """
    log_types = {
        "rinex": "rinex",
        "ubx": "ubx",
        "raw": "raw",
        "llh": "llh",
    }  # potential log type for the emlid data
    try:
        l_type = [val for key, val in log_types.items() if key in item.lower()][
            0
        ]  # define log type base on filename
    except IndexError:
        l_type = None
    return l_type


def create_emlid_name(input_name, site, location):
    """
    Create emlid (sub)directory name according to SALVO-2024 nomenclature
    :param input_name:
        input on which emlid name is to be created
    :param site: string
        Either: 'arm', 'beo', 'ice
    :param location: string, array of string
        Either 'line', 'longline', 'library'. Could be appended with a dash (-)
    :return emlid_name: string
        emlid (sub)directory name
    """
    output_name_l = ["salvo", site.lower(), location.lower()]

    # define log type
    instrument = [val for key, val in INSTRUMENT_DICT.items() if key in input_name][0]
    l_type = log_type(input_name)
    output_name_l.append("-".join(filter(None, [instrument, l_type])))

    # loop through filename substring for a date
    for substring in input_name.split("_"):
        substring = substring.split(".")[0]
        # check date pattern base on substring length
        try:
            timestamp = dt.datetime.strptime(substring, DATE_PATTERNS[len(substring)])
        except KeyError:
            timestamp = None
        else:
            timestamp = timestamp.strftime("%Y%m%d-%H%M%S")
            break
    output_name_l.append(timestamp)
    output_name = "_".join(filter(None, output_name_l))
    return output_name
