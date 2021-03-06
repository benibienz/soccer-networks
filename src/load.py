import math
import os
import re
from collections import defaultdict

import networkx as nx
import pandas as pd

from .util import (BasicTransfer, ClubSeasonInfo, FinancialTransferNetwork,
                   TransferNetwork, FullTransferNetwork, AggregateFullTransferNetwork)

# keep this table growing for overlapping names so that we can simplify it
club_name_mappings = {
    "leicester": "leicester city",
    "sheff": "sheffield",
    "west brom": "west bromwich albion",
    "wolves": "wolverhampton wanderers",
    "brighton": "brighton & hove albion",
    "norwich": "norwich city",
    "tottenham hotspurs": "tottenham",
    "tottenham hotspur": "tottenham",
    "spurs": "tottenham",
    "west ham": "west ham united",
    "wigan": "wigan athletic"
}

# exclusions for club names
name_exclusions = ["afc ", " afc", " fc", "fc ", "club ", " club"]

# re for extracting under age from name
u_age_re = re.compile(r"[uU][1-9]+")


# function to clean name
def name_cleaner(name: str) -> str:
    name = name.lower().strip()

    # Manchester
    name = name.replace("man ", "manchester ")

    # merge youth teams
    for substr in u_age_re.findall(name):
        name = name.replace(substr, "")

    # merge B team
    if name.endswith(" b"):
        name = name[:-2]

    # standardize "united" teams
    for substr in ["united", "utd.", " utd"]:
        if substr in name:
            name = name.replace(substr, "") + " united"

    # now look through the others
    for substr in name_exclusions:
        if substr in name:
            name = name.replace(substr, "")

    name = name.replace("  ", " ").strip()
    # finally, if the team has a mapping, look for the mapping
    if name in club_name_mappings:
        name = club_name_mappings[name]

    return name

#------------------ Load networks from pandas dataframe -----------------------#

def basic_transfer_network_from_df(df: pd.DataFrame) -> TransferNetwork:
    """
    Create a basic transfer network from a pandas dataframe. Directed
    edges are player from club x to club y.

    Inputs:
        table:  pandas dataframe with columns 'club_name', 'club_involved_name', 'transfer_movement'
    Outputs:
        nx.DiGraph
    """

    # get all the raw club names
    clubs = set(
        list(df["club_name"].unique()) + list(df["club_involved_name"].unique())
    )

    # create a mapping from the club names in the table to our standardized club names
    table_to_standard = {club: name_cleaner(club) for club in clubs}

    league_clubs = [name_cleaner(club) for club in df["club_name"].unique()]

    G = nx.MultiDiGraph()

    for idx, row in df.iterrows():

        # get the standardized names
        club_name = table_to_standard[row["club_name"]]
        club_involved = table_to_standard[row["club_involved_name"]]
        if club_involved in league_clubs:
            continue  # don't double count edges between league teams

        if row["transfer_movement"] == "in":
            G.add_edge(club_involved, club_name)
        elif row["transfer_movement"] == "out":
            G.add_edge(club_name, club_involved)

    return TransferNetwork(G, league_clubs)


