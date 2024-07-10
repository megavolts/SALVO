"""
File to compute euclidian distance
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)


def euclidian_distance(p1, p2):
    """
        Compute euclidian distance between points P1 and P2
        P1 and P2 must have the same dimension, or P1 or P2 should be a scalar
    :param p1: array_like, float
        Point P1(x1, x2, x3 ... xn)
    :param p2: array_like, float
        Point P2(x1, x2, x3 ... xn)
        P1 and

    :return d: float
        The calculated euclidian distance between P1 and P2
    """
    # make
    if isinstance(p1, (int, float)):
        p1 = [p1]
    p1 = np.array(p1)

    if isinstance(p2, (int, float)):
        p2 = [p2]
    p2 = np.array(p2)

    if p1.shape != p2.shape:
        if len(p1) == 1:
            p1 = p1 * len(p2)
        elif len(p2) == 1:
            p2 = p2 * len(p1)
        else:
            logger.error("P1 and P2 must be of same dimension")

    d = np.sqrt(np.sum((p1 - p2) ** 2))
    return d


def compute_distance(input_df, origin_pt=None):
    """
    Compute distance in between point (TrackDist), cumulative distance in between point (TrackDistCum) and distance from
    origin point (DistOrigin). The origin point is the first point of the dataframe, unless
    :param df: pd.DataFrame()
            Dataframe containing the raw data. Dataframe should contain columns X, Y and Z. The latter could be set
            to 0 if not needed.
    :param origin_pt: 1darray or None (default)
        If none, origin point is the first point in the dataframe
        Origin point should be either of format [x0, y0, z0] or [x0, y0]. In the latter case, z0 is set to zero (z0=0).
    :return:
    """
    data_df = input_df.copy().reset_index(drop=True)
    if origin_pt is None:
        origin_pt = np.array(
            [data_df.iloc[0, ii_col] for ii_col, _ in enumerate(input_df.columns)]
        )
    elif isinstance(origin_pt, (int, float)):
        origin_pt = np.array([origin_pt]) * len(data_df.columns)
    elif len(origin_pt) < len(data_df.columns):
        logger.warning("Setting extra dimension are filled with 0")
        origin_pt = np.array(origin_pt)
        origin_pt = np.concatenate(
            (origin_pt, np.zeros(len(data_df.columns) - len(origin_pt)))
        )
    else:
        logger.error("TODO: compute_distance not defined")

    col_h = list(data_df.columns)
    col_s = [col + "_s" for col in data_df.columns]

    data_df.loc[:, col_s] = data_df[col_h].shift().to_numpy()
    data_df.loc[0, col_s] = data_df.loc[0, col_h].to_numpy()

    # TODO: if previous point is missing, compute with the last known coordinate, aka filter nas row out
    data_df["TrackDist"] = data_df.apply(
        lambda x: euclidian_distance(x[col_h], x[col_s]), axis=1
    )
    data_df["TrackDistCum"] = data_df["TrackDist"].cumsum()
    data_df["DistOrigin"] = data_df.apply(
        lambda x: euclidian_distance(x[col_h], origin_pt), axis=1
    )
    data_df.drop(col_s, axis=1, inplace=True)
    return data_df[["TrackDist", "TrackDistCum", "DistOrigin"]]
