from collections import defaultdict
from typing import Callable, List

import numpy as np
import pandas as pd

from .load import load_basic_transfer_networks, load_financial_transfer_networks
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


def get_league_avg_transfer_fee(
    league: str = "english_premier_league",
    network_load_fn: Callable = load_financial_transfer_networks,
    rankings: dict = None,
    start_year: int = 2000,
    end_year: int = 2020,
) -> pd.DataFrame:
    """
    Get the mean transfer amount both in and out per transfer. If rankings supplied,
    will calculate averages for top 4 and bottom 3 teams. Standard deviation
    values also supplied

    Inputs:
        league: filename of league
        network_load_fn: a function to load network objects
        rankings: optionally include rankings
        start_year: start year
        end_year: year end
    Outputs:
        df of mean and std for in and out transfers
    """
    df = pd.DataFrame()

    # get the financial transfer network
    ftn_dict = network_load_fn(start_year, end_year, league=league)

    # go through each year from start to end to find transfer info
    for year in range(start_year, end_year + 1):

        # get the FinancialTransferNetwork object for the year
        ftn_year = ftn_dict.get(year)

        # aggregate all transfers by team first
        ins_by_team = defaultdict(list, {club: [] for club in ftn_year.league_clubs})
        outs_by_team = defaultdict(list, {club: [] for club in ftn_year.league_clubs})

        for u, v, data in ftn_year.G.edges(data=True):

            # if the fee is 0, thats a loan so skip
            if not data[ftn_year.edge_key] > 0.0:
                continue

            if u in ftn_year.league_clubs:
                outs_by_team[u].append(data[ftn_year.edge_key])

            if v in ftn_year.league_clubs:
                ins_by_team[v].append(data[ftn_year.edge_key])

        # now get the average of each clubs transfers
        avg_ins_team = {
            c: 0 if not len(ts) else np.mean(ts) for c, ts in ins_by_team.items()
        }
        avg_outs_team = {
            c: 0 if not len(ts) else np.mean(ts) for c, ts in outs_by_team.items()
        }

        # if we have rankings, get the top 4 and bottom 3 averages
        if rankings is not None:
            top_4 = list(rankings[year])[:5]
            bottom_3 = list(rankings[year])[-3:]

            df.loc[year, "Top 4 out"] = np.mean([avg_outs_team[club] for club in top_4])
            df.loc[year, "Top 4 in"] = np.mean([avg_ins_team[club] for club in top_4])

            df.loc[year, "Bottom 3 out"] = np.mean(
                [avg_outs_team[club] for club in bottom_3]
            )
            df.loc[year, "Bottom 3 in"] = np.mean(
                [avg_ins_team[club] for club in bottom_3]
            )

        df.loc[year, "avg out"] = np.mean([v for k, v in avg_outs_team.items()])
        df.loc[year, "avg in"] = np.mean([v for k, v in avg_ins_team.items()])
        df.loc[year, "std out"] = np.std([v for k, v, in avg_outs_team.items()])
        df.loc[year, "std in"] = np.std([v for k, v in avg_ins_team.items()])

    return df


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


def get_league_fees(
    league: str = "english_premier_league",
    network_load_fn: Callable = load_financial_transfer_networks,
    start_year: int = 2000,
    end_year: int = 2020,
) -> pd.DataFrame:
    """
    Get the spending in and out of a league

    Args:
        league: filename of league
        network_load_fn: a function to load network objects
        start_year: start year
        end_year: year end

    Returns:
        df of in and out fees
    """
    df = pd.DataFrame()
    ftn_dict = network_load_fn(start_year, end_year, league=league)

    for year in range(start_year, end_year + 1):

        ftn_year = ftn_dict.get(year)

        # aggregate all transfers by team first
        ins_by_team = defaultdict(list, {club: [] for club in ftn_year.league_clubs})
        outs_by_team = defaultdict(list, {club: [] for club in ftn_year.league_clubs})

        for u, v, data in ftn_year.G.edges(data=True):

            # if the fee is 0, thats a loan so skip
            if not data[ftn_year.edge_key] > 0.0:
                continue

            if u in ftn_year.league_clubs:
                outs_by_team[u].append(data[ftn_year.edge_key])

            if v in ftn_year.league_clubs:
                ins_by_team[v].append(data[ftn_year.edge_key])

        for club in ftn_year.league_clubs:
            df.loc[year, f"{club} in fees"] = (
                0 if not len(ins_by_team[club]) else np.mean(ins_by_team[club])
            )
            df.loc[year, f"{club} out fees"] = (
                0 if not len(outs_by_team[club]) else np.mean(outs_by_team[club])
            )

    return df


def get_league_scalar_measures(
    nx_fns: List[Callable],
    league: str = "english_premier_league",
    network_load_fn: Callable = load_basic_transfer_networks,
    start_year: int = 2000,
    end_year: int = 2020,
) -> pd.DataFrame:
    """
    Apply a list of Networkx algorithms - ones that take a whole graph and
    output a scalar value - to a league.
    Args:
        nx_fns: list of Networkx functions (e.g. [nx.reciprocity])
        league: filename of league
        network_load_fn: a function to load network objects
        start_year: start year
        end_year: year end

    Returns:
        df of results
    """
    df = pd.DataFrame()
    tn_dict = network_load_fn(start_year, end_year, league=league)
    for year in range(start_year, end_year + 1):
        t = tn_dict.get(year)
        for nx_fn in nx_fns:
            df.loc[year, nx_fn.__name__] = nx_fn(t.G)
    return df


def get_league_avg_node_measure(
    nx_fn: Callable,
    league: str = "english_premier_league",
    network_load_fn: Callable = load_basic_transfer_networks,
    rankings: dict = None,
    start_year: int = 2000,
    end_year: int = 2020,
) -> pd.DataFrame:
    """
    Apply a Networkx algorithm - one that takes a whole graph and outputs a
    value per node - to a league.

    If rankings supplied, will
    calculate averages for top 4 and bottom 3 teams.
    Args:
        nx_fn: Networkx function (e.g. nx.closeness_centrality)
        league: filename of league
        network_load_fn: a function to load network objects
        rankings: optionally include rankings
        start_year: start year
        end_year: year end

    Returns:
        df of mean and std for each measure
    """
    df = pd.DataFrame()
    tn_dict = network_load_fn(start_year, end_year, league=league)
    for year in range(start_year, end_year + 1):
        t = tn_dict.get(year)
        results = nx_fn(t.G)
        if rankings is not None:
            top_4 = list(rankings[year])[:5]
            bottom_3 = list(rankings[year])[-3:]
            df.loc[year, "Top 4"] = np.mean([results[c] for c in top_4])
            df.loc[year, "Bottom 3"] = np.mean([results[c] for c in bottom_3])
        df.loc[year, "avg"] = np.mean([results[c] for c in t.league_clubs])
        df.loc[year, "std"] = np.std([results[c] for c in t.league_clubs])
    df.name = nx_fn.__name__
    return df