def financial_transfer_network_from_df(
    df: pd.DataFrame, currency="dollars", denomination=1000000
) -> FinancialTransferNetwork:
    """
    Create a financial transfer network from a pandas dataframe. Directed
    edges are fees paid by one team u to another v
    Inputs:
        table:  pandas dataframe with columns 'club_name', 'club_involved_name', 'transfer_movement', 'fee_cleaned'
    Outputs:
        FinancialTransferNetwork
    """

    # set the key used for indexing into currency
    edge_key = "fee"

    # get all the raw club names
    clubs = set(
        list(df["club_name"].unique()) + list(df["club_involved_name"].unique())
    )

    # create a mapping from the club names in the table to our standardized club names
    table_to_standard = {club: name_cleaner(club) for club in clubs}

    G = nx.MultiDiGraph()

    league_clubs = set()

    for idx, row in df.iterrows():

        # get the standardized names
        club_name = table_to_standard[row["club_name"]]
        club_involved = table_to_standard[row["club_involved_name"]]

        # get the price
        amount = row["fee_cleaned"]

        # if its not a number, make it 0
        if math.isnan(amount):
            amount  = 0.0

        # NOTE: if both teams involved are in the prem, then we get a duplicate edge
        # so we should check to see if a transfer from one to another with that price exists
        # since its really unlikely two transfers of the same amount exists between the same two teams
        if row["transfer_movement"] == "out":

            # check if the edge exists and has the same fee
            if G.has_edge(club_involved, club_name) and any(
                [x["fee"] == amount for _, x in G[club_involved][club_name].items()]
            ):
                continue

            G.add_edge(club_involved, club_name, fee=amount)

        elif row["transfer_movement"] == "in" and not G.has_edge(
            club_name, club_involved
        ):

            # check if the edge exists and has the same fee
            if G.has_edge(club_name, club_involved) and any(
                [x["fee"] == amount for _, x in G[club_name][club_involved].items()]
            ):
                continue

            G.add_edge(club_name, club_involved, fee=amount)

        league_clubs.add(club_name)

    return FinancialTransferNetwork(G, league_clubs, currency, denomination, edge_key)


def basic_financial_transfer_network_from_df(
    df: pd.DataFrame, currency="dollars", denomination=1000000
) -> FinancialTransferNetwork:
    """
    Create a financial transfer network from a pandas dataframe. Directed
    edges are fees paid by one team u to another v. Note this is different because 
    it is only a DiGraph instead of a MultiDiGraph
    
    Inputs:
        table:  pandas dataframe with columns 'club_name', 'club_involved_name', 'transfer_movement', 'fee_cleaned'
    Outputs:
        FinancialTransferNetwork
    """
    
    # first just load the graph from financial transfer network
    ftn = financial_transfer_network_from_df(df, currency=currency, denomination=denomination)
    
    # create a new graph that is a digraph instead of multidigraph
    g = nx.DiGraph()

    # now merge the the edges
    for u, v, data in ftn.G.edges(data=True):
        
        # see if u v in G
        if g.has_edge(u, v): 
            
            # update the value
            g[u][v]['fee'] += data['fee']
            continue
            
        # otherwise create the edge
        g.add_edge(u, v, fee=data['fee'])
        
    return FinancialTransferNetwork(g, ftn.league_clubs, currency, denomination, 'fee')

def load_full_network_from_df(
    df: pd.DataFrame, 
    currency: str = 'dollars', 
    denomination: float = 1000000
) -> FullTransferNetwork:
    '''
    Create a full transfer network with player involved, fee, year, window
    
    Inputs:
        table:  pandas dataframe with columns 
        'club_name', 'club_involved_name', 'transfer_movement', 'fee_cleaned', 'transfer_period', 'year', 'player_name'
    Outputs:
        FinancialTransferNetwork
    '''
    # set the keys used for indexing into edge properties
    fee_key = "fee"
    year_key = "year"
    window_key = "transfer_period"
    player_key = "player"

    # get all the raw club names
    clubs = set(
        list(df["club_name"].unique()) + list(df["club_involved_name"].unique())
    )

    # create a mapping from the club names in the table to our standardized club names
    table_to_standard = {club: name_cleaner(club) for club in clubs}

    G = nx.MultiDiGraph()

    league_clubs = set()

    for idx, row in df.iterrows():

        # get the standardized names
        club_name = table_to_standard[row["club_name"]]
        club_involved = table_to_standard[row["club_involved_name"]]

        # get the price
        amount = row["fee_cleaned"]
        
        # get the player name
        player = row["player_name"].lower()
        
        # get the transfer year and period
        year = int(row["year"])
        window = row["transfer_period"].lower()

        # if its not a number, make it 0
        if math.isnan(amount):
            amount  = 0.0

        # NOTE: if both teams involved are in the prem, then we get a duplicate edge
        # so we should check to see if a transfer from one to another with that player exsits
        if row["transfer_movement"] == "in":

            # check if the edge exists and has the same fee
            if G.has_edge(club_involved, club_name) and any(
                [x[player_key] == player for _, x in G[club_involved][club_name].items()]
            ):
                continue

            G.add_edge(club_involved, club_name, fee=amount, year=year, transfer_period=window, player=player)

        elif row["transfer_movement"] == "out":

            # check if the edge exists and has the same player
            if G.has_edge(club_name, club_involved) and any(
                [x[player_key] == player for _, x in G[club_name][club_involved].items()]
            ):
                continue

            G.add_edge(club_name, club_involved, fee=amount, year=year, transfer_period=window, player=player)

        league_clubs.add(club_name)

    return FullTransferNetwork(G, league_clubs, currency, denomination, player_key, fee_key, year_key, window_key)

    

