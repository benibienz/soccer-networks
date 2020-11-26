from typing import Callable

import numpy as np
import pandas as pd

from .load import load_basic_transfer_networks
from .util import TransferNetwork


def highest_in_degree(transfer_nw: TransferNetwork) -> str:
    """Returns name of prem club with highest in-degree"""
    res, max_in_deg = None, 0
    for club in transfer_nw.league_clubs:
        in_deg = transfer_nw.G.in_degree(club)
        if in_deg > max_in_deg:
            res = club
            max_in_deg = in_deg
    return res


def get_league_avg_degrees(
    league: str = "english_premier_league",
    network_load_fn: Callable = load_basic_transfer_networks,
    rankings: dict = None,
    start_year: int = 2000,
    end_year: int = 2020,
) -> pd.DataFrame:
    """
    Get the mean in and out degrees of a league. If rankings supplied, will
    calculate averages for top 4 and bottom 3 teams.
    Args:
        league: filename of league
        network_load_fn: a function to load network objects
        rankings: optionally include rankings
        start_year: start year
        end_year: year end

    Returns:
        df of mean and std for in and out degrees
    """
    df = pd.DataFrame()
    tn_dict = network_load_fn(start_year, end_year, league=league)
    for year in range(start_year, end_year + 1):
        t = tn_dict.get(year)
        if rankings is not None:
            top_4 = list(rankings[year])[:5]
            bottom_3 = list(rankings[year])[-3:]
            df.loc[year, "Top 4 out"] = np.mean([t.G.out_degree(c) for c in top_4])
            df.loc[year, "Top 4 in"] = np.mean([t.G.in_degree(c) for c in top_4])
            df.loc[year, "Bottom 3 out"] = np.mean(
                [t.G.out_degree(c) for c in bottom_3]
            )
            df.loc[year, "Bottom 3 in"] = np.mean([t.G.in_degree(c) for c in bottom_3])
        df.loc[year, "avg out"] = np.mean([t.G.out_degree(c) for c in t.league_clubs])
        df.loc[year, "avg in"] = np.mean([t.G.in_degree(c) for c in t.league_clubs])
        df.loc[year, "std out"] = np.std([t.G.out_degree(c) for c in t.league_clubs])
        df.loc[year, "std in"] = np.std([t.G.in_degree(c) for c in t.league_clubs])
    return df


def get_league_degrees(
    league: str = "english_premier_league",
    network_load_fn: Callable = load_basic_transfer_networks,
    start_year: int = 2000,
    end_year: int = 2020,
) -> pd.DataFrame:
    """
    Get the in and out degrees of a league.
    Args:
        league: filename of league
        network_load_fn: a function to load network objects
        start_year: start year
        end_year: year end

    Returns:
        df of in and out degrees
    """
    df = pd.DataFrame()
    tn_dict = network_load_fn(start_year, end_year, league=league)
    for year in range(start_year, end_year + 1):
        t = tn_dict.get(year)
        for club in t.league_clubs:
            df.loc[year, f"{club} out-degree"] = t.G.out_degree(club)
            df.loc[year, f"{club} in-degree"] = t.G.in_degree(club)
    return df