#----------------------------- Load a league's network over time ------------------------------#

def load_basic_transfer_networks(
    start_year=2000, end_year=2020, league="english_premier_league"
) -> dict:
    """Loads premier league TransferNetwork objects for given year range"""
    basic_transfer_networks = {}
    for year in range(start_year, end_year + 1):
        df = pd.read_csv(f"data/{year}/{league}.csv")
        basic_transfer_networks[year] = basic_transfer_network_from_df(df)
    return basic_transfer_networks


def load_financial_transfer_networks(start_year=2000, end_year=2020, league='english_premier_league') -> dict:
    """Loads premier league TransferNetwork objects for given year range"""
    financial_transfer_networks = {}
    for year in range(start_year, end_year + 1):
        df = pd.read_csv(f"data/{year}/{league}.csv")
        financial_transfer_networks[year] = financial_transfer_network_from_df(
            df, "pounds"
        )
    return financial_transfer_networks


def load_basic_financial_transfer_networks(start_year=2000, end_year=2020, league='english_premier_league') -> dict:
    """Loads premier league TransferNetwork objects for given year range"""
    financial_transfer_networks = {}
    for year in range(start_year, end_year + 1):
        df = pd.read_csv(f"data/{year}/{league}.csv")
        financial_transfer_networks[year] = basic_financial_transfer_network_from_df(
            df, "pounds"
        )
    return financial_transfer_networks

def load_full_aggregate_network(
    start_year: int = 2000, 
    end_year: int = 2010, 
    league: str = "english_premier_league"
) -> AggregateFullTransferNetwork:
    '''
    Create an aggregate Full Transfer Network from start year to end year. The graph will contain 
    attributes such as players, teams, fees, years, and transfer windows
    
    Inputs:
        start_year:  (int) the start year to look at for transfers. Lowest value 1888
        end_year:    (int) the end year to look at for transfers. Highest value is 2019
        league:      (str) the league to load
    Outputs:
        AggregateFullTransferNetwork
    '''
    
    # create the graph to use
    G = nx.MultiDiGraph()
    
    # keep track of all clubs
    clubs = []
    
    # keep track of the keys
    player_key = None
    fee_key = None
    year_key = None
    window_key = None
    denomination = None
    
    # go through all years and load the networks
    for year in range(start_year, end_year + 1):
        
        # we have to make the dataframe first
        df = pd.read_csv(f"data/{year}/{league}.csv")
        
        year_ftn = load_full_network_from_df(df, "pounds")
        
        # set the keys
        if year == start_year:
            player_key = year_ftn.player_key
            fee_key = year_ftn.fee_key
            year_key = year_ftn.year_key
            window_key = year_ftn.window_key
            denomination = year_ftn.denomination
        
        # get all clubs
        clubs += year_ftn.league_clubs
        
        # combine the graphs
        for u, v, data in year_ftn.G.edges(data=True):
            G.add_edge(u, v, player=data[player_key], fee=data[fee_key], year=data[year_key], transfer_window=data[window_key])
        
    # setify the clubs
    clubs = list(set(clubs))
    
    # now create the AggregateFullTransferNetwork
    return AggregateFullTransferNetwork(G, clubs, "pounds", denomination, player_key, fee_key, year_key, window_key, start_year, end_year)

#--------------------------- Extra load functions ----------------------------#

def season_rankings_prem_league(start_year=2000, end_year=2016) -> dict:
    """
    Load in the premier league final season rankings from the data source.
    NOTE: we have data from 1888/1889 to 2019/2020 so we can't go outside of this range

    Inputs:
        start_year: (int) the first year to get rankings for (this is the Fall year)
        end_year:   (int) the last year to get rankings for (this is the Fall year)
    Outputs:
        dict  keyed by year with keys in each year of the team and their final rankings. Ex:
            {
                2019: {
                    Liverpool: 1, ...
                }
            }
    """
    # the current file dir
    full_path = os.path.abspath("")

    # get up until the project dir
    path_split = full_path.split(os.path.sep)

    # join until 'soccer-networks' and add 'data' 'PremierLeagueSeasonRankings' 'results.csv'
    project_dir = path_split[: path_split.index("soccer-networks") + 1]
    rankings_file = os.path.join(
        os.path.sep, *project_dir, "data", "PremierLeagueSeasonRankings", "result.csv"
    )

    # load it in
    rankings_df = pd.read_csv(rankings_file)

    # create our rankings dictionary
    rankings_dict = defaultdict(dict)

    # go through each row and create our dictionary
    for idx, row in rankings_df.iterrows():

        # get the first year from the year column
        year = int(row["year"].split("/")[0])

        if year < start_year or year > end_year:
            continue

        # get the team and the rankings directly from the row
        team = name_cleaner(row["Team"])
        rank = row["Pos"]

        rankings_dict[year][team] = rank

    return dict(rankings_dict)


def prem_season_transfer_summary(year: int) -> list:
    """
    Get a season summary of the season

    NOTE: latest year available is 2019, earliest is 1992

    Inputs:
        year: (int) the fall of the season interested
    Outputs:
        (list) ClubSeasonInfo objects for every premier league team in that season
    """
    if year > 2016 or year < 1992:
        raise Exception(
            f"Year out of range. Year {year} not in range 1992-2016 (inclusive)"
        )

    # get the season rankngs
    ranks = season_rankings_prem_league(start_year=year, end_year=year)

    # get clean name mappings to match the financial graph
    name_map = {club: name_cleaner(club) for club in ranks[year]}

    # get the financial transfer graph for the season
    ftn = load_financial_transfer_networks(start_year=year, end_year=year, league='english_premier_league')

    key = ftn[year].edge_key

    # keep track of all our club seasons
    csi = []

    # go through each club
    for club_dirty in ranks[year]:

        # get the clean club name
        club_name = name_map[club_dirty]

        # keep a list of basic transfers
        transfers = []

        # go through all edges and got those that have club name in them
        # NOTE: not the fastest way, but its fast enough

        # for the financial network, edges (u, v) is the flow of money from u to v
        for u, v, data in ftn[year].G.edges(data=True):

            direction = ""
            fee = ""
            club_involved = ""

            # money flows from club TO other team, player comes in, direction is then 'in'
            if u == club_name:
                direction = "in"
                fee = data[key]
                club_involved = v

            # money flows from other club TO this club, player goes out, direction is 'out'
            elif v == club_name:
                direction = "out"
                fee = data[key]
                club_involved = u

            else:
                continue

            # add this to transfers
            transfers.append(BasicTransfer(direction, club_involved, fee))

        # make a ClubSeasonInfo to hold all this
        csi.append(
            ClubSeasonInfo(
                club_name,
                ranks[year][club_dirty],
                transfers,
                ftn[year].currency,
                ftn[year].denomination,
            )
        )

    return csi
